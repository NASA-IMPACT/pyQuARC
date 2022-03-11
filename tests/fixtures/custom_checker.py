from collections import OrderedDict


INPUT_OUTPUT = {
    "get_path_value": {
        "input": [
            "Collection/ShortName",
            "Collection/DataSetId",
            "Collection/Contacts/Contact/Role",
            "Collection/Platforms/Platform/Instruments/Instrument",
        ],
        "output": [
            ["ACOS_L2S"],
            [
                "ACOS GOSAT/TANSO-FTS Level 2 Full Physics Standard Product V7.3 (ACOS_L2S) at GES DISC"
            ],
            ["ARCHIVER", "TECHNICAL CONTACT"],
            [
                OrderedDict(
                    [
                        ("ShortName", "TANSO-FTS"),
                        ("LongName", "Thermal And Near Infrared Sensor For Carbon Observation"),
                    ]
                )
            ],
        ],
    }
}
