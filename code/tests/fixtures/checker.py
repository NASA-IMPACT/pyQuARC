DUMMY_METADATA_CONTENT = {
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

INPUT_OUTPUT = {
    "date_datetime_iso_format_check": [
        {
            "input": "2016-06-14T00:00:00.000Z",
            "output": True,
        },
        {
            "input": "2016-06-1400:00:00.000",
            "output": False,
        }
    ],
    "get_path_value": [
        {
            "input": "Contacts/Contact/ContactPersons/ContactPerson/glabb",
            "output": set()
        },
        {
            "input": "Contacts/Contact/ContactPersons/ContactPerson/blabla",
            "output": {"BOSILOVICH"}
        },
        {
            "input": "Contacts/Contact/ContactPersons/ContactPerson/FirstName",
            "output": {"DANA", "MICHAEL", "SLESA"}
        }
    ]
    
}