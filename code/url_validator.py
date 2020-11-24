import requests
import re

from urlextract import URLExtract

from .string_validator import StringValidator
from .utils import if_arg


class UrlValidator(StringValidator):
    """
    Validator class for URLs
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    @if_arg
    def health_and_status_check(text_with_urls):
        """
        Checks the health and status of the URLs included in `text`
        Args:
           text_with_urls (str, required): The text that contains the URLs where the check needs to be performed
        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        results = []

        validity = True
        value = text_with_urls

        # extract URLs from text
        extractor = URLExtract()
        urls = extractor.find_urls(text_with_urls)

        # remove dots at the end (The URLExtract library catches URLs, but sometimes appends a '.' at the end)
        # remove duplicated urls
        urls = set(url[:-1] if url.endswith(".") else url for url in urls)

        # check that URL returns a valid response
        for url in urls:
            if not url.startswith("http"):
                url = f"http://{url}"
            try:
                response_code = requests.get(url).status_code
                if response_code == 200:
                    continue
                result = {"url": url, "status_code": response_code}
            except requests.ConnectionError as exception:
                result = {"url": url, "error": "The URL does not exist on Internet."}
            except Exception as e:
                result = {"url": url, "error": "Some unknown error occurred."}
            results.append(result)

        if results:
            validity = False
            value = results

        return {"valid": validity, "value": ", ".join(urls)}

    @staticmethod
    @if_arg
    def doi_check(doi):
        """
        Checks if the doi link given in the text is a valid doi link

        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        url = f"https://www.doi.org/{doi}"
        return UrlValidator.health_and_status_check(url)
