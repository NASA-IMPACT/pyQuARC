import json
import re
import requests

from datetime import datetime
from urlextract import URLExtract

from constants import SCHEMA_PATHS
from relations import mapping as relations_mapping


class Checker:

    def __init__(self, content_to_validate):
        self.content_to_validate = json.loads(content_to_validate)
        self.ruleset = json.load(open(SCHEMA_PATHS["ruleset"], "r"))
        self.rules_mapping = json.load(
            open(SCHEMA_PATHS["rules_mapping"], "r"))
        self.id_to_rule_mapping = json.load(
            open(SCHEMA_PATHS["id_to_rule_mapping"], "r"))

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
            return False
        except TypeError as e:
            # TODO: need another way to parse lists
            print(e, split.strip())
            print(f"_get_path_value failed for {path}")
        return input_json

    def _iso_datetime(self, datetime_string):
        """
        Converts the input datetime string to iso datetime object

        Args:
            datetime_string (str): the datetime string

        Returns:
            (datetime.datetime) if the string is valid iso string, False otherwise
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
            (dict) an object with the validity of the check and the instance
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
            (dict) an object with the validity of the check and the instance
        """
        
        date1 = self._iso_datetime(path_value)
        date2 = self._iso_datetime(self._get_path_value(data["related_paths"]))
        relation = data["related_paths"][0]["relation"]

        result = relations_mapping["relation"](date1, date2)

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
            (dict) an object with the validity of the check and the instance/results
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


    DISPATCHER = {
        "date_datetime_iso_format_check": date_datetime_iso_format_check,
        "data_update_time_logic_check": data_update_time_logic_check,
        "url_health_and_status_check": url_health_and_status_check,
        "collectiondatatype_enumeration_check": collectiondatatype_enumeration_check,
    }


    def run_old(self):
        """
        Performs all the custom checks based on the QA Rules

        Returns:
            (dict) A dictionary that gives the result of the custom checks and errors if they exist
        """
        # TODO: This code needs to be rewritten completely
        results = {}

        for mapping in self.rules_mapping:
            # do nothing for paths that have no custom checks
            if not mapping["rules"]:
                continue

            path = mapping["path"]
            results[path] = {}

            for rule in mapping["rules"]:
                rule_id = rule["id"]
                function_name = rule_id

                results[path][rule_id] = {}
                rule = self._get_rule(rule_id)

                value = self._get_path_value(path)
                if not value:
                    del results[path][rule_id]
                    # results[path]["exists"] = False
                    continue

                results[path]["exists"] = True
                try:
                    if rule_id == "data_update_time_logic_check":
                        value1 = self._get_path_value(
                            "Collection/InsertTime")
                        value2 = self._get_path_value(
                            "Collection/LastUpdate"
                        )

                        result = self.DISPATCHER[rule["id"]](
                            self, value1, value2)
                    else:
                        print(self.DISPATCHER[rule["id"]])
                        print(value)
                        result = self.DISPATCHER[rule["id"]](self, value)
                except KeyError as e:
                    # print(e)
                    continue
                if result["valid"] == False:
                    results[path][rule_id]["check_passes"] = False
                    results[path][rule_id]["severity"] = rule["severity"]

                    results[path][rule_id]["message"] = re.sub(
                        r"\{.*\}", str(result["instance"]
                                       ), rule["message-fail"]
                    )
                    results[path][rule_id]["help_url"] = rule["help_url"]
                    # checks[path][rule_id]["error"] = result["result"]
                else:
                    results[path][rule_id]["check_passes"] = True

                results[path][rule_id]["instance"] = result["instance"]

            # if there is no output for any of the rules
            if not results[path]:
                del results[path]

        return results

    def run(self, path):
        '''
            Runs all relevant checks on the given path

            Args:
                path (str): The path to the field in the metadata
            Returns:
                (dict) Result of the checks
        '''

        for mapping in self.rules_mapping:
            if mapping["path"] == path:
                rules = mapping

        path_value = self._get_path_value(path)

        try:
            for rule in rules["rules"]:
                rule_metadata = self.id_to_rule_mapping[rule["id"]]

                result = self.DISPATCHER[rule_metadata["id"]](path_value, rule["data"])
        except:
            print(path)
            # pass



