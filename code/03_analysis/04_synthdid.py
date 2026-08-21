# -*- coding: utf-8 -*-
"""
Synthetic DiD (Arkhangelsky et al. 2021) for mechanism outcomes.

Implements the regularized SDiD unit-weight estimator (Algorithm 1).
  zeta = (T1 * N0)^{1/4} * sigma_hat
  Unit weights via augmented NNLS:
    [Y_ctrl_pre.T; sqrt(N0)*zeta * I_N0] @ omega ≈ [y_trt_pre; 0]
    then normalize to sum = 1
  Time weights: equal (1/T0) — valid for T0=T1=3.
  ATT = (y_T_post - omega.y_C_post_avg) - (1/T0) Σ_t (y_T_t - omega.y_C_t)

Inference: placebo permutation (200 reps, treated units drawn from controls).

Control pool: WFP floor >= 40, subsampled to N_MAX_CTRL for tractability.

Outputs:
  results/mechanism_synthdid.csv
"""

import sys
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
warnings.filterwarnings("ignore")

ROOT    = Path(__file__).resolve().parents[2]
PROC    = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

WFP_FLOOR  = 40.0
H_ORDER    = [-3, -2, -1, 0, 1, 2]
T0         = 3        # pre-periods: h = -3, -2, -1
T1         = 3        # post-periods: h = 0, +1, +2
N_MAX_CTRL = 500      # control subsample for tractability
N_PLACEBO  = 200
RNG_SEED   = 2025

OUTCOMES = {
    "med_gross_rent":     "Median gross rent ($)",
    "log_home_value":     "Log home value",
    "med_age_diffcounty": "Median age of diff-county in-migrants (yr)",
    "inmov_poverty_rate": "Poverty rate of in-movers (pp)",
}
SCALES = {
    "med_gross_rent":     1.0,
    "log_home_value":     1.0,
    "med_age_diffcounty": 1.0,
    "inmov_poverty_rate": 100.0,
}


def load_data() -> tuple[pd.DataFrame, set]:
    mech = pd.read_parquet(PROC / "mechanism_vars_panel.parquet")
    fire = pd.read_parquet(
        PROC / "fire_treatment_tracts.parquet",
        columns=["GISJOIN", "treated", "never_treated"],
    )
    covs = pd.read_parquet(
        PROC / "matching_covariates.parquet", columns=["GISJOIN", "wfp_mean_pct"]
    )
    wfp_tracts = set(covs.loc[covs["wfp_mean_pct"] >= WFP_FLOOR, "GISJOIN"].values)
    df = mech.merge(fire, left_on="NHGISCODE", right_on="GISJOIN", how="left")
    df = df[(df["treated"] == 1) | (df["never_treated"] == 1)].copy()
    df["h"] = df["acs_year"].map(dict(zip([2010, 2012, 2014, 2022, 2023, 2024], H_ORDER)))
    return df, wfp_tracts


def build_matrices(df: pd.DataFrame, outcome: str, wfp_tracts: set,
                   rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray] | None:
    """Balanced (Y_ctrl [N0 x T], Y_trt [N1 x T]). Controls subsampled to N_MAX_CTRL."""
    mask = (df["treated"] == 1) | (
        (df["never_treated"] == 1) & df["NHGISCODE"].isin(wfp_tracts)
    )
    sub = df[mask].copy()
    counts = sub.groupby("NHGISCODE")[outcome].count()
    balanced = set(counts[counts == 6].index)
    sub = sub[sub["NHGISCODE"].isin(balanced)].copy()

    wide = (
        sub[["NHGISCODE", "h", "treated", outcome]]
        .pivot(index="NHGISCODE", columns="h", values=outcome)
        .reindex(columns=H_ORDER)
    )
    flag = sub[sub["h"] == 0].set_index("NHGISCODE")["treated"]
    wide = wide.join(flag.rename("_treated"))

    ctrl_tracts = wide.index[wide["_treated"] == 0].tolist()
    trt_tracts  = wide.index[wide["_treated"] == 1].tolist()
    if len(ctrl_tracts) < 10 or len(trt_tracts) == 0:
        return None

    if len(ctrl_tracts) > N_MAX_CTRL:
        ctrl_tracts = rng.choice(ctrl_tracts, size=N_MAX_CTRL, replace=False).tolist()

    Y_ctrl = wide.loc[ctrl_tracts, H_ORDER].values.astype(float)
    Y_trt  = wide.loc[trt_tracts,  H_ORDER].values.astype(float)
    return Y_ctrl, Y_trt


def _zeta(Y_ctrl: np.ndarray) -> float:
    """Regularisation parameter: (T1*N0)^{1/4} * sigma_hat.
    sigma_hat = mean over controls of SD of pre-period first differences.
    Matches Algorithm 1 of Arkhangelsky et al. (2021)."""
    N0 = Y_ctrl.shape[0]
    diffs = np.diff(Y_ctrl[:, :T0], axis=1)   # N0 x (T0-1) first differences
    sigma_hat = np.mean(np.std(diffs, axis=1, ddof=1))
    return float((T1 * N0) ** 0.25 * sigma_hat)


def unit_weights(Y_ctrl: np.ndarray, y_trt_pre: np.ndarray) -> np.ndarray:
    """Regularised unit weights via augmented NNLS (Arkhangelsky et al. Algorithm 1)."""
    N0  = Y_ctrl.shape[0]
    zeta = _zeta(Y_ctrl)
    A    = Y_ctrl[:, :T0].T          # T0 x N0
    b    = y_trt_pre                  # T0
    # Augmented system includes ridge penalty: ||omega||^2 penalised by N0*zeta^2
    A_aug = np.vstack([A, np.sqrt(N0) * zeta * np.eye(N0)])   # (T0+N0) x N0
    b_aug = np.concatenate([b, np.zeros(N0)])
    omega, _ = nnls(A_aug, b_aug)
    s = omega.sum()
    return omega / s if s > 0 else np.ones(N0) / N0


def sdid_att(Y_ctrl: np.ndarray, Y_trt: np.ndarray) -> float:
    """SDiD ATT with equal time weights (valid for T0 = T1 = 3)."""
    y_trt_pre  = Y_trt[:, :T0].mean(axis=0)   # T0 treated pre-mean per period
    y_trt_post = Y_trt[:, T0:].mean()          # scalar treated post-mean

    omega = unit_weights(Y_ctrl, y_trt_pre)

    y_c_wtd_pre  = omega @ Y_ctrl[:, :T0]   # T0 weighted control pre-means
    y_c_wtd_post = (omega @ Y_ctrl[:, T0:]).mean()  # scalar weighted control post-mean

    # ATT with equal time weights: DiD in the unit-weight sense
    # (1/T0) * Σ_t(y_T_t - omega.y_C_t) is the time-averaged pre-period gap
    pre_gap = (y_trt_pre - y_c_wtd_pre).mean()  # equal-weight average
    att = (y_trt_post - y_c_wtd_post) - pre_gap
    return float(att)


def placebo_se(Y_ctrl: np.ndarray, Y_trt: np.ndarray,
               rng: np.random.Generator) -> float:
    """Permutation SE: draw n_trt from control pool as fake treated."""
    n_trt = len(Y_trt)
    N0    = len(Y_ctrl)
    if N0 <= n_trt:
        return np.nan
    placebos = []
    for _ in range(N_PLACEBO):
        idx  = rng.choice(N0, size=n_trt, replace=False)
        Y_ft = Y_ctrl[idx]
        Y_fc = np.delete(Y_ctrl, idx, axis=0)
        try:
            placebos.append(sdid_att(Y_fc, Y_ft))
        except Exception:
            pass
    return float(np.std(placebos, ddof=1)) if len(placebos) > 1 else np.nan


def main() -> None:
    print("=" * 70)
    print("Synthetic DiD: Mechanism outcomes (regularised NNLS, Python)")
    print(f"  WFP floor={WFP_FLOOR}  T0={T0}  T1={T1}  "
          f"N_max_ctrl={N_MAX_CTRL}  Placebos={N_PLACEBO}")
    print("=" * 70)

    rng = np.random.default_rng(RNG_SEED)
    df, wfp_tracts = load_data()

    rows = []
    for outcome, label in OUTCOMES.items():
        scale = SCALES[outcome]
        print(f"\n  {outcome} ({label})")
        mats = build_matrices(df, outcome, wfp_tracts, rng)
        if mats is None:
            print("    [SKIP] Insufficient balanced sample")
            continue
        Y_ctrl, Y_trt = mats
        n_c, n_t = len(Y_ctrl), len(Y_trt)
        print(f"    N_ctrl={n_c}  N_trt={n_t}  zeta={_zeta(Y_ctrl):.4f}", flush=True)

        att = sdid_att(Y_ctrl, Y_trt)
        print(f"    ATT = {att*scale:+.4f}  |  running {N_PLACEBO} placebos ...", flush=True)

        se    = placebo_se(Y_ctrl, Y_trt, rng)
        ci_lo = att - 1.96 * se
        ci_hi = att + 1.96 * se
        print(f"    SE = {se*scale:.4f}  CI = [{ci_lo*scale:+.4f}, {ci_hi*scale:+.4f}]")
        rows.append({
            "outcome": outcome, "method": "synthdid",
            "att": att * scale, "se": se * scale,
            "ci_lo": ci_lo * scale, "ci_hi": ci_hi * scale,
            "n_ctrl": n_c, "n_treated": n_t,
        })

    out = RESULTS / "mechanism_synthdid.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\n[OK] Saved: {out}")


if __name__ == "__main__":
    main()
