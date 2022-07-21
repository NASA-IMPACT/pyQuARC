import argparse
import os
import os.path
import requests
import xmltodict

from tqdm import tqdm

if __name__ == '__main__':
    from code.checker import Checker
    from code.constants import COLOR, ECHO10_C, SUPPORTED_FORMATS
    from code.downloader import Downloader
    from code.utils import get_cmr_url, is_valid_cmr_url
else:
    from .code.checker import Checker
    from .code.constants import COLOR, ECHO10_C, SUPPORTED_FORMATS
    from .code.downloader import Downloader
    from .code.utils import get_cmr_url, is_valid_cmr_url


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
END = COLOR["reset"]


class ARC:
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
        metadata_format=ECHO10_C,
        checks_override=None,
        rules_override=None,
        messages_override=None,
        version=None,
        cmr_host=get_cmr_url(),
    ):
        """
        Args:
            query (str): The query url for the metadata content ids to download
            input_concept_ids (list of str): The list of concept ids to download
            fake (bool): If set to true, used a fake data to perform the validation
            file_path (str): The absolute path to the sample/test metadata file
            metadata_format (str): The format of the metadata file (echo-c, dif10, echo-g etc)
            checks_override (str): The filepath of the checks_override file
            rules_override (str): The filepath of the rules_override file
            messages_override (str): The filepath of the checks_override file
        """

        self.input_concept_ids = input_concept_ids
        self.query = query

        self.concept_ids = self._cmr_query() if self.query else self.input_concept_ids

        self.errors = []

        self.file_path = (
            file_path if file_path else os.path.join(
                    ABS_PATH,
                    f"../tests/fixtures/test_cmr_metadata.{metadata_format}"
                )
        )
        self.metadata_format = metadata_format
        self.checks_override = checks_override
        self.rules_override = rules_override
        self.messages_override = messages_override
        self.cmr_host = cmr_host
        self.version = version

    def _cmr_query(self):
        """
        Reads from the query urls all the concept ids

        Returns:
            (list of str) Returns all the concept ids found in the `query_url` as a list
        """
        concept_ids = []

        # If any of the page query params is already specified in the url, it means that
        # the user wants the subset of results provided by the query param, so we run
        # the get request only once
        # Else, we need to get all the result, not just the one in the given page since
        # there's pagination implemented by the API. Thus, we iterate the get request with
        # page_num query param

        already_selected = False
        page_qparams = ['page_size', 'page_num', 'offset']
        for qparam in page_qparams:
            if qparam in self.query:
                already_selected = True

        # Set to maximum allowable so that we need the min # of get req
        page_size = 2000
        collected = 0
        page_num = 1

        orig_query = f"{self.query}&page_size={page_size}" if not already_selected else self.query
        query = orig_query

        while True:
            response = requests.get(query)

            if response.status_code != 200:
                return {"error": "CMR Query failed"}

            response_dict = xmltodict.parse(response.text)
            hits = int(response_dict["results"]["hits"])
            collections = response_dict["results"]["references"]["reference"]

            collected += len(collections)

            concept_ids.extend([
                collection["id"]
                for collection in collections
            ])

            if collected >= hits or already_selected:
                break

            page_num += 1
            query = f"{orig_query}&page_num={page_num}"

        return concept_ids

    def validate(self):
        """
        Validates the metadata contents of all the `concept_ids` and returns the errors

        Returns:
            (list of dict) The errors found in the metadata content of all the `concept_id`s
        """
        checker = Checker(
            metadata_format=self.metadata_format,
            checks_override=self.checks_override,
            rules_override=self.rules_override,
            messages_override=self.messages_override
        )

        if self.concept_ids:
            for concept_id in tqdm(self.concept_ids):
                downloader = Downloader(concept_id, self.metadata_format, self.version, self.cmr_host)
                if not (content := downloader.download()):
                    self.errors.append(
                        {
                            "concept_id": concept_id,
                            "errors": [],
                            "pyquarc_errors": [
                                {
                                    "message": "No metadata content found. Please make sure the concept id is correct.",
                                    "details": f"The request to CMR {self.cmr_host} failed for concept id {concept_id}",
                                }
                            ]
                        }
                    )
                    continue
                content = content.encode()

                validation_errors, pyquarc_errors = checker.run(content)
                self.errors.append(
                    {
                        "concept_id": concept_id,
                        "errors": validation_errors,
                        "pyquarc_errors": pyquarc_errors
                    }
                )

        elif self.file_path:
            with open(os.path.abspath(self.file_path), "r") as myfile:
                content = myfile.read().encode()

                validation_errors, pyquarc_errors = checker.run(content)
                self.errors.append(
                    {
                        "file": self.file_path,
                        "errors": validation_errors,
                        "pyquarc_errors": pyquarc_errors
                    }
                )
        return self.errors

    @staticmethod
    def _error_message(messages):
        severities = ["error", "warning", "info"]
        result_string = ""
        for message in messages:
            colored_message = [
                message.replace(
                    text,
                    f"{COLOR[severity]}{text}{END}"
                )
                for severity in severities
                if (text := severity.title()) and message.startswith(text)
            ][0]
            result_string += (f"\t\t{colored_message}{END}\n")
        return result_string

    def display_results(self):
        result_string = '''
        ********************************
        ** Metadata Validation Errors **
        ********************************\n'''
        error_prompt = ""
        for error in self.errors:
            title = error.get("concept_id") or error.get("file")
            error_prompt += (f"\n\t{COLOR['title']}{COLOR['bright']}METADATA: {title}{END}\n")
            validity = True
            for field, result in error["errors"].items():
                for rule_type, value in result.items():
                    if not value.get("valid"):
                        messages = value.get("message")
                        error_prompt += (f"\n\t>> {field}: {END}\n")
                        error_prompt += self._error_message(messages)
                        error_prompt += (f"\t\t{remedy}\n") if (remedy := value.get('remediation')) else ""
                        validity = False
            if validity:
                error_prompt += "\n\tNo validation errors\n"

            if (pyquarc_errors := error["pyquarc_errors"]):
                error_prompt += (f"\n\t {COLOR['title']}{COLOR['bright']} pyQuARC ERRORS: {END}\n")
                for error in pyquarc_errors:
                    error_prompt += (f"\t\t  ERROR: {error['message']}. Details: {error['details']} \n")

        result_string += error_prompt
        print(result_string)


if __name__ == "__main__":
    """
        parse command line arguments (argparse)
        --query
        --concept_ids
        --file
        --fake
        --format
        --cmr_host
        --version
    """
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
        help=f"The metadata format. Choices are: echo-c (echo10 collection), echo-g (echo10 granule), dif10 (dif10 collection), umm-c (umm-json collection), umm-g (umm-json granules)",
    )
    parser.add_argument(
        "--cmr_host",
        action="store",
        nargs="?",
        type=str,
        help="The cmr host base url. Default is: https://cmr.earthdata.nasa.gov",
    )
    parser.add_argument(
        "--version",
        action="store",
        nargs="?",
        type=str,
        help="The revision version of the collection. Default is the latest version.",
    )

    args = parser.parse_args()
    parser.usage = parser.format_help().replace("optional ", "")

    if not (args.query or args.concept_ids or args.file or args.fake):
        parser.error(
            "No metadata given, add --query or --concept_ids or --file or --fake"
        )
    format = args.format or ECHO10_C
    if (format not in SUPPORTED_FORMATS):
        parser.error(
            f"The given format is not supported. Only {', '.join(SUPPORTED_FORMATS)} are supported."
        )

    if cmr_host := args.cmr_host:
        if not is_valid_cmr_url(cmr_host):
            raise Exception(f"The given CMR host is not valid: {cmr_host}")
        os.environ["CMR_URL"] = cmr_host
    
    arc = ARC(
        query=args.query,
        input_concept_ids=args.concept_ids or [],
        fake=args.fake,
        file_path=args.file,
        metadata_format=args.format or ECHO10_C,
        cmr_host=get_cmr_url(),
        version=args.version,
    )
    results = arc.validate()
    arc.display_results()
