class Scheduler:
    """
    Schedules the rules based on the applicable ordering
    """

    def __init__(self, rule_mapping, rules_override, checks, checks_override):
        self.check_list = checks
        self.checks_override = checks_override
        self.rule_mapping = rule_mapping
        self.rules_override = rules_override

    @staticmethod
    def append_if_not_exist(value, list_of_values):
        """
        Appends `value` if it doesn't exist in `list_of_values`
        `list_of_values` is an ordered list
        """
        if value not in list_of_values:
            list_of_values.append(value)

    def _add_to_list(self, rule_id, rule, rules_list):
        """
        Adds `rule` to `rules_list` based on the dependency order
        """
        check_id = rule.get("check_id") or rule_id
        if check := self.checks_override.get(
            check_id
        ) or self.check_list.get(check_id):
            dependencies = check.get("dependencies", [])
            for dependency in dependencies:
                check = self.rules_override.get(
                    dependency[0]
                ) or self.rule_mapping.get(dependency[0])
                self._add_to_list(
                    dependency[0],
                    check,
                    rules_list
                )
            Scheduler.append_if_not_exist(rule_id, rules_list)
        else:
            print(f"Missing entry for {check_id} in `checks.json`")

    def order_rules(self):
        """
        Creates a rule ordering based on the dependencies

        Returns:
            (list): ordered list of rules
        """
        ordered_check_list = []
        keys = list(self.rule_mapping.keys())
        keys += list(self.rules_override.keys())
        for rule_id in set(keys):
            rule = self.rules_override.get(
                rule_id
            ) or self.rule_mapping.get(rule_id)
            self._add_to_list(rule_id, rule, ordered_check_list)

        return ordered_check_list
