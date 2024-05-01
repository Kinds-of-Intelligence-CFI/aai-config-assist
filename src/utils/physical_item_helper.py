from typing import Dict


def get_default_item_parameter(item_name: str, param_name: str, default_item_parameters: Dict) -> Dict:
    """Provides the default parameter value of a particular Animal-AI item.

    Note:
        - Copied the default values from official Animal-AI repository at Arena-Objects.yaml.
        - Some default values were not available on the official repo and were inferred from the images.

    Args:
        default_item_parameters (dict): Dictionary of default item parameters from physical items definitions.
        item_name (str): Name of the physical Animal-AI item.
        param_name (str): Parameter type that is being requested (colour or size for the time being)

    Returns:
        (dict[str]): The components of the default colour for the inputted item.
    """
    item_name = item_name.split(" ")[0]

    param_name_to_keys = {"colour": ["r", "g", "b"],
                          "size": ["x", "y", "z"],
                          }

    try:
        param_keys = param_name_to_keys[param_name]
    except KeyError:
        raise KeyError(f"The parameter name {param_name} is not defined in the default definitions. "
                       f"Please add this category to the definitions to move on without errors.")

    try:
        default_values = default_item_parameters[item_name][param_name]
    except KeyError:
        # Eventually, could implement a custom exception to avoid repeating KeyError
        raise KeyError(f"The item {item_name}'s {param_name} value is not defined in the default definitions. "
                       f"Please add the value to the definitions to move on without errors.")

    return dict(zip(param_keys, default_values))


def set_item_name_from(type_name: str, item_ix: str) -> str:
    """Sets a name for an item from its type and index (e.g. if there are several walls)."""
    return f"{type_name} {item_ix}"
