import requests

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
    def _extract_http_texts(text_with_urls):
        """
        Extracts anything that starts with 'http' from `text_with_urls`. 
        This is required for catching "wrong" urls that aren't extracted by `URLExtract.find_urls()` because they are not urls at all
        An example: https://randomurl
        Args:
            text_with_urls (str, required): The text that contains the URLs where the check needs to be performed

        Returns:
            (list) List of texts that start with 'http' from `text_with_urls`
        """
        texts = text_with_urls.split(' ')
        starts_with_http = set()
        for text in texts:
            if text.startswith('http'):
                starts_with_http.add(text)
        return starts_with_http

    @staticmethod
    @if_arg
    def health_and_status_check(text_with_urls):
        """
        Checks the health and status of the URLs included in `text_with_urls`
        Args:
           text_with_urls (str, required): The text that contains the URLs where the check needs to be performed
        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        results = []

        validity = True

        # extract URLs from text
        extractor = URLExtract()
        urls = extractor.find_urls(text_with_urls)
        urls.extend(
            UrlValidator._extract_http_texts(text_with_urls)
        )

        # remove dots at the end (The URLExtract library catches URLs, but sometimes appends a '.' at the end)
        # remove duplicated urls
        urls = set(url[:-1] if url.endswith(".") else url for url in urls)
        value = ", ".join(urls)

        # check that URL returns a valid response
        for url in urls:
            if not url.startswith("http"):
                url = f"http://{url}"
            try:
                response_code = requests.get(url).status_code
                if response_code == 200:
                    if url.startswith("http://"):
                        secure_url = url.replace("http://", "https://")
                        if requests.get(secure_url).status_code == 200:
                            result = {"url": url, "error": "The URL is secure. Please use 'https' instead of 'http'."}
                    else:
                        continue
                else:
                    result = {"url": url, "error": f'Status code {response_code}'}
            except requests.ConnectionError:
                result = {"url": url, "error": "The URL does not exist on Internet."}
            except:
                result = {"url": url, "error": "Some unknown error occurred."}
            results.append(result)

        if results:
            validity = False
            value = results

        return {"valid": validity, "value": value}

    @staticmethod
    @if_arg
    def doi_check(doi):
        """
        Checks if the doi link given in the text is a valid doi link

        Returns:
            (dict) An object with the validity of the check and the instance/results
        """
        valid = False
        if doi.strip().startswith("10."): # doi always starts with "10."
            url = f"https://www.doi.org/{doi}"
            valid =  UrlValidator.health_and_status_check(url).get("valid")
        return {"valid": valid, "value": doi}

    @staticmethod
    @if_arg
    def doi_link_update(
        value, bad_urls
    ):
        validity = True
        if value in bad_urls:
            validity = False

        return {
            "valid": validity,
            "Value": value
        }
