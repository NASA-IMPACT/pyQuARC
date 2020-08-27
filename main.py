import argparse
import json
import requests
import xmltodict

from pprint import pprint
from tqdm import tqdm

from code.downloader import Downloader
from code.validator import Validator


class PyCMR:
    """
        Takes concept_ids and runs downloader/validator on each

        1. Can generate list of concept_ids from CMR query
        2. Accepts custom list of concept_ids
    """

    def __init__(
        self, query=None, input_concept_ids=[], validation_paths=[], fake=None
    ):
        """
        Args:
            query (str): The query url for the metadata content ids to download
            input_concept_ids (list of str): The list of concept ids to download
            validation_paths (list of str): The list of the fields/paths to validate in the metadata
            fake (bool): If set to true, used a fake data to perform the validation
        """

        self.input_concept_ids = input_concept_ids
        self.query = query
        self.validation_paths = validation_paths

        self.concept_ids = self._cmr_query() if self.query else self.input_concept_ids

        self.errors = []

        self.fake = fake

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
                "error": "PyCMR received both CMR query and concept_ids. It can only accept one of those."
            }

        if not self.query and not self.input_concept_ids:
            return {
                "error": "PyCMR expects either a CMR query or a list of concept_ids."
            }

        for concept_id in tqdm(self.concept_ids):
            downloader = Downloader(concept_id)
            if self.fake:
                with open("code/tests/data/test_cmr_metadata_echo10.json", "r") as myfile:
                    content = myfile.read()
            else:
                content = downloader.download()

            validator = Validator(
                downloader.metadata_format, validation_paths=self.validation_paths
            )

            validation_errors = validator.validate(content)

            self.errors.append(
                {
                    "concept_id": concept_id,
                    "errors": validation_errors,
                    "checked_fields": self.validation_paths or "all",
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
        "--fields_to_validate",
        nargs="+",
        action="store",
        type=str,
        help="List of fields to validate in the schema. By default, it takes all of them. For example, Collection/Temporal/RangeDateTime only validates that field.",
    )
    parser.add_argument(
        "--fake", action="store", type=str, help="Fake content for testing.",
    )
    args = parser.parse_args()

    pycmr = PyCMR(
        query=args.query,
        input_concept_ids=args.concept_ids or [],
        validation_paths=args.fields_to_validate or [],
        fake=args.fake,
    )
    results = pycmr.validate()

    print(json.dumps(results, indent=4))
    