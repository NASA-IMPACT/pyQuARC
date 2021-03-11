from pyQuARC.code.downloader import Downloader


class TestDownloader:
    """
    Test cases for the methods in Downloader class in downloder.py
    """

    def setup_method(self):
        self.concept_ids = {
            "collection": {
                "real": "C1339230297-GES_DISC",
                "dummy": "C123456-LPDAAC_ECS",
            },
            "granule": {
                "real": "G1370895082-GES_DISC",
                "dummy": "G1000000002-CMR_PROV",
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
            Downloader._concept_id_type(
                self.concept_ids["collection"]["dummy"])
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

    def test_construct_url_collection(self):
        real_collection = self.concept_ids["collection"]["real"]
        downloader = Downloader(real_collection, "echo10")
        assert (
            downloader._construct_url()
            == f"https://cmr.earthdata.nasa.gov/search/concepts/{real_collection}.echo10"
        )

    def test_construct_url_granule(self):
        real_granule = self.concept_ids["granule"]["real"]
        downloader = Downloader(real_granule, "echo10")

        assert (
            downloader._construct_url()
            == f"https://cmr.earthdata.nasa.gov/search/concepts/{real_granule}.echo10"
        )

    def test_log_error(self):
        # create a dummy granule downloader
        dummy_granule = self.concept_ids["granule"]["dummy"]
        downloader = Downloader(dummy_granule, "echo10")

        downloader.log_error("invalid_concept_id", {
                             "concept_id": dummy_granule})

        downloader.log_error(
            "request_failed",
            {
                "concept_id": dummy_granule,
                "url": "https://dummy.url",
                "status_code": 404,
            },
        )

        assert downloader.errors == [
            {"type": "invalid_concept_id", "details": {"concept_id": dummy_granule}},
            {
                "type": "request_failed",
                "details": {
                    "concept_id": dummy_granule,
                    "url": "https://dummy.url",
                    "status_code": 404,
                },
            },
        ]

    def test_download_invalid_concept_id(self):
        invalid_concept_id = self.concept_ids["invalid"]
        downloader = Downloader(invalid_concept_id, "echo10")

        downloader.download()

        assert len(downloader.errors) == 1
        assert downloader.errors == [
            {
                "type": "invalid_concept_id",
                "details": {"concept_id": self.concept_ids["invalid"]},
            }
        ]

    def test_download_dummy_collection_no_errors(self):
        dummy_collection = self.concept_ids["collection"]["dummy"]
        downloader = Downloader(dummy_collection, "echo10")

        downloader.download()

        assert len(downloader.errors) == 1
        assert downloader.errors == [
            {
                "type": "request_failed",
                "details": {
                    "concept_id": dummy_collection,
                    "url": f"https://cmr.earthdata.nasa.gov/search/concepts/{dummy_collection}.echo10",
                    "status_code": 404,
                },
            }
        ]

    def test_download_real_collection_no_errors(self):
        real_collection = self.concept_ids["collection"]["real"]
        downloader = Downloader(real_collection, "echo10")

        downloader.download()

        # is the concept id valid and is the request going through?
        assert downloader.errors == []

    def test_download_dummy_granule_no_errors(self):
        dummy_granule = self.concept_ids["granule"]["dummy"]
        downloader = Downloader(dummy_granule, "echo10")

        downloader.download()

        assert len(downloader.errors) == 1
        assert downloader.errors == [
            {
                "type": "request_failed",
                "details": {
                    "concept_id": dummy_granule,
                    "url": f"https://cmr.earthdata.nasa.gov/search/concepts/{dummy_granule}.echo10",
                    "status_code": 404,
                },
            }
        ]

    def test_download_real_granule_no_errors(self):
        real_collection = self.concept_ids["granule"]["real"]
        downloader = Downloader(real_collection, "echo10")

        downloader.download()

        # is the concept id valid and is the request going through?
        assert downloader.errors == []
