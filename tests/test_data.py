"""
Unit tests for data loading and cleaning.
"""

import pytest
from pathlib import Path


class TestDataLoading:
    """Tests for data.build_analysis_dataset module."""

    def test_analysis_dataset_structure(self):
        """Check that analysis dataset has expected columns."""
        # TODO: Implement test
        pytest.skip("Data loading not yet implemented")

    def test_no_missing_outcomes(self):
        """Check that outcome variables have no missing values."""
        pytest.skip("Data loading not yet implemented")

    def test_sample_restrictions(self):
        """Verify sample restrictions applied correctly."""
        pytest.skip("Data loading not yet implemented")


class TestTreatmentAssignment:
    """Tests for treatment indicator and timing."""

    def test_treatment_year_validity(self):
        """Check that treatment years are within sample window."""
        pytest.skip("Implementation pending")

    def test_no_untreated_in_treated_cohort(self):
        """Verify no untreated units in treated cohorts."""
        pytest.skip("Implementation pending")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
