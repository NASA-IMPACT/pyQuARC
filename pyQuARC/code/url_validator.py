import requests
import re

from .string_validator import StringValidator
from .utils import get_headers, if_arg


class UrlValidator(StringValidator):
    """
    Validator class for URLs
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def _extract_urls_from_texts(text_with_urls):
        """
        Extracts anything that matches web URLs -- http, https, and naked domains like "example.com". Reference: https://gist.github.com/gruber/8891611
        Args:
            text_with_urls (str, required): The text that contains the URLs
        Returns:
            (set) Set of unique urls from `text_with_urls`
        Examples:
            >>> text = "Check out this website: https://example.com"
            >>> _extract_urls_from_texts(text)
            ['https://example.com']
        """
        regex_pattern = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        return set(re.findall(regex_pattern, text_with_urls))

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

        def status_code_from_request(url):
            headers = get_headers()
            # timeout = 10 seconds, to allow for slow but not invalid connections
            return requests.get(url, headers=headers, timeout=10).status_code

        results = []

        validity = True

        urls = UrlValidator._extract_urls_from_texts(text_with_urls)

        value = ", ".join(urls)

        # check that URL returns a valid response
        for url in urls:
            if not url.startswith("http"):
                url = f"http://{url}"
            try:
                response_code = status_code_from_request(url)
                if response_code == 200:
                    if url.startswith("http://"):
                        secure_url = url.replace("http://", "https://")
                        if status_code_from_request(secure_url) == 200:
                            result = {
                                "url": url,
                                "error": "The URL is secure. Please use 'https' instead of 'http'.",
                            }
                    else:
                        continue
                else:
                    result = {"url": url, "error": f"Status code {response_code}"}
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

        return {"valid": validity, "Value": value}
