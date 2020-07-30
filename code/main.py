from downloader import Downloader
from validator import Validator


def main(concept_id):
    downloader = Downloader(concept_id)
    content = downloader.download()
    validator = Validator(downloader.metadata_format)

    validation_results = validator.validate(content)

    from pprint import pprint
    pprint(validation_results)

    return validation_results


if __name__ == "__main__":
    main("C1339230297-GES_DISC")
