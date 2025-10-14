# pyQuARC 

### Open Source Library for Earth Observation Metadata Quality Assessment

[![DOI](https://zenodo.org/badge/153786129.svg)](https://zenodo.org/doi/10.5281/zenodo.10724716)

## Introduction
The pyQuARC (*pronounced "pie-quark"*) library was designed to read and evaluate descriptive metadata used to catalog Earth observation data products and files. This type of metadata focuses and limits attention to important aspects of data, such as the spatial and temporal extent, in a structured manner that can be leveraged by data catalogs and other applications designed to connect users to data. Therefore, poor quality metadata (e.g. inaccurate, incomplete, improperly formatted, inconsistent) can yield subpar results when users search for data. Metadata that inaccurately represents the data it describes risks matching users with data that does not reflect their search criteria and, in the worst-case scenario, can make data impossible to find.

Given the importance of high quality metadata, it is necessary that metadata be regularly assessed and updated as needed. pyQuARC is a tool that can help streamline the process of assessing metadata quality by automating it as much as possible. In addition to basic validation checks (e.g. adherence to the metadata schema, controlled vocabularies, and link checking), pyQuARC flags opportunities to improve or add contextual metadata information to help the user connect to, access, and better understand the data product. pyQuARC also ensures that information common to both data product (i.e. collection) and the file-level (i.e. granule) metadata are consistent and compatible. As open source software, pyQuARC can be adapted and customized to allow for quality checks unique to different needs.

## pyQuARC Metadata Quality Framework
pyQuARC was designed to assess metadata in NASA’s [Common Metadata Repository (CMR)](https://earthdata.nasa.gov/eosdis/science-system-description/eosdis-components), a centralized repository for all of NASA’s Earth observation data products. In addition, the CMR contains metadata for Earth observation products submitted by external partners. The CMR serves as the backend for NASA’s Earthdata Search ([search.earthdata.nasa.gov](https://search.earthdata.nasa.gov/)) and is also the authoritative metadata source for NASA’s [Earth Observing System Data and Information System (EOSDIS)](https://earthdata.nasa.gov/eosdis).

pyQuARC was initially developed by a group called the [Analysis and Review of the CMR (ARC)](https://www.earthdata.nasa.gov/data/projects/analysis-review-cmr-project) team. The ARC team conducted quality assessments of NASA’s metadata records in the CMR, identified opportunities for improvement in the metadata records, and collaborated with the data archive centers to resolve any identified issues. ARC has developed a [metadata quality assessment framework](http://doi.org/10.5334/dsj-2021-017) which specifies a common set of assessment criteria. These criteria focus on correctness, completeness, and consistency with the goal of making data more discoverable, accessible, and usable. The ARC metadata quality assessment framework is the basis for the metadata checks that have been incorporated into pyQuARC base package. Specific quality criteria for each CMR metadata element are documented in the [Earthdata Wiki space](https://wiki.earthdata.nasa.gov/display/CMR/CMR+Metadata+Best+Practices%3A+Landing+Page).

Each metadata element’s wiki page includes an “Metadata Validation and QA/QC” section that lists quality criteria categorized by priority levels, referred to as a priority matrix. The [priority matrix](https://wiki.earthdata.nasa.gov/spaces/CMR/pages/109874556/ARC+Priority+Matrix) are designated as high (red), medium (yellow), or low (blue), and are intended to communicate the importance of meeting the specified criteria.

The CMR is designed around its own metadata standard called the [Unified Metadata Model (UMM)](https://www.earthdata.nasa.gov/about/esdis/eosdis/cmr/umm). In addition to being an extensible metadata model, the UMM provides a crosswalk for mapping among the various CMR-supported metadata standards, including DIF10, ECHO10, ISO 19115-1, and ISO 19115-2. 

pyQuARC currently supports the following metadata standards:
* [UMM-JSON](https://wiki.earthdata.nasa.gov/display/CMR/UMM+Documents) (UMM)
	* Collection/Data Product-level metadata (UMM-C)
	* Granule/File-level metadata (UMM-G)
* [ECHO10](https://earthdata.nasa.gov/esdis/eso/standards-and-references/echo-metadata-standard)
	* Collection/Data Product-level metadata (ECHO-C)
	* Granule/File-level metadata (ECHO-G)
* [DIF10](https://earthdata.nasa.gov/esdis/eso/standards-and-references/directory-interchange-format-dif-standard)
	* Collection/Data Product-level only

## Install and Clone the Repository
The pyQuARC library requires `Python 3.10` to function properly across all operating systems.

### 1. Open your Command Prompt or Terminal and use the following command to clone the pyQuARC repository:
* `git clone https://github.com/NASA-IMPACT/pyQuARC.git`

Note: If you see the message `fatal: destination path 'pyQuARC' already exists and is not an empty directory` when running this command, it means the repository has already been cloned. To reclone it, delete the folder and its contents using the following command before running the original command again.

* `rmdir /s /q pyQuARC` # deletes the directory (be cautious)

Additional note: If you want to know where your freshly cloned pyQuARC folder ended up, you can use the following command to print your working directory:

* `pwd` # for Linux/MacOS operating systems
* `cd` # for Windows operating systems

This will show you the full path to the directory where the cloned pyQuARC repository is located. You can then append `\pyQuARC` to the end of the path to get the full path to the folder.

### 2. Configure and Activate Environment:
Create an environment to set up an isolated workspace for using pyQuARC. You can do this with Anaconda/Miniconda (Option A) or with Python’s built-in `venv` module (Option B).

**A. Use the Conda package manager to create and name the environment:**
* `conda create --name <yourenvname>` # -	Replace `<yourenvname>` with the name of your environment.

**B. Use the Python interpreter to create a virtual environment in your current directory:**
* `python -m venv env`

Next, activate the environment using either Option A or Option B, depending on how you created it in the previous step:

**A. Activate the Conda environment with the Conda package manager:**
* `conda activate <yourenvname>`

**B. Activate the Python virtual environment** 
For macOS/Linux operating systems, use the following:
* `source env/bin/activate`

For Windows operating systems, use the following command:
* `env\Scripts\activate`

Note: On Windows, you may encounter an error with this command. If that happens, use:
* `.\env\Scripts\Activate.ps1`

Be sure to reference the correct location of the env directory, as you may need to activate either the `.bat` or `.ps1` script. This error is uncommon.

### 3. Install Requirements
Next, install the required packages. The requirements are included as a text file in the repository and will be available on your local machine automatically once you clone the pyQuARC repository. Before installing the requirements, make sure you are in your working directory and navigate to the pyQuARC folder.

Navigate to your directory:
* `cd`

Navigate to the pyQuARC folder:
* `cd pyQuARC`

Install the requirements:
* `pip install -r requirements.txt`

You are almost there! Open your code editor (e.g., VS Code), navigate to the location where you cloned the repository, select the pyQuARC folder, and click Open. You should now be able to see all the existing files and contents of the pyQuARC folder in your code editor. Voilà! You are ready to use pyQuARC!

## pyQuARC Architecture
![pyQuARC Architecture](/images/architecture.png)

pyQuARC uses a Downloader to obtain a copy of a metadata record of interest from the CMR API. This is accomplished using a [CMR API query,](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html) where the metadata record of interest is identified by its unique identifier in the CMR (concept_id). For more, please visi the [CMR API documentation](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html).

After cloning the repository, you can find a set of files in the `schemas` folder including `checks.json`, `rule_mapping.json`, and `check_messages.json` that define and apply the rules used to evaluate metadata. Each rule is specified by its `rule_id`, associated function, and any dependencies on specific metadata elements. 

* The `checks.json` file contains a comprehensive list of all metadata quality rules used by pyQuARC. Each rule in this file includes a `check_function` that specifies the name of the check.
* The `check_messages.json` file contains the messages that are displayed when a check fails. You can use the `check_function` name from the `checks.json` file to locate the output message associated with each check.
* The `rule_mapping.json` file specifies which metadata element(s) each rule applies to.

Furthermore, the `rule_mapping.json` file specifies the severity level associated with a failure. If a check fails, it is assigned one of three categories: ❌ Error, ⚠️ Warning, or ℹ️ Info. These categories correspond to priority levels in [ARC’s priority matrix](https://wiki.earthdata.nasa.gov/display/CMR/ARC+Priority+Matrix) and indicate the importance of the failed check. Default severity values are based on ARC’s metadata quality assessment framework but can be customized to meet individual needs.

❌ Error → most critical issues
⚠️ Warning → medium-priority issues
ℹ️ Info → minor issues

In the `code` folder, you will find a series of Python files containing the implementations for each check. For example, the `data_format_gcmd_check` listed in the `checks.json` file can be found in the `string_validator.py` file, where the code performs the check using a string validator.

## Run pyQuARC on a Single Record

### Locating the Concept ID
To run pyQuARC on a single record, either at the collection (data product) level or the granule (individual file) level, you will need the associated Concept ID. If you don’t know the Concept ID for the record, you can find it by following these steps:

1. Go to NASA [Earthdata Search](https://search.earthdata.nasa.gov/) and locate the data product of interest.
2. Click Collection Details and locate the dataset’s Short Name, which is often highlighted in gray along with the Version number (for example: Short Name = Aqua_AIRS_MODIS1km_IND, Version = 1).
3. Copy the Short Name and Version number, then modify the following path:

* `https://cmr.earthdata.nasa.gov/search/collections.umm-json?entry_id=SHORTNAME_VERSION#.2&all_revisions=true`

You will need to replace `SHORTNAME` in the path with the actual Short Name of the dataset (for example: Aqua_AIRS_MODIS1km_IND).
You will also need to replace `VERSION#` in the path with the actual Version number listed under Collection Details in Earthdata Search (for example: 1).

For the dataset “Aqua AIRS-MODIS 1-km Matchup Indexes V1 (Aqua_AIRS_MODIS1km_IND) at GES_DISC” with Short Name Aqua_AIRS_MODIS1km_IND and Version 1, the path is modified as follows:

* `https://cmr.earthdata.nasa.gov/search/collections.umm-json?entry_id=Aqua_AIRS_MODIS1km_IND_1&all_revisions=true`

You should now be able to find the `concept-id` for that collection (data product).

For individual files (granules), locating the Concept ID is straightforward. In [Earthdata Search](https://search.earthdata.nasa.gov/), find the file of interest, click View Details, and then check the Information tab to see the Concept ID.

### Running pyQuARC Using the Concept ID
Now that you have identified the Concept ID for the collection (data product) or granule (individual file) metadata, you can use the following command in your code editor to curate it:

* `python pyQuARC/main.py --concept_ids CONCEPT_ID --format FORMAT`

`CONCEPT_ID` should be replaced with the Concept ID of the collection or granule-level metadata (for example: `C2515837343-GES_DISC`).  
`FORMAT` should be replaced with the schema you are using to validate the metadata. This will differ depending on whether you are curating collection- or granule-level metadata. The list of acceptable formats is as follows:  

- `umm-c` (for collection)  
- `umm-g` (for granule)  
- `echo-c` (for collection)  
- `echo-g` (for granule)  
- `dif10` (for both collection and granule)  

**Example**
For `C2515837343-GES_DISC`, the command above can be modified as follows:

`python pyQuARC/main.py --concept_ids C2515837343-GES_DISC --format umm-c`

In this example, `CONCEPT_ID` has been replaced with `C2515837343-GES_DISC`, and `FORMAT` has been replaced with `umm-c`

### Running pyQuARC on a Local File
There is also the option to select and run pyQuARC on a metadata record already downloaded to your local desktop.

**Run `main.py`:**

```plaintext
▶ python pyQuARC/main.py -h  
usage: main.py [-h] [--query QUERY | --concept_ids CONCEPT_IDS [CONCEPT_IDS ...]] [--file FILE | --fake FAKE] [--format [FORMAT]] [--cmr_host [CMR_HOST]]
               [--version [VERSION]]

optional arguments:
  -h, --help                Show this help message and exit
  --query QUERY             CMR query URL.
  --concept_ids CONCEPT_IDS [CONCEPT_IDS ...]
                            List of concept IDs.
  --file FILE               Path to the test file, either absolute or relative to the root dir.
  --fake FAKE               Use a fake content for testing.
  --format [FORMAT]         The metadata format. Choices are: echo-c (echo10 collection), echo-g (echo10 granule), dif10 (dif10 collection), umm-c (umm-json collection),
                        umm-g (umm-json granules)
  --cmr_host [CMR_HOST]     The cmr host base url. Default is: https://cmr.earthdata.nasa.gov
  --version [VERSION]       The revision version of the collection. Default is the latest version.

```
To test a local file, use the `--file` argument. Give it either an absolute file path or a file path relative to the project root directory.

Example:
```
▶ python pyQuARC/main.py --file "tests/fixtures/test_cmr_metadata.echo10"
```
or
```
▶ python pyQuARC/main.py --file "/Users/batman/projects/pyQuARC/tests/fixtures/test_cmr_metadata.echo10"
```

## Run pyQuARC on Multiple Records
pyQuARC has the capability to run metadata checks on multiple collection or granule IDs. This feature allows users to perform validation checks on multiple records simultaneously. When performing validation checks on multiple records, it is essential that all records share the same schema format, which could be one of the following: `umm-c`, `umm-g`, `echo-c`, `echo-g`, and `dif10`.

To run pyQuARC on multiple records, use one of the following options/commands:

A. List the collection IDs consecutively, separated by commas. The results will be displayed in the console.

`python pyQuARC/main.py --concept_ids <id1>, <id2>, <id3>, …. --format umm-c`

B. If you have multiple collection IDs (e.g., more than 10 records), it is recommended to create a text file listing the collection IDs. The format of the records should be:

<id1>
<id2>
<id3>
……
<id10>

`python pyQuARC/main.py --concept_ids $(cat pyQuARC/files.txt) --format umm-c`

C. If you prefer to save the output from multiple records to a `.csv` file for reference, use the following command. Note that the output format may not be perfectly structured due to the default settings used when writing output from the Python console.

`python pyQuARC/main.py --concept_ids <id1>, <id2>, <id3>, …. --format umm-c > pyquarc_output.csv`

## Customization
pyQuARC is designed to be customizable. Output messages can be modified using the `messages_override.json` file - any messages added to `messages_override.json` will display over the default messages in the `message.json` file. Similarly, there is a `rule_mapping_override.json` file which can be used to override the default settings for which rules/checks are applied to which metadata elements. There is also the opportunity for more sophisticated customization. New QA rules can be added and existing QA rules can be edited or removed. Support for new metadata standards can be added as well.

### Adding a custom rule
To add a custom rule, follow the following steps:

**Add an entry to the `schemas/rule_mapping.json` file in the form:**

```json
"rule_id": "<An id for the rule in snake case>": {
    "rule_name": "<Name of the Rule>",  
    "fields_to_apply": {
        "<metadata format (eg. echo-c)>": {  
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
                    "<any dependent check that needs to be run before this check (if any), for this specific metadata format>",
                    "<field to apply this dependent check to (if any)>"
                ]
            ]
        },
        "echo-g": {  
            "fields": [  
                "<The primary field2 to apply to (full path separated by /)>",
                "<Related field 21>",
                "<Related field 22>",
                "<Related field ...>",
                "<Related field 2n>",  
            ],
            "relation": "relation_between_the_fields_if_any",
            "data": [ "<any external data that you want to send to the rule for this specific metadata format>" ]
        }  
    },
    "data" : [ "<any external data that you want to send to the rule>" ],
    "check_id": "< one of the available checks, see CHECKS.md, or custom check if you are a developer>"
}  
```

An example:

```json
"data_update_time_logic_check": {
    "rule_name": "Data Update Time Logic Check",
    "fields_to_apply": {
        "echo-c": [
            {
                "fields": [
                    "Collection/LastUpdate",
                    "Collection/InsertTime"
                ],
                "relation": "gte"
            }
        ],
        "echo-g": [
            {
                "fields": [
                    "Granule/LastUpdate",
                    "Granule/InsertTime"
                ],
                "relation": "gte"
            }
        ],
        "dif10": [
            {
                "fields": [
                    "DIF/Metadata_Dates/Data_Last_Revision",
                    "DIF/Metadata_Dates/Data_Creation"
                ],
                "relation": "gte",
                "dependencies": [
                    [
                        "date_or_datetime_format_check"
                    ]
                ]
            }
        ]
    },
    "severity": "info",
    "check_id": "datetime_compare"
},
```

`data` is any external data that you want to pass to the check. For example, for a `controlled_keywords_check`, it would be the controlled keywords list:

```json
"data": [ ["keyword1", "keyword2"] ]
```

`check_id` is the id of the corresponding check from `checks.json`. It'll usually be one of the available checks. An exhaustive list of all the available checks can be found in [CHECKS.md](./CHECKS.md).

**If you're writing your own custom check to `schemas/checks.json`:**

Add an entry in the format:

```json
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

```json
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

```json
{  
	"valid": <the_validity_based_on_the_check>,  
	"value": <the_value_of_the_field_in_user_friendly_format>  
}
```

You can re-use any functions that are already there to reduce redundancy.

**Adding output messages to checks**:

Add an entry to the `schemas/check_messages_override.json` file like this:

```json
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

```json
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

```python
@staticfunction
def is_true(value1, value2):
	return {
		"valid": value1 and value2,
		"value": [value1, value2]
	}
```

And a message:

```json
...
	"failure": "The values `{}` and `{}` do not amount to a true value",
...
```
Then, if the check function receives input `value1=0` and `value2=1`, the output message will be:

```plaintext
The values 0 and 1 do not amount to a true value
```

### Using as a package
*Note:* This program requires `Python 3.8` installed in your system.

**Clone the repo:** [https://github.com/NASA-IMPACT/pyQuARC/](https://github.com/NASA-IMPACT/pyQuARC/)

**Go to the project directory:** `cd pyQuARC`

**Install package:** `python setup.py install`

**To check if the package was installed correctly:**

```python
▶ python
>>> from pyQuARC import ARC
>>> validator = ARC(fake=True)
>>> validator.validate()
>>> ...
```

**To provide locally installed file:**

```python
▶ python
>>> from pyQuARC import ARC
>>> validator = ARC(file_path="<path to metadata file>")
>>> validator.validate()
>>> ...
```

**To provide rules for new fields or override:**

```python
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

```python
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

## pyQuARC as a Service (QuARC)
QuARC is pyQuARC deployed as a service and can be found here: https://quarc.nasa-impact.net/docs/.

QuARC is still in beta but is regularly synced with the latest version of pyQuARC on GitHub. Fully cloud-native, the architecture diagram of QuARC is shown below:

![QuARC](https://user-images.githubusercontent.com/17416300/179866276-7c025699-01a1-4d3e-93cd-50e12c5a5ec2.png)

## Have a question?
If you have any questions, please contact us at **earthdata-support@nasa.gov**.
