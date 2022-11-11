from xmltodict import parse
from pyQuARC.code.custom_checker import CustomChecker
from tests.fixtures.custom_checker import INPUT_OUTPUT
from tests.common import read_test_metadata

class TestCustomChecker:
    """
    Test cases for the CustomChecker script in custom_checker.py
    """

    def setup_method(self):
        self.custom_checker = CustomChecker()
        self.dummy_metadata = parse(read_test_metadata())

    def test_get_path_value(self):
        in_out = INPUT_OUTPUT["get_path_value"]
        for _in, _out in zip(in_out["input"], in_out["output"]):
            assert CustomChecker._get_path_value(
                self.dummy_metadata,
                _in
            ) == _out

        dummy_dif_metadata = {
            "CollectionCitations": [
                {
                    "Creator": "Kamel Didan",
                    "OnlineResource": {
                        "Linkage": "https://doi.org/10.5067/MODIS/MOD13Q1.061",
                        "Name": "DOI Landing Page"
                    },
                    "OtherCitationDetails": "The DOI landing page provides citations in APA and Chicago styles.",
                    "Publisher": "NASA EOSDIS Land Processes DAAC",
                    "ReleaseDate": "2021-02-16",
                    "SeriesName": "MOD13Q1.061",
                    "Title": "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061"
                }
            ],
            "MetadataDates": [
                {
                    "Type": "CREATE",
                    "Date": "2021-09-15T15:54:00.000Z"
                },
                {
                    "Type": "UPDATE",
                    "Date": "2021-09-30T15:54:00.000Z"
                }
            ],
            "DOI": {
                "Authority": "https://doi.org",
                "DOI": "10.5067/MODIS/MOD13Q1.061"
            },
            "SpatialExtent": {
                "GranuleSpatialRepresentation": "GEODETIC",
                "HorizontalSpatialDomain": {
                    "Geometry": {
                        "BoundingRectangles": [
                            {
                                "EastBoundingCoordinate": 180.0,
                                "NorthBoundingCoordinate": 85,
                                "SouthBoundingCoordinate": 89,
                                "WestBoundingCoordinate": -180.0
                            }
                        ],
                        "CoordinateSystem": "CARTESIAN"
                    },
                    "ResolutionAndCoordinateSystem": {
                        "HorizontalDataResolution": {
                            "GriddedResolutions": [
                                {
                                    "Unit": "Meters",
                                    "XDimension": 250.0,
                                    "YDimension": 250.0
                                }
                            ]
                        }
                    },
                    "ZoneIdentifier": "MODIS Sinusoidal Tiling System"
                },
                "SpatialCoverageType": "HORIZONTAL"
            }
        }

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "CollectionCitations/Creator"
        ) == ["Kamel Didan"]

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "CollectionCitations/OnlineResource/Name"
        ) == ["DOI Landing Page"]

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "MetadataDates/Date?Type=UPDATE"
        ) == ["2021-09-30T15:54:00.000Z"]

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "MetadataDates/Date?Type=CREATE"
        ) == ["2021-09-15T15:54:00.000Z"]

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "DOI/DOI"
        ) == ["10.5067/MODIS/MOD13Q1.061"]

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "SpatialExtent/HorizontalSpatialDomain/Geometry/BoundingRectangles/WestBoundingCoordinate"
        ) == [-180.0]

        assert CustomChecker._get_path_value(
            dummy_dif_metadata,
            "SpatialExtent/GranuleSpatialRepresentation"
        ) == ["GEODETIC"]
