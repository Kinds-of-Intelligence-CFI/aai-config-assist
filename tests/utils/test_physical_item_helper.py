import unittest

import yaml

from src.utils.physical_item_helper import *


class TestPhysicalItemHelper(unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Get the default item parameters
        with open("src/definitions/item_default_parameters.yaml", "r") as file:
            self.default_item_parameters = yaml.safe_load(file)

    def test_get_default_item_parameter(self):
        result = get_default_item_parameter(item_name="GoodGoal",
                                            param_name="colour",
                                            default_item_parameters=self.default_item_parameters)
        expected = {"r": 0, "g": 256, "b": 0}
        assert (result == expected, "The expected default colour did not match the result")

    def test_get_default_item_parameter_with_nonexistent_item_name(self):
        with self.assertRaises(KeyError):
            get_default_item_parameter(item_name="ThisIsNotAnItemName",
                                       param_name="colour",
                                       default_item_parameters=self.default_item_parameters)

    def test_get_default_item_parameter_with_nonexistent_param_name(self):
        with self.assertRaises(KeyError):
            get_default_item_parameter(item_name="GoodGoal",
                                       param_name="ThisIsNotAParamName",
                                       default_item_parameters=self.default_item_parameters)

    def test_set_item_name_from(self):
        expected = "Wall 7"
        result = set_item_name_from("Wall", 7)
        assert expected == result
