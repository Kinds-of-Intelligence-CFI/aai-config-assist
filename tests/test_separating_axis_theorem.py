import unittest
from src.separating_axis_theorem import *
import numpy as np


class TestSeparatingAxisTheorem(unittest.TestCase):
    # def test_apply_separating_axis_theorem(self):
    #     # # Rectangle 1
    #     # center1 = np.array([2, 3.5])
    #     # width1 = 3
    #     # height1 = 2.5
    #     # rotation1 = 315
    #     # rectangle1 = Rectangle(center1, width1, height1, rotation1)
    #     # print(f"Rectangle 1 vertices:\n{rectangle1.vertices}\n")
    #     #
    #     # # Rectangle 2
    #     # center2 = np.array([3.5, 2])
    #     # width2 = 2.5
    #     # height2 = 2
    #     # rotation2 = 45
    #     # rectangle2 = Rectangle(center2, width2, height2, rotation2)
    #     # print(f"Rectangle 2 vertices:\n{rectangle2.vertices}\n")

    def test_get_potential_separation_axes_when_theta_is_0(self):
        theta = 0
        expected = (np.array([1, 0]), np.array([0, 1]))
        result = get_potential_separation_axes(deg_angle=theta)
        self.assertTrue(np.all(np.isclose(expected, result)))

    def test_get_potential_separation_axes_when_theta_is_positive(self):
        # Remember theta is defined in the clockwise direction, so with theta = 45, the first axis
        #  corresponds to a vector pointing rightward and downward on a standard 2d x-y plane. When normalised,
        #  this unit vector is [0.70710678, -0.70710678].
        # The second axis is normal and obtained by a 90 degree ANTI-clockwise rotation from the first and
        #  hence corresponds to a vector pointing rightward and upward on a standard 2d x-y plane. When normalised,
        #  this unit vector is: ([0.70710678, 0.70710678])
        theta = 45
        expected = (np.array([0.70710678, -0.70710678]), np.array([0.70710678, 0.70710678]))
        result = get_potential_separation_axes(deg_angle=theta)
        self.assertTrue(np.all(np.isclose(expected, result)))

    def test_get_potential_separation_axes_when_theta_is_negative(self):
        # Remember theta is defined in the clockwise direction, so with theta = -45, the first axis
        #  corresponds to a vector pointing rightward and upward on a standard 2d x-y plane. When normalised,
        #  this unit vector is [0.70710678, 0.70710678].
        # The second axis is normal and obtained by a 90 degree ANTI-clockwise rotation from the first and
        #  hence corresponds to a vector pointing leftward and upward on a standard 2d x-y plane. When normalised,
        #  this unit vector is: ([0.70710678, 0.70710678])
        theta = -45
        expected = (np.array([0.70710678, 0.70710678]), np.array([-0.70710678, 0.70710678]),)
        result = get_potential_separation_axes(deg_angle=theta)
        self.assertTrue(np.all(np.isclose(expected, result)))
