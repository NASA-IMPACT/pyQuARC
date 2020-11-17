import argparse
import json
import os
import requests
import xmltodict

from pprint import pprint
from tqdm import tqdm

from code.downloader import Downloader
from code.checker import Checker


class VACQM:
    """
        Takes concept_ids and runs downloader/validator on each

        1. Can generate list of concept_ids from CMR query
        2. Accepts custom list of concept_ids
    """

    def __init__(
        self, query=None, input_concept_ids=[], fake=None, file_path=None
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

        self.fake = fake
        self.file_path = file_path

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
        if self.query and self.input_concept_ids:
            return {
                "error": "VACQM received both CMR query and concept_ids. It can only accept one of those."
            }

        if not self.query and not self.input_concept_ids:
            return {
                "error": "VACQM expects either a CMR query or a list of concept_ids."
            }

        for concept_id in tqdm(self.concept_ids):
            downloader = Downloader(concept_id)
            if self.fake:
                fake_file_path = self.file_path or "code/tests/fixtures/test_cmr_metadata.echo10"
                with open(os.path.abspath(fake_file_path), "r") as myfile:
                    content = myfile.read().encode()
            else:
                content = downloader.download()

            checker = Checker(
                downloader.metadata_format
            )

            validation_errors = checker.run(content)

            self.errors.append(
                {
                    "concept_id": concept_id,
                    "errors": validation_errors,
                }
            )

        return self.errors


if __name__ == "__main__":
    # parse command line arguments (argparse)
    # --query
    # --concept_ids

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--query",
        action="store",
        type=str,
        help="CMR query URL."
    )
    group.add_argument(
        "--concept_ids",
        nargs="+",
        action="store",
        type=str,
        help="List of concept IDs.",
    )
    parser.add_argument(
        "--file",
        action="store",
        type=str,
        help="Path to the test file, either absolute or relative to the root dir.",
    )
    parser.add_argument(
        "--fake", action="store", type=str, help="Fake content for testing.",
    )
    args = parser.parse_args()

    vacqm = VACQM(
        query=args.query,
        input_concept_ids=args.concept_ids or [],
        fake=args.fake,
        file_path=args.file
    )
    results = vacqm.validate()

    print(json.dumps(results, indent=4))
