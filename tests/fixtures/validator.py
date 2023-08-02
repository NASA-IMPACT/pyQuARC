import os

WORKING_DIR = os.getcwd()
FIXTURE_PATH = os.path.join(WORKING_DIR, "tests/fixtures/")

INPUT_OUTPUT = {
    "date_datetime_iso_format_check": [
        {
            "input": "2016-06-14T00:00:00.000Z",
            "output": True,
        },
        {
            "input": "2016-06-1400:00:00.000",
            "output": False,
        },
    ],
    "get_path_value": [
        {
            "input": "Contacts/Contact/ContactPersons/ContactPerson/glabb",
            "output": set(),
        },
        {
            "input": "Contacts/Contact/ContactPersons/ContactPerson/blabla",
            "output": {"BOSILOVICH"},
        },
        {
            "input": "Contacts/Contact/ContactPersons/ContactPerson/FirstName",
            "output": {"DANA", "SLESA", "MICHAEL"},
        },
    ],
}
