import json


class Scheduler:
    def __init__(self, rule_mapping):
        self.check_list = json.loads(
            open("schemas/checks.json", "r").read()
            )
        self.rule_mapping = rule_mapping

    @staticmethod
    def add_to_list(arg, the_list):
        if arg not in the_list:
            the_list.append(arg)

    def order_rules(self):
        ordered_check_list = []

        for rule in self.rule_mapping:
            dependencies = self.check_list\
                               .get(rule["rule_id"])\
                               .get("dependencies")
            if dependencies:
                for dependency in dependencies:
                    Scheduler.add_to_list(dependency, ordered_check_list)

            Scheduler.add_to_list(rule["rule_id"], ordered_check_list)

        return ordered_check_list
