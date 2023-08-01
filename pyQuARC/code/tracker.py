class Tracker:
    """
    Tracks the status of each check
    """

    def __init__(self, rule_mapping, rules_override, metadata_format):
        """
        Args:
            rule_mapping (dict): The mapping from rule to fields
            rules_override (dict): The override of mapping from rule to fields
            metadata_format (str): The format of the metadata file (eg. echo10, dif10)
        """
        self.data = Tracker.create_initial_track(
            rule_mapping, rules_override, metadata_format
        )

    @staticmethod
    def create_initial_track(rule_mapping, rules_override, metadata_format):
        """
        Creats an initial tracking data where for each rule, the validity and the applied
        status is False

        Args:
            rule_mapping (dict): The mapping from rule to fields
            rules_override (dict): The override of mapping from rule to fields
            metadata_format (str): The format of the metadata file (eg. echo10, dif10)

        Returns:
            (dict): A dictionary in the form:
            {
                "rule_id": [
                    {
                    "field": "field_name",
                    "valid": "validity_status",
                    "applied": "applied_status"
                    },
                    ...
                ],
                ...
            }
        """
        data = {}
        keys = list(rule_mapping.keys())
        keys += list(rules_override.keys())
        for rule_id in set(keys):
            data[rule_id] = []
            rule = rules_override.get(rule_id) or rule_mapping.get(rule_id)
            for field in rule["fields_to_apply"].get(metadata_format, {}):
                data[rule_id].append(
                    {"field": field["fields"][0], "applied": False, "valid": None}
                )
        return data

    def update_data(self, rule_id, field, validity):
        """
        Updates the tracking value for `rule_id` and `field` with the `validity` status

        Args:
            rule_id (str): The id of the rule
            field (str): The field that the rule is applied to
            validity (bool): The validity status of the rule for the field
        """
        for idx, row in enumerate(self.data[rule_id]):
            if row["field"] == field:
                self.data[rule_id][idx]["valid"] = validity
                self.data[rule_id][idx]["applied"] = True

    def read_data(self, rule_id, field):
        """
        Reads the tracking data for `rule_id` and `field`

        Args:
            rule_id (str): The id of the rule
            field (str): The field path

        Returns:
            (dict): A dict of form: {
                "field": "field_value",
                "valid": "validity_status",
                "applied": "applied_status"
            } for the `rule_id` and `field`
        """
        for row in self.data[rule_id]:
            if row["field"] == field:
                return row
        return {}
