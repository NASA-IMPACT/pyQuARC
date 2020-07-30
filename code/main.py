import argparse
import requests
import xmltodict

from pprint import pprint

from downloader import Downloader
from validator import Validator


class PyCMR:
    """
        Takes concept_ids and runs downloader/validator on each

        1. Can generate list of concept_ids from CMR query
        2. Accepts custom list of concept_ids
    """

    def __init__(self, query=None, concept_ids=[]):
        self.concept_ids = concept_ids
        self.query = query

        if self.query:
            self._cmr_query()

        self.errors = {}

    def _cmr_query(self):
        # TODO: Make the page_size dynamic and use page_num to advance through multiple pages of results
        response = requests.get(self.query)

        if response.status_code != 200:
            return {"error": "CMR Query failed"}

        response_dict = xmltodict.parse(response.text)

        concept_ids = [
            result["id"]
            for result in response_dict["results"]["references"]["reference"]
        ]

        self.concept_ids = concept_ids

    def validate(self):
        if self.query and self.concept_ids:
            return {
                "error": "PyCMR received both CMR query and concept_ids. It can only accept one of those."
            }

        if not self.query and not self.concept_ids:
            return {
                "error": "PyCMR expects either a CMR query or a list of concept_ids."
            }

        for concept_id in self.concept_ids:
            downloader = Downloader(concept_id)
            content = downloader.download()
            validator = Validator(downloader.metadata_format)

            validation_errors = validator.validate(content)

            self.errors[concept_id] = validation_errors

        return self.errors


if __name__ == "__main__":
    # parse command line arguments (argparse)
    # --query
    # --concept_ids

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", action="store", type=str, help="CMR query URL.")
    group.add_argument(
        "--concept_ids",
        nargs="+",
        action="store",
        type=str,
        help="List of concept_ids.",
    )
    args = parser.parse_args()

    pycmr = PyCMR(query=args.query, concept_ids=args.concept_ids)
    results = pycmr.validate()

    pprint(results)

# "https://cmr.earthdata.nasa.gov/search/collections?provider=GES_DISC&project=MERRA&page_size=2000"
