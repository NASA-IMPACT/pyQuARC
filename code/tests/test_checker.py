import json
import os
import pytest

from datetime import datetime

from ..checker import Checker


class TestChecks:
    def setup_method(self):
        self.insert_time = "2016-06-14T00:00:00.000Z"
        self.update_time = "2018-07-07T00:00:00.000Z"

        self.wrong_insert_time = "2019-06-14T00:00:00.000Z"
        self.wrong_update_time = "2009-06-14T00:00:00.000Z"

        self.iso_time = "2016-06-14T00:00:00.000Z"
        self.non_iso_time = "2016-06-1400:00:00.000"

        self.checker = Checker(TestChecks._read_test_metadata())

    @staticmethod
    def _read_test_metadata():
        with open(os.path.join(os.getcwd(), "code/tests/data/test_cmr_metadata_echo10.json"), "r") as content_file:
            return content_file.read()

    def test_time_logic_check(self):
        assert self.checker._time_logic_check(self.insert_time, self.update_time) == True
        assert self.checker._time_logic_check(
            self.wrong_insert_time, self.update_time) == False
        assert self.checker._time_logic_check(
            self.insert_time, self.wrong_update_time) == False

    def test_datetime_iso_format_check(self):
        assert self.checker.datetime_iso_format_check(self.iso_time)["valid"] == True
        assert self.checker.datetime_iso_format_check(self.non_iso_time)["valid"] == False

    def test_run(self):
        self.checker.run()

    def test_get_path_value(self):
        input_data = {
            "Contacts": {
                "Contact": [
                    {
                        "Role": "ARCHIVER",
                        "OrganizationName": "NASA/GSFC/SED/ESD/GCDC/GESDISC",
                        "ContactPersons": {
                            "ContactPerson": {
                                "FirstName": "SLESA",
                                "LastName": "OSTRENGA",
                                "JobPosition": "METADATA AUTHOR"
                            }
                        }
                    },
                    {
                        "Role": "TECHNICAL CONTACT",
                        "ContactPersons": {
                            "ContactPerson": [
                                {
                                    "FirstName": "DANA",
                                    "LastName": "OSTRENGA",
                                    "JobPosition": "METADATA AUTHOR"
                                },
                                {
                                    "FirstName": "MICHAEL",
                                    "LastName": "BOSILOVICH",
                                    "JobPosition": "INVESTIGATOR"
                                },
                                {
                                    "blabla": "BOSILOVICH",
                                }
                            ]
                        }
                    }
                ]
            },
        }

        input_output = [
            {
                "path": "Contacts/Contact/ContactPersons/ContactPerson/glabb",
                "expected_output": (False, set())
            },
            {
                "path": "Contacts/Contact/ContactPersons/ContactPerson/blabla",
                "expected_output": (True, {"BOSILOVICH"})
            },
            {
                "path": "Contacts/Contact/ContactPersons/ContactPerson/FirstName",
                "expected_output": (True, {"DANA", "MICHAEL", "SLESA"})
            }
        ]

        checker = Checker(json.dumps(input_data))

        for item in input_output:
            assert checker._get_path_value(item["path"]) == item["expected_output"]
