## Running the program

*Note:* This program requires `Python 3.8` installed in your system.

**Clone the repo:** [https://github.com/NASA-IMPACT/pyARC/](https://github.com/NASA-IMPACT/pyARC/)

**Go to the project directory:** `cd pyARC`

**Create a python virtual environment:** `python -m venv env`

**Activate the environment:** `source env/bin/activate`

**Install the requirements:** `pip install -r requirements.txt`

**Run `main.py`:**

```
▶ python main.py -h  
usage: usage: main.py [-h] [--query QUERY | --concept_ids CONCEPT_IDS [CONCEPT_IDS ...]] [--file FILE | --fake FAKE] [--format [FORMAT]]

arguments:
  -h, --help            show this help message and exit
  --query QUERY         CMR query URL.
  --concept_ids CONCEPT_IDS [CONCEPT_IDS ...]
                        List of concept IDs.
  --file FILE           Path to the test file, either absolute or relative to the root dir.
  --fake FAKE           Use a fake content for testing.
  --format [FORMAT]     The metadata format

```
To test a local file, use the `--file` argument. Give it either an absolute file path or a file path relative to the project root directory.

Example:
`▶ python main.py --file "tests/fixtures/test_cmr_metadata.echo10"`
or
`▶ python main.py --file "/Users/batman/projects/pyARC/tests/fixtures/test_cmr_metadata.echo10"`

## Adding a custom check

To add a custom check, follow the following steps:

  

**Add an entry to the `schemas/rule_mapping.json` file in the form:**
```
{  
	"rule_id": "<An id for the rule in snake case>",  
	"rule_name": "<Name of the Rule>",  
	"fields_to_apply": [  
		{  
			"fields": [  
				"<The primary field1 to apply to (full path separated by /)>",
				"<Related field 11>",
				"<Related field 12>",
				"<Related field ...>",
				"<Related field 1n>",  
			],
			"relation": "relation_between_the_fields_if_any"  
		},

		{  
			"fields": [  
				"<The primary field2 to apply to (full path separated by /)>",
				"<Related field 21>",
				"<Related field 22>",
				"<Related field ...>",
				"<Related field 2n>",  
			],
			"relation": "relation_between_the_fields_if_any"  
		}  
	]  	
}
```

An example:

```
{  
	"rule_id": "date_compare",  
	"rule_name": "Data Update Time Logic Check",  
	"fields_to_apply": [  
		{  
			"fields": [  
				"Collection/InsertTime",  
				"Collection/LastUpdate"  
			],  
			"relation": "lte"  
		},  
		{  
			"fields": [  
				"Collection/Temporal/RangeDateTime/BeginningDateTime",  
				"Collection/Temporal/RangeDateTime/EndingDateTime"  
			],  
			"relation": "lte"  
		}  
	]  
},
```
**Add a corresponding entry to `schemas/checks.json` in the format:**

```
"<rule_id from rule_mapping.json>": {  
	"data_type": "<the data type of the value>",  
	"check_function": "<the function that implements the check>",  
	"dependencies": [  
		"<any dependent check that needs to be run before this check>"  
	],  
	"description": "<description of the check>",  
	"available": <check availability, either true or false>  
},

```

The `data_type` can be `datetime`, `string`, `url` or `custom`.

The `check_function` should be either one of the available functions, or your own custom function.

An example:

```
"date_compare": {  
	"data_type": "datetime",  
	"check_function": "compare",  
	"dependencies": [  
		"datetime_format_check"  
	],  
	"description": "Compares two datetimes based on the relation given.",  
	"available": true  
},
```

**If you’re writing your own check function:**

Locate the validator file based on the `data_type` of the check in `code/` directory. It is in the form: `<data_type>_validator.py`. Example: `string_validator.py`, `url_validator.py`, etc.

Write a `@staticmethod` member method in the class for that particular check. See examples in the file itself. The return value should be in the format:  
```
{  
	"valid": <the_validity_based_on_the_check>,  
	"value": <the_value_of_the_field_in_user_friendly_format>  
}
```
You can re-use any functions that are already there to reduce redundancy.

**Adding output messages to checks**:

Add an entry to the `schemas/check_messages_override.json` file like this:

```
{  
	"check_id": "<The id of the check/rule>",  
	"message": {  
		"success": "<The message to show if the check succeeds>",  
		"failure": "<The message to show if the check fails>",  
		"warning": "<The warning message>"  
	},  
	"help": {  
		"message": "<The help message if any.>",  
		"url": "<The help url if any.>"  
	},  
	"remediation": "<The remediation step to make the check valid.>"  
}
```
An example:
```
{  
	"check_id": "abstract_length_check",  
	"message": {  
		"success": "The length is correct.",  
		"failure": "The length of the field should be less than 100. The current length is `{}`.",  
		"warning": "Make sure length is 100."  
	},  
	"help": {  
		"message": "The length of the field can only be less than 100 characters.",  
		"url": "www.lengthcheckurl.com"  
	},  
	"remediation": "A remedy."  
}
```
**Note:** See the `{}` in the failure message above? It is a placeholder for any value you want to show in the output message. To fill this placeholder with a particular value, you have to return that value from the check function that you write. You can have as many placeholders as you like, you just have to return that many values from your check function.

An example:
Suppose you have a check function:
```
@staticfunction
def is_true(value1, value2):
	return {
		"valid": value1 and value2,
		"value": [value1, value2]
	}
```
And a message:
```
...
	"failure": "The values `{}` and `{}` do not amount to a true value",
...
```
Then, if the check function receives input `value1=0` and `value2=1`, the output message will be:
```
The values 0 and 1 do not amount to a true value
```

## Use as a package
*Note:* This program requires `Python 3.8` installed in your system.

**Clone the repo:** [https://github.com/NASA-IMPACT/pyARC/](https://github.com/NASA-IMPACT/pyARC/)

**Go to the project directory:** `cd pyARC`

**Install package:** `python setup.py install`

**To check if the package was installed correctly:**
```
▶ python
>>> from pyARC import ARC
>>> validator = ARC(fake=True)
>>> validator.validate()
>>> ...
```

**To provide locally installed file:**
```
▶ python
>>> from pyARC import ARC
>>> validator = ARC(file_path="<path to metadata file>")
>>> validator.validate()
>>> ...
```

**To provide rules for new fields or override:**
```
▶ cat rule_override.json
{
    "data_update_time_logic_check": {
        "rule_name": "Data Update Time Logic Check",
        "fields_to_apply": [
            {
                "fields": [
                    "Collection/LastUpdate",
                    "Collection/InsertTime"
                ],
                "relation": "lte"
            }
        ],
        "severity": "info",
        "check_id": "date_compare"
    },
    "new_field": {
        "rule_name": "Check for new field",
        "fields_to_apply": [
            {
                "fields": [
                    "<new field name>",
                    "<other new field name>",
                ],
                "relation": "lte"
            }
        ],
        "severity": "info",
        "check_id": "<check_id>"
    }
}
▶ python
>>> from pyARC import ARC
>>> validator = ARC(checks_override="<path to rule_override.json>")
>>> validator.validate()
>>> ...
```


**To provide custom messages for new or old fields:**
```
▶ cat messages_override.json
{
    "data_update_time_logic_check": {
        "failure": "The UpdateTime `{}` comes after the provided InsertTime `{}`.",
        "help": {
            "message": "",
            "url": "https://wiki.earthdata.nasa.gov/display/CMR/Data+Dates"
        },
        "remediation": "Everything is alright!"
    },
    "new_check": {
        "failure": "Custom check for `{}` and `{}.",
        "help": {
            "message": "",
            "url": "https://wiki.earthdata.nasa.gov/display/CMR/Data+Dates"
        },
        "remediation": "<remediation steps>"
    }
}
▶ python
>>> from pyARC import ARC
>>> validator = ARC(checks_override="<path to rule_override.json>", messages_override=<path to messages_override.json>)
>>> validator.validate()
>>> ...
```