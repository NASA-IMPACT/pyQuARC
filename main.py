import argparse
import json
import os
import requests
import xmltodict

from pprint import pprint
from tqdm import tqdm

from code.checker import Checker
from code.constants import ECHO10
from code.downloader import Downloader


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
            file_path if file_path else "code/tests/fixtures/test_cmr_metadata.echo10"
        )
        self.metadata_format = metadata_format

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
        checker = Checker(self.metadata_format)

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
                        "errors": validation_errors,
                    }
                )

        return self.errors

    def printable_result(self):
        result_string = "\n\n** Metadata Validation Errors **\n\n"
        for error in self.errors:
            if concept_id := error.get("concept_id"):
                result_string += (f"{concept_id}:\n\t")
            for field, result in error["errors"].items():
                for rule_type, value in result.items():
                    if value.get("valid") == False:
                        if value.get("message"):
                            result_string += (f"{field}:\n\t")
                            result_string += (f"{rule_type}:\n\t\t")
                            result_string += (f"{value['message']}\n")
        return result_string


if __name__ == "__main__":
    # parse command line arguments (argparse)
    # --query
    # --concept_ids

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
    print(vacqm.printable_result())
    # for _, value in results[0]["errors"]["custom"].items():
    #     for key, val in value.items():
    #         if not val["valid"]:
    #             print(f"{key}: {val['message']}")

    # print(json.dumps(results, indent=4))
