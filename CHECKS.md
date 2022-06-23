# Adding a new check

**Files that you need to work with:**

1. `rules_override.json`
2. `check_messages_override.json`

**Steps:**

1. Create a unique rule_id for your rule. Make it meaningful. Something like `doi_missing_reason_explanation` (no spaces).
2. Make an entry to the json files with the same rule_id.
3. In `rules_override.json`, add in the `fields_to_apply`, `data` and `check_id`. Add in the `echo10` and `dif10` fields corresponding to the rule. `check_id` should be one of the available `check_id`s (listed below). The format of `data` corresponding to each of these `check_id`s are given in the specifications below.

## Available checks

### Generic checks

#### `date_compare`

Compares the given two dates based on the relationship specified.
Relationship supported: `lt`, `lte`, `gt`, `gte`, `eq` and `neq`.

##### Case I: Compare two different datetime field values

  Specify the two field in `fields` and the corresponding `relation`.

##### Case II: Compare a field with a specific date

  Specify the field in `fields`. Add the date and relation in `data` in the format `[{time}, {relation}]`. eg: `["now", "gte"]`
  Currently only `now` is supported as a date

#### `datetime_format_check`

Checks whether the datetime is in the ISO format.

#### `url_check`

Checks if the url is correct, resolves to a webpage and gives a 200 OK status.

#### `string_compare`

Compares the two strings based on the relationship specified.
Relationship supported: `lt`, `lte`, `gt`, `gte`, `eq` and `neq`.

##### Case I: Compare two different string field values

  Specify the two field in `fields` and the corresponding `relation`.

##### Case II: Compare a field with a specific string

  Specify the field in `fields`. Add the date and relation in `data` in the format `[{string}, {relation}]`. eg: `["FTP", "eq"]`

#### `length_check`

Checks if the legth of the field value adheres to the relationship specified.
`data format`: `[{length}, {relation}]`. eg: `[100, "gte"]`.

#### `availability_check`

Checks the rule: if the first field is provided, the second field has to be provided.
`fields: (ordered) [ {first_field}, {second_field} ]`

#### `boolean_check`

Checks if the field value is boolean, either `true` or `false` or any case combination of those.

#### `controlled_keywords_check`

Checks if the field value is one of the controlled keywords; provide the controlled keywords as `data` in the format:
`[["keyword1", "keyword2",...]]`

#### `doi_validity_check`

Checks if the doi provided resolves to a valid document.

#### `one_item_presence_check`

Checks if one of the given fields is populated.

### Miscellaneous Checks

#### `bounding_coordinate_logic_check`

Check that the North bounding coordinate is always larger than the South bounding coordinate and the East bounding coordinate is always larger than the West bounding coordinate.
`fields`: the parent field 
(eg. `Collection/Spatial/HorizontalSpatialDomain/Geometry/BoundingRectangle`)

#### `characteristic_name_uniqueness_check`

If multiple Charasteristics are provided, checks to see whether each of those names are unique.

#### `collection_progress_consistency_check`

There are a few fields pertaining to the status of the collection as either active or complete whose values should align with one another. This check looks across these related fields to make sure the values are logically consistent.

For `ACTIVE` collections:
`CollectionProgress = ACTIVE`
No `EndingDateTime` should be provided
`EndsAtPresentFlag` = `true`

For `COMPLETE` collections:
`CollectionProgress = COMPLETE`
An `EndingDateTime` should be provided
`EndsAtPresentFlag` = `false` OR no `EndsAtPresentFlag` provided 

#### `doi_link_update`

If `http://dx.doi.org` is provided, recommend updating it to `https://doi.org`

#### `doi_missing_reason_explanation`

If no DOI is provided, and the `DOI/MissingReason` field is populated, recommend adding an explanation for why there is no DOI.

#### `ends_at_present_flag_logic_check`

Checks the logic as follows:
If `EndsAtPresentFlag` is populated:
`true` -> check `EndingDateTime`, if there is no ending date time passes check; if there is an `EndingDateTime` display a warning
`true` -> check `CollectionState/CollectionProgress`, if `CollectionState/CollectionProgress = ACTIVE` passes check; if `CollectionState/CollectionProgress = COMPLETE` display a warning
`false` -> check `EndingDateTime`, if there is an ending date time passes check; if there is not an `EndingDateTime` display a warning
`false` -> check `CollectionState/CollectionProgress`, if `CollectionState/CollectionProgress = COMPLETE` passes check; if `CollectionState/CollectionProgress = ACTIVE` display a warning

#### `ends_at_present_flag_presence_check`

If `EndsAtPresentFlag` is not populated:
If no `EndingDateTime` is provided, print a warning that it might be necessary to add an `EndsAtPresentFlag` of `true`
If an `EndingDateTime` is provided, passes check (no message needed)
If `CollectionState` = `ACTIVE`, print a warning that it might be necessary to add an `EndsAtPresentFlag` of `true`
If `CollectionState` = `COMPLETE`, passes check (no message needed)

#### `get_data_url_check`

Checks for `"GET DATA"` links (at least 1 should be provided). If no GET DATA links are provided this check will throw an error.

#### `mime_type_check`

Checks whether a `Mime Type` is provided for `'USE SERVICE API'` URLs (i.e. when the `URL Type` = `'USE SERVICE API'`).

#### `opendap_url_location_check`

Check to make sure that an OPeNDAP access URL is not provided in the `Online Access URL` field.

#### `user_services_check`

Check to make sure the fields aren't populated like this:

```
Collection/Contacts/Contact/ContactPersons/ContactPerson/FirstName: "User"
Collection/Contacts/Contact/ContactPersons/ContactPerson/MiddleName: "null"
Collection/Contacts/Contact/ContactPersons/ContactPerson/LastName: "Services"
```

#### `validate_beginning_datetime_against_granules`

Checks whether the beginning date time matches the beginning date time of the first granule in the collection (if granules exist.)

#### `validate_ending_datetime_against_granules`

Checks whether the ending date time matches the ending date time of the last granule in the collection (if granules exist.)

### GCMD Checks

#### `science_keywords_gcmd_check`

Check to determine if the provided science keyword matches a value from the GCMD controlled vocabulary list.

#### `spatial_keyword_gcmd_check`

Check to determine if the provided spatial keyword matches a value from the GCMD controlled vocabulary list.

#### `platform_long_name_gcmd_check`

Check to determine if the provided long name matches a value from the platform GCMD controlled vocabulary list.

#### `platform_short_name_gcmd_check`

Check to determine if the provided short name matches a value from the platform GCMD controlled vocabulary list.

#### `platform_type_gcmd_check`

Check to determine if the provided platform type matches a value from the GCMD controlled vocabulary list.

#### `instrument_long_name_gcmd_check`

Check to determine if the provided long name matches a value from the GCMD controlled vocabulary list.

#### `instrument_short_name_gcmd_check`

Check to determine if the provided short name matches a value from the GCMD controlled vocabulary list.

#### `instrument_short_long_name_consistency_check`

Checks if the provided instrument short name and long name are consistent across the GCMD keywords list.

#### `campaign_long_name_gcmd_check`

Checks whether the value adheres to GCMD, specifically the project list long name column.

#### `campaign_short_name_gcmd_check`

Checks whether the value adheres to GCMD, specifically the project list short name column.

#### `campaign_short_long_name_consistency_check`

Checks whether the campaign  (project) short name and long name GCMD keywords are consistent: basically that they belong to the same row.

#### `organization_short_name_gcmd_check`

Checks whether the value adheres to GCMD, specifically the provider list short name column.

#### `data_format_gcmd_check`

Checks whether the value adheres to GCMD, specifically the data format short name/long name column.

#### `online_resource_type_gcmd_check`

Check that the `Online Resource Type` is included in the `rucontenttype` GCMD list under the `Type` or `Subtype` column.
