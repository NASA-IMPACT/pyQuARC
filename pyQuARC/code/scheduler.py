class Scheduler:
    """
    Schedules the rules based on the applicable ordering
    """

    def __init__(self, rule_mapping, rules_override, checks, checks_override, metadata_format):
        self.check_list = {**checks, **checks_override}
        self.rule_mapping = {**rule_mapping, **rules_override}
        self.metadata_format = metadata_format

    @staticmethod
    def append_if_not_exist(value, list_of_values):
        """
        Appends `value` if it doesn't exist in `list_of_values`
        `list_of_values` is an ordered list
        """
        if value not in list_of_values:
            list_of_values.append(value)

    def get_all_dependencies(self, rule, check, field_dict=None):
        """
        Gets all the dependencies for a rule

        If field_dict is provided, get the dependencies only for that field
        """
        dependencies = []
        dependencies_from_fields = []

        if field_dict:
            if dependencies_from_fields := field_dict.get("dependencies"):
                return dependencies_from_fields
            else:
                return check.get("dependencies", [])

        if field_objects := rule.get("fields_to_apply").get(self.metadata_format):
            for field_object in field_objects:
                if field_dependencies := field_object.get("dependencies"):
                    dependencies_from_fields.extend(field_dependencies)

        dependencies.extend(dependencies_from_fields)

        dependencies_from_checks = check.get("dependencies", [])
        dependencies.extend(dependencies_from_checks)
        return dependencies

    def dependencies_ordering(self, dependencies, list):
        """
        Creates a dependency ordering; basically independent checks are added first
        """
        for dependency in dependencies:
            dependency_check = self.check_list.get(dependency[0])
            if dependency_check.get("dependencies"):
                self.dependencies_ordering(
                    dependency_check.get("dependencies"), list
                )
            Scheduler.append_if_not_exist(dependency[0], list)
            
    def _find_rule_ids_based_on_check_id(self, check_id):
        """
        Returns all the rule_ids that are based on a check_id

        Args:
            check_id (str): The check id to find the rules based on

        Returns:
            list: list of all the rule_ids that are based on the check_id
        """
        return [
            rule_id for rule_id, rule in self.rule_mapping.items() if (rule.get("check_id") == check_id) or (rule_id == check_id)
        ]

    def order_rules(self):
        """
        Creates a rule ordering based on the dependencies

        Returns:
            (list): ordered list of rules
        """
        ordered_rules = []
        ordered_check_list = []

        for rule_id, rule in self.rule_mapping.items():
            check_id = rule.get("check_id") or rule_id
            if check := self.check_list.get(check_id):
                dependencies = self.get_all_dependencies(rule, check)
                # First add dependencies and their dependencies and so on
                self.dependencies_ordering(dependencies, ordered_check_list)
                # Then add self
                Scheduler.append_if_not_exist(check_id, ordered_check_list)
            else:
                print(f"Missing entry for {check_id} in `checks.json`")

        for dependency in ordered_check_list:
            ordered_rules.extend(
                self._find_rule_ids_based_on_check_id(dependency)
            )

        return ordered_rules
