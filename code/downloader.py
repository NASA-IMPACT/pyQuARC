import json
import re
import requests

from xmltodict import parse

from .constants import DIF, ECHO10, UMM_JSON


class Downloader:
    """
        Downloads data given a concept ID
    """

    BASE_URL = (
        "https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}.{metadata_format}"
    )

    COLLECTION = "collection"
    GRANULE = "granule"
    INVALID = "invalid"

    def __init__(self, concept_id, metadata_format=ECHO10, version=None):
        """
        Args:
            concept_id (str): The concept id of the metadata to download
            metadata_format (str): The file format of the metadata to download
            version (str): The version of the metadata to download
        """
        # TODO: Handle versions here
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
            (bool) True if the concept id is valid, False otherwise
        """

        return Downloader._concept_id_type(self.concept_id) != Downloader.INVALID

    def _construct_url(self):
        """
        Constructs CMR API URL based on the concept ID.
        It assumes that the concept_id is already valid.

        Returns:
            (str) The URL constructed based on the concept ID
        """

        concept_id_type = Downloader._concept_id_type(self.concept_id)
        constructed_url = Downloader.BASE_URL.format(
            concept_id=self.concept_id, metadata_format=self.metadata_format
        )

        return constructed_url

    def log_error(self, error_message_code, kwargs):
        """
        Logs errors in self.errors

        Args:
            error_message_code (str): The key to the ERROR_MESSAGES dict
            kwargs (dict): Any keyword arguments required for the error string
        """

        self.errors.append({"type": error_message_code, "details": kwargs})

    def download(self):
        """
        Downloads metadata by calling the CMR API

        Returns:
            (str) The JSON string if download is successful, None otherwise
        """

        # is the concept id valid? if not, log error
        if not self._valid_concept_id():
            self.log_error(
                "invalid_concept_id",
                {"concept_id": self.concept_id}
            )
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
        return self.downloaded_content

    @staticmethod
    def _concept_id_type(concept_id: str) -> str:
        """
        Concept ID can be for a collection or granule. This function determines which one it is.

        Returns:
            (str)   "collection" when the concept_id is a collection
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
