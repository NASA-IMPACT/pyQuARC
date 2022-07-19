# pyQuARC

### Open Source Library for Earth Observation Metadata Quality Assessment


## Introduction

The pyQuARC (pronounced "pie-quark") library was designed to read and evaluate descriptive metadata used to catalog Earth observation data products and files. This type of metadata focuses and limits attention to important aspects of data, such as the spatial and temporal extent, in a structured manner that can be leveraged by data catalogs and other applications designed to connect users to data. Therefore, poor quality metadata (e.g. inaccurate, incomplete, improperly formatted, inconsistent) can yield subpar results when users search for data. Metadata that inaccurately represents the data it describes risks matching users with data that does not reflect their search criteria and, in the worst-case scenario, can make data impossible to find.

Given the importance of high quality metadata, it is necessary that metadata be regularly assessed and updated as needed. pyQuARC is a tool that can help streamline the process of assessing metadata quality by automating it as much as possible. In addition to basic validation checks (e.g. adherence to the metadata schema, controlled vocabularies, and link checking), pyQuARC flags opportunities to improve or add contextual metadata information to help the user connect to, access, and better understand the data product. pyQuARC also ensures that information common to both data product (i.e. collection) and the file-level (i.e. granule) metadata are consistent and compatible. As open source software, pyQuARC can be adapted and customized to allow for quality checks unique to different needs.

## pyQuARC Base Package

pyQuARC was specifically designed to assess metadata in NASA’s [Common Metadata Repository (CMR)](https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components), which is a centralized metadata repository for all of NASA’s Earth observation data products. In addition to NASA’s ~9,000 data products, the CMR also holds metadata for over 40,000 additional Earth observation data products submitted by external data partners. The CMR serves as the backend for NASA’s Earthdata Search (search.earthdata.nasa.gov) and is also the authoritative metadata source for NASA’s [Earth Observing System Data and Information System (EOSDIS).](https://earthdata.nasa.gov/eosdis)

pyQuARC was developed by a group called the [Analysis and Review of the CMR (ARC)](https://earthdata.nasa.gov/esds/impact/arc) team. The ARC team conducts quality assessments of NASA’s metadata records in CMR, identifies opportunities for improvement in the metadata records, and collaborates with the data archive centers to resolve any identified issues. ARC has developed a [metadata quality assessment framework](http://doi.org/10.5334/dsj-2021-017) which specifies a common set of assessment criteria. These criteria focus on correctness, completeness, and consistency with the goal of making data more discoverable, accessible, and usable. The ARC metadata quality assessment framework is the basis for the metadata checks that have been incorporated into pyQuARC base package. Specific quality criteria for each CMR metadata element is documented in the following wiki:
[https://wiki.earthdata.nasa.gov/display/CMR/CMR+Metadata+Best+Practices%3A+Landing+Page](https://wiki.earthdata.nasa.gov/display/CMR/CMR+Metadata+Best+Practices%3A+Landing+Page)

There is an “ARC Metadata QA/QC” section on the wiki page for each metadata element that lists quality criteria categorized by level of [priority. Priority categories](https://wiki.earthdata.nasa.gov/display/CMR/ARC+Priority+Matrix) are designated as high (red), medium (yellow), or low (blue), and are intended to communicate the importance of meeting the specified criteria.

The CMR is designed around its own metadata standard called the [Unified Metadata Model (UMM).](https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/cmr/umm) In addition to being an extensible metadata model, the UMM also provides a cross-walk for mapping between the various CMR-supported metadata standards. CMR-supported metadata standards currently include:
* [DIF10](https://earthdata.nasa.gov/esdis/eso/standards-and-references/directory-interchange-format-dif-standard) (Collection/Data Product-level only)
* [ECHO10](https://earthdata.nasa.gov/esdis/eso/standards-and-references/echo-metadata-standard) (Collection/Data Product and Granule/File-level metadata)
* [ISO19115-1 and ISO19115-2](https://earthdata.nasa.gov/esdis/eso/standards-and-references/iso-19115) (Collection/Data Product and Granule/File-level metadata)
* [UMM-JSON](https://wiki.earthdata.nasa.gov/display/CMR/CMR+Documents) (UMM)
	* UMM-C (Collection/Data Product-level metadata)
	* UMM-G (Granule/File-level metadata)
	* UMM-S (Service metadata)
	* UMM-T (Tool metadata)

**Currently, pyQuARC only supports ECHO 10 and DIF10 collection-level metadata. Support for additional metadata standards will continue to be added in the coming months.** When completed, pyQuARC will support the DIF10 (collection only), ECHO10 (collection and granule), UMM-C and UMM-G standards. At this time, there are no plans to add ISO 19115 or UMM-S/T specific checks. **Additionally, the output messages pyQuARC currently displays should be taken with a grain of salt. There is still testing and clean-up work to be done.**  

**For inquiries, please email: jeanne.leroux@nsstc.uah.edu**

## pyQuARC as a Service (QuARC)

QuARC is pyQuARC deployed as a service and can be found here: https://quarc.nasa-impact.net/docs/

QuARC is still in beta but is regularly synced with the latest version of pyQuARC on GitHub.

![QuARC](https://user-images.githubusercontent.com/17416300/179866276-7c025699-01a1-4d3e-93cd-50e12c5a5ec2.png)

## Architecture

![pyQuARC Architecture](/images/architecture.png)

The Downloader is used to obtain a copy of a metadata record of interest from the CMR. This is accomplished using a [CMR API query,](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html) where the metadata record of interest is identified by its unique identifier in the CMR (concept_id). CMR API documentation can be found here:
[https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)

There is also the option to select and run pyQuARC on a metadata record already downloaded to your local desktop.

The `checks.json` file includes a comprehensive list of rules. Each rule is specified by its `rule_id,` associated function, and any dependencies on specific metadata elements. 

The `rule_mapping.json` file specifies which metadata element(s) each rule applies to. The `rule_mapping.json` also references the `messages.json` file which includes messages that can be displayed when a check passes or fails.

Furthermore, the `rule_mapping.json` file specifies the level of severity associated with a failure. If a check fails, it will be assigned a severity category of “<span style="color:red">error</span>,” “<span style="color:orange">warning</span>,” or <span style="color:blue">info</span>.” These categories correspond to priority categorizations in [ARC’s priority matrix](https://wiki.earthdata.nasa.gov/display/CMR/ARC+Priority+Matrix) and communicate the importance of the failed check, with “error” being the most critical category, “warning” indicating a failure of medium priority, and “info” indicating a minor issue or inconsistency. Default severity values are assigned based on ARC’s metadata quality assessment framework, but can be customized to meet individual needs.

## Customization
pyQuARC is designed to be customizable. Output messages can be modified using the `messages_override.json` file - any messages added to `messages_override.json` will display over the default messages in the `message.json` file. Similarly, there is a `rule_mapping_override.json` file which can be used to override the default settings for which rules/checks are applied to which metadata elements.  

There is also the opportunity for more sophisticated customization. New QA rules can be added and existing QA rules can be edited or removed. Support for new metadata standards can be added as well. Further details on how to customize pyQuARC will be provided in the technical user’s guide below.

While the pyQuARC base package is currently managed by the ARC team, the long term goal is for it to be owned and governed by the broader EOSDIS metadata community.

## Install/User’s Guide
### Running the program

*Note:* This program requires `Python 3.8` installed in your system.

**Clone the repo:** [https://github.com/NASA-IMPACT/pyQuARC/](https://github.com/NASA-IMPACT/pyQuARC/)

**Go to the project directory:** `cd pyQuARC`

**Create a python virtual environment:** `python -m venv env`

**Activate the environment:** `source env/bin/activate`

**Install the requirements:** `pip install -r requirements.txt`

**Run `main.py`:**

```
▶ python pyQuARC/main.py -h  
usage: main.py [-h] [--query QUERY | --concept_ids CONCEPT_IDS [CONCEPT_IDS ...]] [--file FILE | --fake FAKE] [--format [FORMAT]]

arguments:
  -h, --help            show this help message and exit
  --query QUERY         CMR query URL.
  --concept_ids CONCEPT_IDS [CONCEPT_IDS ...]
                        List of concept IDs.
  --file FILE           Path to the test file, either absolute or relative to the root dir.
  --fake FAKE           Use a fake content for testing.
--format [FORMAT]     	The metadata format (currently supported: 'echo10' and 'dif10')

```
To test a local file, use the `--file` argument. Give it either an absolute file path or a file path relative to the project root directory.

Example:
`▶ python pyQuARC/main.py --file "tests/fixtures/test_cmr_metadata.echo10"`
or
`▶ python pyQuARC/main.py --file "/Users/batman/projects/pyQuARC/tests/fixtures/test_cmr_metadata.echo10"`

### Adding a custom rule

To add a custom rule, follow the following steps:



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
			"relation": "relation_between_the_fields_if_any",
                        "dependencies": [
                            [
                                "<any dependent check that needs to be run before this check (if any)>",
                                "<field to apply this dependent check to (if any)>"
                            ]
                        ]
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
	],
        "data" : [ <any external data that you want to send to the rule> ],
        "check_id": "< one of the available checks, see CHECKS.md, or custom check if you are a developer>"
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
			"relation": "lte",
                        "dependencies": [
                            [
                                "datetime_format_check",
                                "Collection/InsertTime"
                            ],
                            [
                                "datetime_format_check",
                                "Collection/LastUpdate"
                            ]
                        ]
		},
		{  
			"fields": [  
				"Collection/Temporal/RangeDateTime/BeginningDateTime",  
				"Collection/Temporal/RangeDateTime/EndingDateTime"  
			],  
			"relation": "lte"  
		}  
	],
    "data": [],
    "check_id": "date_compare"
},
```
`data` is any external data that you want to pass to the check. For example, for a `controlled_keywords_check`, it would be the controlled keywords list:

```

"data": [ ["keyword1", "keyword2"] ]
```
`check_id` is the id of the corresponding check from `checks.json`. It'll usually be one of the available checks. An exhaustive list of all the available checks can be found in [CHECKS.md](./CHECKS.md).

**If you're writing your own custom check to `schemas/checks.json`:**

Add an entry in the format:
```
"<a check id>": {  
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

### Use as a package
*Note:* This program requires `Python 3.8` installed in your system.

**Clone the repo:** [https://github.com/NASA-IMPACT/pyQuARC/](https://github.com/NASA-IMPACT/pyQuARC/)

**Go to the project directory:** `cd pyQuARC`

**Install package:** `python setup.py install`

**To check if the package was installed correctly:**
```
▶ python
>>> from pyQuARC import ARC
>>> validator = ARC(fake=True)
>>> validator.validate()
>>> ...
```

**To provide locally installed file:**
```
▶ python
>>> from pyQuARC import ARC
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
>>> from pyQuARC import ARC
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
>>> from pyQuARC import ARC
>>> validator = ARC(checks_override="<path to rule_override.json>", messages_override=<path to messages_override.json>)
>>> validator.validate()
>>> ...
```
