import pytest
from unittest.mock import patch
from datetime import datetime

from pyQuARC.code.datetime_validator import DatetimeValidator
from tests.fixtures.validator import INPUT_OUTPUT


class TestValidator:
    """
    Test cases for the validator script in validator.py
    """

    def setup_method(self):
        pass

    def test_datetime_iso_format_check(self):
        for input_output in INPUT_OUTPUT["date_datetime_iso_format_check"]:
            assert (
                DatetimeValidator.iso_format_check(input_output["input"])["valid"]
            ) == input_output["output"]

    def test_datetime_compare(self):
        pass

    @patch("pyQuARC.code.datetime_validator.set_cmr_prms")
    @patch("pyQuARC.code.datetime_validator.cmr_request")
    @patch("pyQuARC.code.datetime_validator.get_date_time")
    @pytest.mark.parametrize(
        "datetime_string, granule_datetime, expected_valid, expected_severity",
        [
            # Exact match → valid, no severity
            ("2025-08-01T00:00:00Z", "2025-08-01T00:00:00Z", True, None),

            # Different date but within 24 hours → invalid, no severity
            ("2025-08-02T00:00:00Z", "2025-08-01T12:00:00Z", False, None),

            # More than 24 hours difference → invalid, severity error
            ("2025-08-03T00:00:00Z", "2025-08-01T00:00:00Z", False, "error"),

            # No granules returned → valid=False, severity error
            ("2025-08-01T00:00:00Z", None, False, "error"),
        ],
    )
    def test_validate_datetime_against_granules(
        self,
        mock_get_date_time,
        mock_cmr_request,
        mock_set_cmr_prms,
        datetime_string,
        granule_datetime,
        expected_valid,
        expected_severity,
    ):
        # Arrange: cmr_request mock
        if granule_datetime is None:
            mock_cmr_request.return_value = {"feed": {"entry": []}}
        else:
            mock_cmr_request.return_value = {
                "feed": {
                    "entry": [
                        {
                            "time_start": granule_datetime,
                            "time_end": granule_datetime,
                        }
                    ]
                }
            }

        mock_set_cmr_prms.return_value = {"mock": "params"}

        # Mock get_date_time to return datetime objects or None
        def fake_get_date_time(val):
            if val is None:
                return None
            return datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ")

        mock_get_date_time.side_effect = fake_get_date_time

        # Act
        result = DatetimeValidator.validate_datetime_against_granules(
            datetime_string,
            collection_shortname="TEST",
            version="1",
            sort_key="start_date",
            time_key="time_start",
        )

        # Assert
        assert result["valid"] == expected_valid
        if expected_severity:
            assert result["severity"] == expected_severity
        else:
            assert "severity" not in result
