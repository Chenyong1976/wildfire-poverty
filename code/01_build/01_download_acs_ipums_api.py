#!/usr/bin/env python3
"""
Download ACS 5-year tract-level data from IPUMS via the IPUMS API.

Downloads poverty, income, employment, and migration data for ACS periods:
2012, 2017, 2023 at census tract level for all lower-48 US states.

Requires IPUMS API key (https://account.ipums.org/api)
"""

import requests
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "acs_extracts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# IPUMS API configuration
# Note: IPUMS API v2 uses different endpoints; trying common variations
IPUMS_API_BASE = "https://api.ipums.org/v2"
IPUMS_PROJECT = "usa"

# ACS samples and years
ACS_SAMPLES = {
    2012: "us2012a",      # ACS 2008-2012 5-year
    2017: "us2017a",      # ACS 2013-2017 5-year
    2023: "us2023a",      # ACS 2019-2023 5-year
}

# Variables to extract
# B17001: Poverty status
# B19013: Median household income
# B23025: Employment status
# B07001: Residence 5 years ago (migration proxy)
VARIABLES = [
    "B17001",  # Poverty Status
    "B19013",  # Median Household Income
    "B23025",  # Employment Status
    "B07001",  # Residence 5 Years Ago
]


class IPUMSAPIClient:
    """Client for IPUMS API operations."""

    def __init__(self, api_key: str):
        """Initialize IPUMS API client."""
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """Make authenticated request to IPUMS API."""
        url = f"{IPUMS_API_BASE}{endpoint}"

        try:
            if method == "POST":
                response = self.session.post(url, json=json_data, timeout=timeout)
            elif method == "GET":
                response = self.session.get(url, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"[ERROR] API request failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response: {e.response.text}")
            raise

    def create_extract(
        self, sample: str, variables: list, geographic_level: str = "tract"
    ) -> Dict[str, Any]:
        """Create a new extract definition."""
        payload = {
            "samples": [sample],
            "variables": variables,
            "geographic_level": geographic_level,
        }

        print(f"[API] Creating extract: sample={sample}, vars={variables}")
        response = self._make_request(
            "POST",
            f"/projects/{IPUMS_PROJECT}/extracts",
            json_data=payload,
        )

        extract_id = response.get("id")
        print(f"[OK] Extract created with ID: {extract_id}")
        return response

    def get_extract_status(self, extract_id: int) -> Dict[str, Any]:
        """Check status of an extract."""
        response = self._make_request(
            "GET",
            f"/projects/{IPUMS_PROJECT}/extracts/{extract_id}",
        )
        return response

    def wait_for_extract(
        self, extract_id: int, max_wait_minutes: int = 30
    ) -> bool:
        """Poll extract until it's ready for download."""
        print(f"[WAITING] Polling extract {extract_id} for completion...")

        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        poll_interval = 5  # seconds

        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                print(f"[TIMEOUT] Extract did not complete within {max_wait_minutes} minutes")
                return False

            response = self.get_extract_status(extract_id)
            status = response.get("status")

            if status == "completed":
                print(f"[OK] Extract {extract_id} completed")
                return True
            elif status in ["failed", "error"]:
                print(f"[ERROR] Extract {extract_id} failed with status: {status}")
                print(f"Message: {response.get('message', 'N/A')}")
                return False

            # Print status update
            time_mins = int(elapsed / 60)
            print(f"  [STATUS] {status} ({time_mins} min elapsed)...")

            time.sleep(poll_interval)

    def download_extract(self, extract_id: int, output_path: Path) -> bool:
        """Download extract data to file."""
        print(f"[DOWNLOADING] Extract {extract_id} to {output_path}...")

        try:
            # Get download URL
            response = self._make_request(
                "GET",
                f"/projects/{IPUMS_PROJECT}/extracts/{extract_id}/download",
            )

            download_url = response.get("url")
            if not download_url:
                print("[ERROR] No download URL in response")
                return False

            # Download file
            file_response = requests.get(download_url, timeout=300)
            file_response.raise_for_status()

            # Save to disk
            with open(output_path, "wb") as f:
                f.write(file_response.content)

            file_size_mb = output_path.stat().st_size / (1024 ** 2)
            print(f"[OK] Downloaded {file_size_mb:.1f} MB to {output_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return False


def download_acs_year(
    api_client: IPUMSAPIClient,
    year: int,
    sample_code: str,
    output_path: Path,
) -> bool:
    """Download ACS data for a specific year."""

    print(f"\n{'='*80}")
    print(f"DOWNLOADING ACS {year}")
    print(f"{'='*80}")

    # Check if already exists
    if output_path.exists():
        print(f"[SKIP] Already exists: {output_path}")
        return True

    # Create extract
    try:
        extract = api_client.create_extract(
            sample=sample_code,
            variables=VARIABLES,
            geographic_level="tract",
        )
        extract_id = extract["id"]
    except Exception as e:
        print(f"[ERROR] Failed to create extract: {e}")
        return False

    # Wait for completion
    if not api_client.wait_for_extract(extract_id):
        print(f"[ERROR] Extract did not complete: {extract_id}")
        return False

    # Download
    if not api_client.download_extract(extract_id, output_path):
        print(f"[ERROR] Failed to download extract: {extract_id}")
        return False

    # Verify file
    if not output_path.exists() or output_path.stat().st_size == 0:
        print(f"[ERROR] Downloaded file is empty or missing")
        return False

    print(f"[OK] ACS {year} download complete")
    return True


def main(api_key: str) -> bool:
    """Download ACS data for all years."""

    print("=" * 80)
    print("IPUMS ACS 5-YEAR TRACT-LEVEL DATA DOWNLOAD")
    print("=" * 80)

    # Initialize API client
    try:
        api_client = IPUMSAPIClient(api_key)
        print("[OK] IPUMS API client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize API client: {e}")
        return False

    # Download each year
    success = True
    for year in sorted(ACS_SAMPLES.keys()):
        sample_code = ACS_SAMPLES[year]
        output_path = OUTPUT_DIR / f"acs_{year}_tract_extract.csv"

        if not download_acs_year(api_client, year, sample_code, output_path):
            success = False
            print(f"[FAILED] ACS {year} download failed")

    # Summary
    print(f"\n{'='*80}")
    if success:
        print("[OK] All ACS downloads complete!")
        print(f"Files saved to: {OUTPUT_DIR}")
        print("\nNext steps:")
        print("1. Parse RUCC 2013 XLS → CSV")
        print("2. Run data validation (Week 2)")
        print("3. Register PAP on OSF")
    else:
        print("[ERROR] Some downloads failed")

    return success


if __name__ == "__main__":
    import sys

    # API key from command line or environment
    api_key = sys.argv[1] if len(sys.argv) > 1 else None

    if not api_key:
        import os

        api_key = os.environ.get("IPUMS_API_KEY")

    if not api_key:
        print("[ERROR] IPUMS API key not provided")
        print("Usage: python script.py <api_key>")
        print("Or set IPUMS_API_KEY environment variable")
        sys.exit(1)

    success = main(api_key)
    sys.exit(0 if success else 1)
