import json
import re
import requests

from datetime import datetime
from urlextract import URLExtract

from .constants import SCHEMA_PATHS
from .relations import mapping as relations_mapping


class Checker:
    """
    Class to implement custom checks
    """

    def __init__(self, content_to_validate):
        """
        Args:
            content_to_validate (str): JSON string containing downloaded metadata
        """

        self.content_to_validate = json.loads(content_to_validate)
        self.ruleset = json.load(open(SCHEMA_PATHS["ruleset"], "r"))
        self.rules_mapping = json.load(
            open(SCHEMA_PATHS["rules_mapping"], "r"))
        self.id_to_rule_mapping = json.load(
            open(SCHEMA_PATHS["id_to_rule_mapping"], "r"))

        self.DISPATCHER = {
            "date_datetime_iso_format_check": self.date_datetime_iso_format_check,
            "data_update_time_logic_check": self.data_update_time_logic_check,
            "url_health_and_status_check": self.url_health_and_status_check,
            "collectiondatatype_enumeration_check": self.collectiondatatype_enumeration_check,
        }

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

    def _get_path_value(self, path):
        """
        Gets the value of the field from the metadata (input_json)

        Args:
            input_json (str): The metadata content
            path (str): The path of the field. Example: 'Collection/RangeDateTime/StartDate'

        Returns:
            (str) The value of the field from the metadata (input_json)
        """

        splits = path.split("/")
        input_json = self.content_to_validate

        try:
            for split in splits:
                input_json = input_json[split.strip()]
        except KeyError as e:
            return False, None
        except TypeError as e:
            # TODO: need another way to parse lists
            print(e, split.strip())
            print(f"_get_path_value failed for {path}")

        return True, input_json

    def _iso_datetime(self, datetime_string):
        """
        Converts the input datetime string to iso datetime object

        Args:
            datetime_string (str): the datetime string

        Returns:
            (datetime.datetime) If the string is valid iso string, False otherwise
        """
        regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
        match_iso8601 = re.compile(regex).match
        try:
            if match_iso8601(datetime_string) is not None:
                if datetime_string.endswith("Z"):
                    datetime_string = datetime_string.replace("Z", "+00:00")
                value = datetime.fromisoformat(datetime_string)
                return value
        except:
            pass
        return False

    def _time_logic_check(self, earlier_datetime_string, later_datetime_string):
        """
            Checks if the earlier datetime comes before later datetime
        """
        # assumes that iso check has already occurred
        earlier_datetime = self._iso_datetime(earlier_datetime_string)
        later_datetime = self._iso_datetime(later_datetime_string)

        return earlier_datetime <= later_datetime

    def date_datetime_iso_format_check(self, path_value, data):
        """
        Performs the Date/DateTime ISO Format Check - checks if the datetime
        is valid ISO formatted datetime string

        Args:
            path_value (str): The datetime string

        Returns:
            (dict) An object with the validity of the check and the instance
        """

        return {
            "valid": bool(self._iso_datetime(path_value)),
            "instance": path_value
        }

    def data_update_time_logic_check(self, path_value, data):
        """
        Checks if the UpdateTime comes chronologically after the InsertTime

        Args:
            value1 (str): The InsertTime datetime string
            value2 (str): The UpdateTime datetime string

        Returns:
            (dict) An object with the validity of the check and the instance
        """

        related_path = data["related_paths"][0]
        _, related_date_value = self._get_path_value(related_path["path"])

        date1 = self._iso_datetime(path_value)
        date2 = self._iso_datetime(related_date_value)

        relation = related_path["relation"]

        # convert "gte", "lte" etc to corresponding functions
        result = relations_mapping[relation](date1, date2)

        return {
            "valid": result,
            "instance": {
                "InsertTime": date1,
                "LastUpdate": date2
            }
        }

    def url_health_and_status_check(self, path_value, data):
        """
        Checks the health and status of the URLs included in the text

        Args:
            text (str): The text where the check needs to be performed

        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        results = []

        # extract URLs from text
        extractor = URLExtract()
        urls = extractor.find_urls(path_value)

        # remove dots at the end
        # remove duplicated urls
        urls = set(url[:-1] if url.endswith(".") else url for url in urls)

        # check that URL returns a valid response
        # TODO: snafu fix for multiple randomurl1.coms
        for url in urls:
            if not url.startswith('http'):
                url = f'http://{url}'
            try:
                response_code = requests.get(url).status_code
                if response_code == 200:
                    continue
                result = {"url": url, "status_code": response_code}
            except requests.ConnectionError as exception:
                result = {"url": url,
                          "error": "The URL does not exist on Internet."}
            except Exception as e:
                result = {"url": url, "error": "Some unknown error occurred."}
            results.append(result)

        if len(results) == 0:
            return {"valid": True}

        return {"valid": False, "instance": results}

    def collectiondatatype_enumeration_check(self, path_value, data):
        """
        Checks if Collection DataType is one of the valid keywords

        Args:
            text (str): The value of the DataType field

        Returns:
            (dict) an object with the validity of the check and the instance/results
        """

        return {"valid": path_value in data["valid_values"], "instance": path_value}

    def _result_dict(self, result, rule):
        """
        Creates an output dictionary based on the result of a check

        Args:
            result (dict): Result dict from a check function
            rule (dict): The metadata of the rule that was applied to get the result

        Returns:
            (dict) Output dictionary
        """

        result_dict = {}

        if result["valid"] == False:
            result_dict["check_passes"] = False

            # put path_value in message-fail string
            fail_message = re.sub(
                r"\{.*\}",
                str(result["instance"]),
                rule["message-fail"]
            )

            # replace \n, \t with space
            result_dict["message"] = "".join(fail_message.split())

            result_dict["help_url"] = rule["help_url"]
            result_dict["severity"] = rule["severity"]
        elif result["valid"] is None:
            result_dict["error"] = "Check function not implemented"
        else:
            result_dict["check_passes"] = True

        return result_dict

    def run(self):
        """
            Runs all relevant checks on the given path

            Args:
                path (str): The path to the field in the metadata
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

            path_exists, path_value = self._get_path_value(path)

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

                try:
                    result = self.DISPATCHER[rule_id](
                        path_value, rule["data"])
                except KeyError:  # rule function not implemented
                    result = {"valid": None}

                rule_metadata = self._get_rule(rule_id)

                results[path][rule_id] = self._result_dict(
                    result,
                    rule_metadata
                )

        return results
