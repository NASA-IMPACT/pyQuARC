import os
import requests

from urlextract import URLExtract

from .string_validator import StringValidator
from .utils import get_headers, if_arg


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
        texts = text_with_urls.split(" ")
        starts_with_http = set()
        for text in texts:
            if text.startswith("http"):
                starts_with_http.add(text)
        return starts_with_http

    @staticmethod
    def _status_code_from_request(url):
        """
        Return HTTP status code for url, raising requests exceptions to caller.
        """
        headers = get_headers()
        return requests.get(url, headers=headers, timeout=10).status_code

    @staticmethod
    def _extract_and_normalize_urls(text_with_urls):
        """
        Extract URLs from text, include tokens that start with 'http', strip trailing dots,
        and return (set_of_urls, joined_value_string).
        """
        extractor = URLExtract(cache_dir=os.environ.get("CACHE_DIR"))
        urls = extractor.find_urls(text_with_urls)
        urls.extend(UrlValidator._extract_http_texts(text_with_urls))
        # remove dots at the end and deduplicate
        urls = set(url[:-1] if url.endswith(".") else url for url in urls)
        value = ", ".join(urls)
        return urls, value

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

        urls, value = UrlValidator._extract_and_normalize_urls(text_with_urls)

        for url in urls:
            if url.startswith("http"):
                try:
                    response_code = UrlValidator._status_code_from_request(url)
                    if response_code == 200:
                        if url.startswith("http://"):
                            secure_url = url.replace("http://", "https://")
                            if UrlValidator._status_code_from_request(secure_url) == 200:
                                result = {
                                    "url": url,
                                    "error": f"The url{url} is secure. Please use 'https' instead of 'http'.",
                                }
                                results.append(result)
                          
                        else:
                            continue
                    else:
                        result = {"url": url, "error": f"Status code {response_code}"}
                        results.append(result)
                except requests.ConnectionError:
                    result = {"url": url, "error": f"The URL {url} does not exist on Internet."}
                    results.append(result)
                
        if results:
            validity = False
            value = results

        return {"valid": validity, "value": value}

    @staticmethod
    @if_arg
    def protocol_checks(text_with_urls):
        """
        Checks the ftp included in `text_with_urls`
        Args:
           text_with_urls (str, required): The text that contains ftp
        Returns:
            (dict) An object with the validity of the check and the instance/results
        """

        results = []

        validity = True

        urls, value = UrlValidator._extract_and_normalize_urls(text_with_urls)

        for url in urls:
            if url.startswith("ftp://"):
                results.append({
                    "url": url,
                    "error": f"The URL {url} exists"
                })

        if results:
            validity = False
            value = results

        return {"valid": validity, "value": value}

    @staticmethod
    @if_arg
    def secure_url_checks(text_with_urls):
        """
        Checks whether the secure link (https) is included in `text_with_urls`
        Args:
           text_with_urls (str, required): The text that contains https
        Returns:
            (dict) An object with the validity of the check and the instance/results
        """

        results = []

        validity = True

        urls, value = UrlValidator._extract_and_normalize_urls(text_with_urls)

        for url in urls:
            if url.startswith("http://"):
                results.append({
                    "url": url,
                    "error": f"The URL {url} is not secure"
                })

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
        if doi.strip().startswith("10."):  # doi always starts with "10."
            url = f"https://www.doi.org/{doi}"
            valid = UrlValidator.health_and_status_check(url).get("valid")
        return {"valid": valid, "value": doi}

    @staticmethod
    @if_arg
    def doi_link_update(value, bad_urls):
        validity = True
        if value in bad_urls:
            validity = False

        return {"valid": validity, "value": value}
    
    @staticmethod
    @if_arg
    def url_update_email_check(url, bad_urls=None):
        if bad_urls is None:
            bad_urls = []

        if not url:
            return {
                "valid": False,
                "value": url,
                "message": "No email value provided for URL update contact.",
                "remediation": "Provide a valid contact email address."
            }
         
        validity = True
        # Check if the URL matches 'support-cddis@earthdata.nasa.gov'
        if url in bad_urls or url == "support-cddis@earthdata.nasa.gov":
            # Update the URL
            url = "support-cddis@nasa.gov"
            validity = False  # Mark as invalid if the URL was updated
        return {"valid": validity, "value": url}
