import json
import re
import requests

from .constants import SCHEMA_PATHS


class CustomChecker:
    """
    Class to implement custom checks
    """

    def __init__(self, rules_mapping, checks):
        """
        Args:
            content_to_validate (str): JSON string containing downloaded metadata
        """
        self.checks = checks
        self.rules_mapping = rules_mapping

    def _get_rule(self, identifier):
        """
        Extracts the rule from the ruleset based on its identifier

        Args:
            identifier (str): The identifier of the rule
            ruleset (list of dict): The ruleset that contains all the rules and their details

        Returns:
            (dict) The target rule and its details

        Raises:
            KeyError: When the identifier doesn't exist in the ruleset
        """

        return self.id_to_rule_mapping[identifier]


    @staticmethod    
    def _get_path_value_recursively(subset_of_metadata_content, path, container):
        """
        Gets the path values recursively while handling list or dictionary in `subset_of_metadata_content`
        Adds the values to `container`

        Args:
            subset_of_metadata_content (dict or list or str): 
                        The value of the field at a certain point;
                        changes during each level of recursion
            path (list): The path of the field as a list
                         Example: 'Collection/RangeDateTime/StartDate' ->
                                  ['Collection', 'RangeDateTime', 'StartDate']
            container (set): The container that holds all the path values
        """

        try:
            root_content = subset_of_metadata_content[path[0]]
        except KeyError as e:
            return
        new_path = path[1:]
        if isinstance(root_content, str) or isinstance(root_content, int):
            container.add(root_content)
        elif isinstance(root_content, list):
            for each in root_content:
                try:
                    CustomChecker._get_path_value_recursively(each, new_path, container)
                except KeyError as e:
                    continue
        elif isinstance(root_content, dict):
            CustomChecker._get_path_value_recursively(root_content, new_path, container)

    @staticmethod
    def _get_path_value(content_to_validate, path):
        """
        Gets the value of the field from the metadata (input_json)

        Args:
            path (str): The path of the field. Example: 'Collection/RangeDateTime/StartDate'

        Returns:
            (bool, set) If the path exists, (True, set of values of the path);
                        else (False, empty set)
        """

        container = set()

        path = path.split('/')
        CustomChecker._get_path_value_recursively(content_to_validate, path, container)
        # TODO: Handle cases where there are multiple values for the field
        return container

    @staticmethod
    def _result_dict(result, rule):
        """
        Creates an output dictionary based on the result of a check

        Args:
            result (dict): Result dict from a check function
            rule (dict): The metadata of the rule that was applied to get the result

        Returns:
            (dict) Output dictionary
        """

        result_dict = {}

        if result["valid"] == None:
            result_dict["error"] = "Check function not implemented"
            return result_dict

        # if any one instance fails the rule, the rule as a whole needs to fail the check
        # a flag to determine if all instances have passed
        all_instances_pass = True
        for item in result["instances"]:
            if item["valid"]:
                all_instances_pass = False
                break

        if not all_instances_pass:
            result_dict["check_passes"] = False

            # put path_value in message-fail string
            fail_message = re.sub(
                r"\{.*\}",
                str(result["instances"]),
                rule["message-fail"]
            )

            # replace \n, \t with space
            result_dict["message"] = " ".join(fail_message.split())

            result_dict["help_url"] = rule["help_url"]
            result_dict["severity"] = rule["severity"]
            result_dict["instances"] = result["instances"]
        elif result["valid"] is None:
            result_dict["error"] = "Check function not implemented"
        else:
            result_dict["check_passes"] = True

        return result_dict

    def run(self, content_to_validate, field, func):
        """
            Runs all relevant checks on the given path

            Returns:
                (dict) Result of the checks
        """

        # TODO: where do we check if the data is empty?

        results = {}

        for mapping in self.rules_mapping:
            path = mapping["path"]

            # do nothing for paths that have no custom checks
            if not mapping["rules"]:
                continue

            path_values = self._get_path_value(path)
            path_exists = bool(path_values)

            # if the path referenced in the rule is not in the data
            # TODO: Required field checking can be done here
            if not path_exists:
                # TODO: maybe set exists = False
                continue

            results[path] = {}

            # apply rules to the data
            for rule in mapping["rules"]:
                rule_id = rule["id"]

                results[path][rule_id] = {}

                res = {}
                res["instances"] = []
                res["valid"] = True

                try:
                    for path_value in path_values:
                        result = self.DISPATCHER[rule_id](
                            path_value, rule["data"])
                        res["instances"].append(result)
                except KeyError:  # rule function not implemented
                    res["valid"] = None

                rule_metadata = self._get_rule(rule_id)

                results[path][rule_id] = self._result_dict(
                    res,
                    rule_metadata
                )

        return results

    def run_v2(self, content_to_validate, field, func):
        fields = field["fields"]
        field_values = []
        relation = field.get("relation")
        result = {
            "valid": None
        }
        # TODO: refactor
        if len(fields) == 1:
            values = CustomChecker._get_path_value(content_to_validate, fields[0])
            if values:
                field_values.append(
                    list(values)[0]
                )
        else:
            for _field in fields:
                values = CustomChecker._get_path_value(content_to_validate, _field)
                if values:
                    field_values.append(
                        list(values)[0]
                    )
        if field_values:
            result = func(*field_values, relation)
        return result