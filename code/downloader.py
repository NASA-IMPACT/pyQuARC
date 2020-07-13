import re
import requests


class Downloader:
    """
        Downloads data given a concept ID
    """

    METADATA_FORMATS = [
        "dif",
        "echo10",
        "umm-json",
    ]

    BASE_URL = "https://cmr.earthdata.nasa.gov/search"
    COLLECTION_URL = f"{BASE_URL}/collections"
    GRANULE_URL = f"{BASE_URL}/granules"

    COLLECTION = "collection"
    GRANULE = "granule"
    INVALID = "invalid"

    def __init__(self, concept_id, metadata_format="echo10"):
        self.concept_id = concept_id
        self.metadata_format = metadata_format
        self.errors = []

        # big XML string or dict is stored here
        self.downloaded_content = None

    def _construct_url(self):
        """
            Constructs CMR API URL based on the concept ID
        """

        pass

    def download(self):
        """
            Downloads metadata by calling the CMR API
        """

        # constructs url based on concept id
        # calls request.get on the url
        # gets the response, makes sure it's 200, puts it in an object variable
        # otherwise logs the error in the error list
        # stores the data in the downloaded_content variable
        # logs success as well
        # returns nothing

        pass

    def validate(self):
        """
            Compare json of downloaded data against json schema
        """

        # takes stuff from downloaded_content
        # runs the downloaded response through the schema we've built
        # log validation errors
        pass

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
