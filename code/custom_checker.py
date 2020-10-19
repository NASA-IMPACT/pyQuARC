class CustomChecker:
    """
    Class to implement custom checks
    """

    def __init__(self):
        """
        Args:
            content_to_validate (str): JSON string containing downloaded metadata
        """
        pass

    @staticmethod
    def _get_path_value_recursively(subset_of_metadata_content, path_list, container):
        """
        Gets the path values recursively while handling list or dictionary in `subset_of_metadata_content`
        Adds the values to `container`

        Args:
            subset_of_metadata_content (dict or list or str): 
                        The value of the field at a certain point;
                        changes during each level of recursion
            path_list (list): The path of the field as a list
                         Example: 'Collection/RangeDateTime/StartDate' ->
                                  ['Collection', 'RangeDateTime', 'StartDate']
            container (set): The container that holds all the path values
        """

        try:
            root_content = subset_of_metadata_content[path_list[0]]
        except KeyError as e:
            # this is needed because GCMD keywords check needs the placement 
            # of the values in the returned list
            container.append(" ")
            return
        new_path = path_list[1:]
        if isinstance(root_content, str) or isinstance(root_content, int):
            container.append(root_content)
        elif isinstance(root_content, list):
            for each in root_content:
                try:
                    CustomChecker._get_path_value_recursively(
                        each, new_path, container)
                except KeyError as e:
                    container.append(" ")
                    continue
        elif isinstance(root_content, dict):
            CustomChecker._get_path_value_recursively(
                root_content, new_path, container)

    @staticmethod
    def _get_path_value(content_to_validate, path_string):
        """
        Gets the value of the field from the metadata (input_json)

        Args:
            path_string (str): The path of the field. Example: 'Collection/RangeDateTime/StartDate'

        Returns:
            (bool, set) If the path exists, (True, set of values of the path);
                        else (False, empty set)
        """

        container = list()
        path = path_string.split('/')
        CustomChecker._get_path_value_recursively(
            content_to_validate, path, container)
        return container[0] if len(container) == 1 else container

    def run(self, func, content_to_validate, field_dict):
        """
        Runs the custom check based on `func` to the `content_to_validate`'s `field_dict` path

        Args:
            content_to_validate (dict): The metadata content
            field_dict (dict): The field dictionary of the form: 
                    {
                        "fields": relavant fields,
                        "relation": relation between the fields
                    }
            func (function): The function reference to the check

        Returns:
            (dict): The result of the check in the form:
            {
                "valid": "Validity status (bool)",
                "value": "The instance value/s"
            }
        """
        fields = field_dict["fields"]
        field_values = []
        relation = field_dict.get("relation")
        result = {
            "valid": None
        }
        for _field in fields:
            value = CustomChecker._get_path_value(
                content_to_validate, _field)
            field_values.append(value)
        # If relation is None, we don't want to pass it to the function
        arguments = [arg for arg in [*field_values, relation] if arg]
        if arguments[0] != " ": # Only if there is a value for a field
            result = func(*arguments)
        return result
