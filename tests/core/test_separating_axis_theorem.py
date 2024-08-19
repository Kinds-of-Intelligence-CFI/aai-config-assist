import unittest

from src.core.separating_axis_theorem import *

# Run in terminal to get per test breakdown: python -m unittest -v tests/core/separating_axis_theorem.py


class TestSeparatingAxisTheorem(unittest.TestCase):
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
        expected = (
            np.array([0.70710678, -0.70710678]),
            np.array([0.70710678, 0.70710678]),
        )
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
        expected = (
            np.array([0.70710678, 0.70710678]),
            np.array([-0.70710678, 0.70710678]),
        )
        result = get_potential_separation_axes(deg_angle=theta)
        self.assertTrue(np.all(np.isclose(expected, result)))
