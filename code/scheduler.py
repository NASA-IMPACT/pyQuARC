import json


class Scheduler:
    """
    Schedules the rules based on the applicable ordering
    """

    def __init__(self, rule_mapping):
        self.check_list = json.loads(
            open("schemas/checks.json", "r").read()
        )
        self.rule_mapping = rule_mapping

    @staticmethod
    def append_if_not_exist(value, list_of_values):
        """
        Appends `value` if it doesn't exist in `list_of_values`
        `list_of_values` is an ordered list
        """
        if value not in list_of_values:
            list_of_values.append(value)

    def _add_to_list(self, rule_id, rules_list):
        """
        Adds `rule_id` to `rules_list` based on the dependency order
        """
        dependencies = self.check_list[rule_id].get("dependencies", [])
        for dependency in dependencies:
            self._add_to_list(dependency, rules_list)
    
        Scheduler.append_if_not_exist(rule_id, rules_list)

    def order_rules(self):
        """
        Creates a rule ordering based on the dependencies

        Returns:
            (list): ordered list of rules
        """
        ordered_check_list = []

        for rule in self.rule_mapping:
            self._add_to_list(rule["rule_id"], ordered_check_list)

        return ordered_check_list
