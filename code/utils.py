def prepare_received_gcmd_keywords_list(*args):
        keywords_lists_unordered = [arg for arg in args if arg is not None]
        ordered_keyword_list = list(zip(*keywords_lists_unordered))
        received_keywords = []
        for keywords in ordered_keyword_list:
            received_keywords.append(
                # converting the keywords to uppercase and
                # stripping any whitespaces for consistency
                # stripping any extra slashes in case there's no value for the field
                '/'.join([keyword.upper().strip() for keyword in keywords]).strip('/')
            )
        return received_keywords

def prepare_gcmd_keywords_dict(all_keywords):
    combined_keywords = {}
    for row in all_keywords:
        # converting the keywords to lowercase and
        # stripping any whitespaces for consistency
        keyword = '/'.join([keyword.upper().strip() for keyword in row[:-1]])
        keyword = keyword.strip('/')
        # making it a dict to make it more efficient to check for values
        combined_keywords[keyword] = True
    return combined_keywords