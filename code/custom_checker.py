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
    def _get_path_value_recursively(subset_of_metadata_content, path, container):
        """
        Gets the path values recursively while handling list or dictionary in `subset_of_metadata_content`
        Adds the values to `container`

        Args:
            subset_of_metadata_content (dict or list or str): 
                        The value of the field at a certain point;
                        changes during each level of recursion
            path (list): The path of the field as a list
                         Example: 'Collection/RangeDateTime/StartDate' ->
                                  ['Collection', 'RangeDateTime', 'StartDate']
            container (set): The container that holds all the path values
        """

        try:
            root_content = subset_of_metadata_content[path[0]]
        except KeyError as e:
            return
        new_path = path[1:]
        if isinstance(root_content, str) or isinstance(root_content, int):
            container.add(root_content)
        elif isinstance(root_content, list):
            for each in root_content:
                try:
                    CustomChecker._get_path_value_recursively(
                        each, new_path, container)
                except KeyError as e:
                    continue
        elif isinstance(root_content, dict):
            CustomChecker._get_path_value_recursively(
                root_content, new_path, container)

    @staticmethod
    def _get_path_value(content_to_validate, path):
        """
        Gets the value of the field from the metadata (input_json)

        Args:
            path (str): The path of the field. Example: 'Collection/RangeDateTime/StartDate'

        Returns:
            (bool, set) If the path exists, (True, set of values of the path);
                        else (False, empty set)
        """

        container = set()

        path = path.split('/')
        CustomChecker._get_path_value_recursively(
            content_to_validate, path, container)
        # TODO: Handle cases where there are multiple values for the field
        return container

    def run(self, content_to_validate, field, func):
        """
        Runs the custom check based on `func` to the `content_to_validate`'s `field` path

        Args:
            content_to_validate (dict): The metadata content
            field (str): The field path
            func (function): The function reference to the check

        Returns:
            (dict): The result of the check in the form:
            {
                "valid": "Validity status (bool)",
                "value": "The instance value/s"
            }
        """
        fields = field["fields"]
        field_values = []
        relation = field.get("relation")
        result = {
            "valid": None
        }
        # REVIEWERS: better way to do this?
        if len(fields) == 1:
            value = CustomChecker._get_path_value(
                content_to_validate, fields[0])
            if value:
                field_values.append(
                    list(value)[0]
                )
        else:
            for _field in fields:
                value = CustomChecker._get_path_value(
                    content_to_validate, _field)
                if value:
                    field_values.append(
                        list(value)[0]
                    )
        if field_values:
            result = func(*field_values, relation)
        return result
