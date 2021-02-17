import argparse
import json
import os
import os.path
import requests
import xmltodict

from pprint import pprint
from tqdm import tqdm

from .code.checker import Checker
from .code.constants import COLOR, ECHO10
from .code.downloader import Downloader

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
END = COLOR["reset"]


class VACQM:
    """
    Takes concept_ids and runs downloader/validator on each

    1. Can generate list of concept_ids from CMR query
    2. Accepts custom list of concept_ids
    """

    def __init__(
        self,
        query=None,
        input_concept_ids=[],
        fake=None,
        file_path=None,
        metadata_format=ECHO10,
        checks_override=None,
        messages_override=None
    ):
        """
        Args:
            query (str): The query url for the metadata content ids to download
            input_concept_ids (list of str): The list of concept ids to download
            validation_paths (list of str): The list of the fields/paths to validate in the metadata
            fake (bool): If set to true, used a fake data to perform the validation
            file (str): The absolute path to the sample/test metadata file
        """

        self.input_concept_ids = input_concept_ids
        self.query = query

        self.concept_ids = self._cmr_query() if self.query else self.input_concept_ids

        self.errors = []

        self.file_path = (
            file_path if file_path else os.path.join(
                    ABS_PATH,
                    "../tests/fixtures/test_cmr_metadata.echo10"
                )
        )
        self.metadata_format = metadata_format
        self.checks_override = checks_override
        self.messages_override = messages_override

    def _cmr_query(self):
        """
        Reads from the query urls all the concept ids

        Returns:
            (list of str) Returns all the concept ids found in the `query_url` as a list
        """
        # TODO: Make the page_size dynamic and use page_num to advance through multiple pages of results
        response = requests.get(self.query)

        if response.status_code != 200:
            return {"error": "CMR Query failed"}

        response_dict = xmltodict.parse(response.text)

        concept_ids = [
            result["id"]
            for result in response_dict["results"]["references"]["reference"]
        ]

        return concept_ids

    def validate(self):
        """
        Validates the metadata contents of all the `concept_ids` and returns the errors

        Returns:
            (list of dict) The errors found in the metadata content of all the `concept_id`s
        """
        checker = Checker(
            metadata_format=self.metadata_format,
            checks_override=self.checks_override,
            messages_override=self.messages_override
        )

        if self.concept_ids:
            for concept_id in tqdm(self.concept_ids):
                downloader = Downloader(concept_id, self.metadata_format)
                content = downloader.download().encode()

                validation_errors = checker.run(content)
                self.errors.append(
                    {
                        "concept_id": concept_id,
                        "errors": validation_errors,
                    }
                )

        elif self.file_path:
            with open(os.path.abspath(self.file_path), "r") as myfile:
                content = myfile.read().encode()

                validation_errors = checker.run(content)
                self.errors.append(
                    {
                        "file": self.file_path,
                        "errors": validation_errors,
                    }
                )

        return self.errors

    @staticmethod
    def _error_message(messages):
        severities = ["error", "warning", "info"]
        result_string = ""
        for message in messages:
            colored_message = [
                message.replace(
                    text,
                    f"{COLOR[severity]}{text}{END}"
                )
                for severity in severities
                if (text := severity.title()) and message.startswith(text)
            ][0]
            result_string += (f"\t\t{colored_message}{END}\n")
        return result_string

    def display_results(self):
        result_string = '''
        ********************************
        ** Metadata Validation Errors **
        ********************************\n'''
        error_prompt = ""
        for error in self.errors:
            title = error.get("concept_id") or error.get("file")
            error_prompt += (f"\n\tMETADATA: {COLOR['title']}{COLOR['bright']}{title}{END}\n")
            validity = True
            for field, result in error["errors"].items():
                for rule_type, value in result.items():
                    if not value.get("valid"):
                        messages = value.get("message")
                        error_prompt += (f"\n\t>> {field}: {END}\n")
                        error_prompt += self._error_message(messages)
                        error_prompt += (f"\t\t{remedy}\n") if (remedy := value.get('remediation')) else ""
                        validity = False
            if validity:
                error_prompt += "\n\tNo validation errors\n"
        result_string += error_prompt
        print(result_string)

if __name__ == "__main__":
    # parse command line arguments (argparse)
    # --query
    # --concept_ids
    # --file
    # --fake

    parser = argparse.ArgumentParser()
    download_group = parser.add_mutually_exclusive_group()
    download_group.add_argument(
        "--query", action="store", type=str, help="CMR query URL."
    )
    download_group.add_argument(
        "--concept_ids",
        nargs="+",
        action="store",
        type=str,
        help="List of concept IDs.",
    )
    fake_group = parser.add_mutually_exclusive_group()
    fake_group.add_argument(
        "--file",
        action="store",
        type=str,
        help="Path to the test file, either absolute or relative to the root dir.",
    )
    fake_group.add_argument(
        "--fake",
        action="store",
        type=str,
        help="Use a fake content for testing.",
    )
    parser.add_argument(
        "--format",
        action="store",
        nargs="?",
        type=str,
        help="The metadata format",
    )

    args = parser.parse_args()
    parser.usage = parser.format_help().replace("optional ", "")

    if not (args.query or args.concept_ids or args.file or args.fake):
        parser.error(
            "No metadata given, add --query or --concept_ids or --file or --fake"
        )
        exit()

    vacqm = VACQM(
        query=args.query,
        input_concept_ids=args.concept_ids or [],
        fake=args.fake,
        file_path=args.file,
        metadata_format=args.format or ECHO10,
    )
    results = vacqm.validate()
    vacqm.display_results()

    # print(json.dumps(results, indent=4))
