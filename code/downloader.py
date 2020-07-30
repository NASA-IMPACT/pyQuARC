import json
import re
import requests

from xmltodict import parse

from constants import DIF, ECHO10, UMM_JSON


class Downloader:
    """
        Downloads data given a concept ID
    """

    # BASE_URL = "https://cmr.earthdata.nasa.gov/search/{concept_id_type}/{concept_id}"
    BASE_URL = "https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}.{metadata_format}"

    COLLECTION = "collection"
    GRANULE = "granule"
    INVALID = "invalid"

    def __init__(self, concept_id, metadata_format=ECHO10, version=None):
        self.concept_id = concept_id
        self.version = version
        self.metadata_format = metadata_format
        self.errors = []

        # big XML string or dict is stored here
        self.downloaded_content = None

    def _valid_concept_id(self):
        """
            Check whether passed concept id is valid

            Returns:
                True if the concept id is valid
                False if the concept id is not valid
        """

        return Downloader._concept_id_type(self.concept_id) != Downloader.INVALID

    def _construct_url(self):
        """
            Constructs CMR API URL based on the concept ID.
            It assumes that the concept_id is already valid.

            Returns:
                constructed_url (str)
        """

        concept_id_type = Downloader._concept_id_type(self.concept_id)
        constructed_url = Downloader.BASE_URL.format(
            concept_id=self.concept_id,
            metadata_format=self.metadata_format
        )

        return constructed_url

    def log_error(self, error_message_code, kwargs):
        """
            Logs errors in self.errors

            Arguments:
                error_message_code (str): The key to the ERROR_MESSAGES dict
                **kwargs: any keyword arguments required for the error string

            Returns:
                None
        """

        self.errors.append({"type": error_message_code, "details": kwargs})

    def _convert_output_to_json(self):
        """
            Convert downloaded content to JSON if necessary
        """

        # TODO: Handle DIF here
        if self.metadata_format == ECHO10:
            result = parse(self.downloaded_content)
        else:
            result = self.downloaded_content

        return json.dumps(result)

    def download(self):
        """
            Downloads metadata by calling the CMR API
        """

        # is the concept id valid? if not, log error
        if not self._valid_concept_id():
            self.log_error("invalid_concept_id", {
                           "concept_id": self.concept_id})
            return

        # constructs url based on concept id
        url = self._construct_url()
        response = requests.get(url)

        # gets the response, makes sure it's 200, puts it in an object variable
        if response.status_code != 200:
            self.log_error(
                "request_failed",
                {
                    "concept_id": self.concept_id,
                    "url": url,
                    "status_code": response.status_code,
                },
            )
            return

        # stores the data in the downloaded_content variable
        self.downloaded_content = response.text

        return self._convert_output_to_json()

    @staticmethod
    def _concept_id_type(concept_id: str) -> str:
        """
            Concept ID can be for a collection or granule. This function determines which one it is.

            Returns:
                "collection" when the concept_id is a collection
                "granule" when the concept_id is a granule
                "invalid" when the concept_id is neither collection nor granule, or invalid concept id
        """

        concept_id_pattern: str = r"C\d+-([a-zA-Z]+_[a-zA-Z]+)+"
        granule_id_pattern: str = r"G\d+-([a-zA-Z]+_[a-zA-Z]+)+"

        concept_id_type: str = Downloader.INVALID

        if re.match(concept_id_pattern, concept_id):
            concept_id_type = Downloader.COLLECTION
        elif re.match(granule_id_pattern, concept_id):
            concept_id_type = Downloader.GRANULE

        return concept_id_type


# new class for error logs

# new class for validation


# if __name__ == "__main__":
#     concept_id = "C123456-LPDAAC_ECS"
#     downloader = Downloader(concept_id)


# take input from the user
# concept ID

# how to find out correct endpoint

# need to figure out collection or granule
# collection starts with c and granule starts with g

# collection: C123456-LPDAAC_ECS
# https://cmr.earthdata.nasa.gov/search/collections?concept_id\[\]=C123456-LPDAAC_ECS

# granule id: G1000000002-CMR_PROV1
# https://cmr.earthdata.nasa.gov/search/granules?provider=PROV1&echo_granule_id\[\]=G1000000002-CMR_PROV1

# search for a collection
# randomly select one granule
# get details of that granule

# granule metadata is automatically extracted
# if you fix one, you fix all of them
