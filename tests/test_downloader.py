import pytest

from ..code.downloader import Downloader


class TestDownloader:
    """
    Test cases for the downloader script in downloder.py
    """

    def setup_method(self):
        # self.downloader = Downloader()
        self.concept_ids = {
            "collection": {
                "real": "C1339230297-GES_DISC",
                "dummy": "C123456-LPDAAC_ECS",
            },
            "granule": {
                "real": "",
                "dummy": "G1000000002-CMR_PROV1"
            },
            "invalid": "asdfasdf",
        }

    def test_download(self):
        # self.assertEqual()
        # this should return a status_code that must be 200 or 404
        # hitting the URL we are supposed to hit
        # getting results from that in proper format (asking for echo10, we get echo10)
        # store the content in a variable or fill up the error list
        # if the concept ID is a collection concept id, it downloads collection and not granule. same for granule
        # assert "h" in "this"
        pass

    # def test_validate(self):
    #     pass

    def test_concept_id_type_collection(self):
        assert (
            Downloader._concept_id_type(self.concept_ids["collection"]["dummy"])
            == Downloader.COLLECTION
        )

    def test_concept_id_type_granule(self):
        assert (
            Downloader._concept_id_type(self.concept_ids["granule"]["dummy"])
            == Downloader.GRANULE
        )

    def test_concept_id_type_invalid(self):
        assert (
            Downloader._concept_id_type(self.concept_ids["invalid"])
            == Downloader.INVALID
        )
