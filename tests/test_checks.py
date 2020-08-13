import pytest

from datetime import datetime

from ..code.checks import _time_logic_check, datetime_iso_format_check


class TestChecks:
    def setup_method(self):
        self.insert_time = "2016-06-14T00:00:00.000Z"
        self.update_time = "2018-07-07T00:00:00.000Z"

        self.wrong_insert_time = "2019-06-14T00:00:00.000Z"
        self.wrong_update_time = "2009-06-14T00:00:00.000Z"

        self.iso_time = "2016-06-14T00:00:00.000Z"
        self.non_iso_time = "2016-06-1400:00:00.000"

    def test_time_logic_check(self):
        assert _time_logic_check(self.insert_time, self.update_time) == True
        assert _time_logic_check(self.wrong_insert_time, self.update_time) == False
        assert _time_logic_check(self.insert_time, self.wrong_update_time) == False

    def test_datetime_iso_format_check(self):
        assert datetime_iso_format_check(self.iso_time)["valid"] == True
        assert datetime_iso_format_check(self.non_iso_time)["valid"] == False