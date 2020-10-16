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


FUNCTION_MAPPING = {
    "input": [
        {
            "datatype": "datetime",
            "function": "iso_format_check"
        },
        {
            "datatype": "datetime",
            "function": "format_check"
        }
    ],
    "output": [
        True,
        False
    ]
}
