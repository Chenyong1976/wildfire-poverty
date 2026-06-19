"""
Staggered difference-in-differences estimation using Callaway & Sant'Anna (2021).

Main estimating equation:
    outcome_{c,t} = alpha_c + lambda_t + sum_h beta_h * 1[relative_year = h] + eps_{c,t}

where:
- c = county, t = year
- alpha_c, lambda_t = county and year FE
- beta_h = event-study coefficient at relative year h (h < 0 for pre-trends, h >= 0 for post-treatment)
- ATT = average of beta_h for h >= 0

TODO: Implement via csdid Python package or call R's did package.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def estimate_did(analysis_df: pd.DataFrame):
    """
    Estimate staggered DiD with Callaway & Sant'Anna (2021).

    Parameters
    ----------
    analysis_df : pd.DataFrame
        Analysis-ready panel with columns: fips, year, outcome, treated, treatment_year.

    Returns
    -------
    dict
        Results dictionary with keys:
        - 'att': ATT point estimate
        - 'event_study': DataFrame with columns (relative_year, beta, se, ci_lower, ci_upper)
        - 'heterogeneous': Heterogeneous effects by subgroup (if computed)
    """
    logger.info("Estimating Callaway & Sant'Anna staggered DiD...")

    # TODO: Implement DiD estimation
    # 1. Use csdid or call R's did package
    # 2. Compute event-study coefficients beta_h for h in [-5, ..., 5]
    # 3. Check pre-trends (beta_h for h < 0 should be ~0)
    # 4. Compute ATT = avg(beta_h for h >= 0)
    # 5. Report 95% CIs

    logger.warning("DiD estimation not yet implemented. Placeholder only.")

    results = {
        'att': None,
        'event_study': pd.DataFrame(),
        'heterogeneous': {}
    }

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
