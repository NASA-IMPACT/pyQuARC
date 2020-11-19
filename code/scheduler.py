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

    def rule(self, check_id):
        for rule in self.rule_mapping:
            if rule["rule_id"] == check_id:
                return rule

    @staticmethod
    def append_if_not_exist(value, list_of_values):
        """
        Appends `value` if it doesn't exist in `list_of_values`
        `list_of_values` is an ordered list
        """
        if value not in list_of_values:
            list_of_values.append(value)

    def _add_to_list(self, rule, rules_list):
        """
        Adds `rule` to `rules_list` based on the dependency order
        """
        check_id = rule.get("check_id") or rule.get("rule_id")
        if check := self.check_list.get(check_id):
            dependencies = check.get("dependencies", [])
            for dependency in dependencies:
                self._add_to_list(self.rule(dependency), rules_list)
        
            Scheduler.append_if_not_exist(rule["rule_id"], rules_list)
        else:
            print(f"Missing entry for {rule.check_id} in `checks.json`")

    def order_rules(self):
        """
        Creates a rule ordering based on the dependencies

        Returns:
            (list): ordered list of rules
        """
        ordered_check_list = []

        for rule in self.rule_mapping:
            # identity = rule.get("check_id") or rule["rule_id"]
            self._add_to_list(rule, ordered_check_list)

        return ordered_check_list
