# CHANGELOG

## v1.2.2

- Bugfixes:
  - Stray newlines in GCMD keywords
  - Reading xml metadata for fields with attributes didn't get expected output
  - Missing field in rule_mapping
   

## v1.2.1

- Added support for automated regression testing
- Revised output messages

## v1.2.0

- Added support for ECHO10 Granule, UMM-G (UMM-JSON Granule) and UMM-C (UMM-JSON Collection) metadata
- Added support for custom CMR host
- Added support for some UMM fields that look like the following:

    ```json
    "ContactMechanisms": [
        {
            "Type": "Telephone",
            "Value": "605-594-6116"
        },
        {
            "Type": "U.S. toll free",
            "Value": "866-573-3222"
        },
        {
            "Type": "Email",
            "Value": "lpdaac@usgs.gov"
        }
    ]
    ```

    To specify the "Email" field, in the `rule_mapping`, a user would put in `ContactMechanisms/Value?Type=Email` as the field.
- All the field specified in a datetime check that involves comparison should have a corresponding `datetime_format_check` entry, otherwise the check won't run
- Added support for `data` specific to format type. This will take precedence over the generic `data`. Example:

    ```json
    "get_data_url_check": {
        "rule_name": "GET DATA URL check",
        "fields_to_apply": {
            "dif10": [
                {
                    "fields": [
                        "DIF/Related_URL"
                    ],
                    "data": [
                        ["URL_Content_Type", "Type"]
                    ]
                }
            ],
            "umm-json": [
                {
                    "fields": [
                        "RelatedUrls"
                    ]
                }
            ]
        },
        "data": [
            ["Type"]
        ],
        "severity": "error",
        "check_id": "get_data_url_check"
    },
    ```

- Prioritized field dependencies to check dependencies (dependencies from fields take precedence over dependencies from data)
- Added collection `version` to collection datetime validation with granules for accuracy
- Allowed DIF10 datetime fields to support ISO Date (not just ISO Datetime)
- Generalized and renamed `datetime_compare` check to `date_compare`
- Updated auto GCMD keywords downloader to use the new GCMD url
- Addded `pyquarc_errors` to the response, which will contain any errors that were thrown as exceptions during validation
- Added checks that validate granule fields against the corresponding collection fields


### List of added  and updated checks

- GET DATA URL Check
- Data Center Long Name Check
- URL Description Uniqueness Check
- Periodic Duration Unit Check
- Characteristic Name Uniqueness Check UMM
- Range Date Time Logic Check
- Range Date Time Logic Check
- Project Date Time Logic Check
- Project Date Time Logic Check
- Periodic Date Time Logic Check
- Datetime ISO Format Check
- URL Health and Status Check
- Delete Time Check
- DOI Missing Reason Enumeration Check
- Processing Level Description Length Check
- UMM Controlled Collection State List
- Ends at present flag logic check
- Ends at present flag presence check
- Data Contact Role Enumeration Check
- Controlled Contact Role Check
- Characteristic Description Length Check
- Organization Longname GCMD Check
- Instrument Short/Longname Consistency Check
- Instrument Shortname GCMD Check
- Instrument Long Name Check
- Platform Shortname GCMD Check
- Data Format GCMD Check
- Platform Longname GCMD Check
- Platform Type GCMD Check
- Campaign Short/Long name consistency Check
- Campaign Short Name GCMD Check
- Campaign Long Name GCMD Check
- Collection Data Type Enumeration Check
- Bounding Coordinates Logic Check
- Vertical Spatial Domain Type Check
- Spatial Coverage Type Check
- Campaign Name Presence Check
- Spatial Extent Requirement Fulfillment Check
- Collection Progress Related Fields Consistency Check
- Online Resource Type GCMD Check
- Characteristic Name Uniqueness Check
- Ending Datetime validation against granules
- Beginning Datetime validation against granules
- ISO Topic Category Vocabulary Check
- Temporal Extent Requirement Check
- FTP Protocol Check
- Citation Version Check
- Default Date Check
- Online Description Presence Check
- IDN Node Shortname GCMD Check
- Chrono Unit GCMD Check
- Platform Type Presence Check
- Horizontal Data Resolution Unit Controlled Vocabulary Check
- Sensor number check
- Data Center Shortname GCMD Check
- Characteristics Data Type Presence Check
- Platform Type Presence Check
- Platform Longname Presence Check
- Granule Platform Short Name Check
- Horizontal Data Resolution Unit Controlled Vocabulary Check
- Periodic Duration Unit Check
- URL Description Uniqueness Check
- Online Resource Description Uniqueness Check
- Online Access Description Uniqueness Check
- Metadata Update Time Logic Check
- Granule Single Date Time Check
- Granule Project Short Name Check
- Granule Sensor Short Name Check
- Validate Granule Data Format Against Collection Check
- Granule Data Format Presence Check


## v1.1.5

- Added reader for specific columns from GCMD csvs
- Fixed bug to handle cases when there are multiple entries for same shortname but the first entry has missing long name

## v1.1.4

- Added error handling for errored checks
- Fixed minor bugs

## v1.1.3

- Fixed null pointer exception in the check `collection_progress_consistency_check`

## v1.1.2

- Removed stdout when importing pyQuARC package

## v1.1.1

- Included addition of `version.txt` in the package build

## v1.1.0

- Support for [DIF10](https://earthdata.nasa.gov/esdis/eso/standards-and-references/directory-interchange-format-dif-standard) collection level metadata
- Added new checks and rules listed in the following section
- Restructured the schema files for ease of new rule addition
  - Users will now be able to deal with just the `rule_mapping.json` file without having to mess with `checks.json`
- Added documentation for all available checks, available at [CHECKS.md](./CHECKS.md)

### List of added checks

- `opendap_url_location_check`
- `user_services_check`
- `doi_missing_reason_explanation`
- `boolean_check`
- `collection_progress_consistency_check`
- `online_resource_type_gcmd_check`
- `characteristic_name_uniqueness_check`
- `validate_ending_datetime_against_granules`
- `validate_beginning_datetime_against_granules`
- `get_data_url_check`

### List of added rules

- `altitude_unit_check`
- `campaign_name_presence_check`
- `spatial_coverage_type_presence_check`
- `horizontal_datum_name_check`
- `online_access_url_presence_check`
- `online_resource_url_presence_check`
- `online_access_url_description_check`
- `online_resource_url_description_check`
- `opendap_url_location_check`
- `location_keyword_presence_check`
- `spatial_extent_requirement_fulfillment_check`
- `license_information_check`
- `collection_citation_presence_check`
- `user_services_check`
- `doi_missing_reason_explanation`
- `boolean_check`
- `collection_progress_consistency_check`
- `online_resource_type_gcmd_check`
- `online_resource_type_presence_check`
- `characteristic_name_uniqueness_check`
- `validate_ending_datetime_against_granules`
- `validate_beginning_datetime_against_granules`
- `future_date_check`
- `iso_topic_category_check`
- `dif10_date_not_provided_check`
- `temporal_extent_requirement_check`
- `ftp_protocol_check`
- `citation_version_check`
- `default_date_check`
- `url_desc_presence_check`
- `get_data_url_check`

## v1.0.0

- Support for **ECHO10** collection level metadata
- Feature to use as a package
- Description and Architecture Diagram in the README document
