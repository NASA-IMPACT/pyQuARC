# CHANGELOG

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
