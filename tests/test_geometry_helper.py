import unittest

import numpy

from src.utils.geometry_helper import *

# Run in terminal to get per test breakdown: python -m unittest -v tests/test_geometry_helper.py


class TestGeometryHelper(unittest.TestCase):
    def test_calculate_vertices_of_rotated_rectangle_when_rotation_is_0(self):
        centroid = np.array([0, 0])
        height = 4
        width = 2
        rotation = 0

        expected = np.array([[-1, 2],
                             [1, 2],
                             [1, -2],
                             [-1, -2]
                             ])

        result = calculate_vertices_of_rotated_rectangle(center=centroid, width=width,
                                                         height=height, angle_deg=rotation)

        self.assertTrue(np.all(np.isclose(expected, result)), "The rotated lower_base_vertices are not as expected.")

    def test_calculate_vertices_of_rotated_rectangle_when_rotation_is_positive_and_centroid_is_not_at_origin(self):
        x_centroid = 1
        y_centroid = -3

        centroid = np.array([x_centroid, y_centroid])
        height = 2
        width = 2
        rotation = +45

        sqrt_2 = np.sqrt(2)
        expected = np.array([[0, sqrt_2],
                             [sqrt_2, 0],
                             [0, -sqrt_2],
                             [-sqrt_2, 0]
                             ])

        expected[:, 0] += x_centroid
        expected[:, 1] += y_centroid

        result = calculate_vertices_of_rotated_rectangle(center=centroid, width=width,
                                                         height=height, angle_deg=rotation)

        self.assertTrue(np.all(np.isclose(expected, result)), "The rotated lower_base_vertices are not as expected.")

    def test_calculate_vertices_of_rotated_rectangle_when_rotation_is_negative(self):
        centroid = np.array([0, 0])
        height = 4
        width = 2
        rotation = -90

        expected = np.array([[-2, -1],
                             [-2, 1],
                             [2, 1],
                             [2, -1]
                             ])

        result = calculate_vertices_of_rotated_rectangle(center=centroid, width=width,
                                                         height=height, angle_deg=rotation)

        self.assertTrue(np.all(np.isclose(expected, result)), "The rotated lower_base_vertices are not as expected.")

    def test_calculate_vertices_of_axis_aligned_rectangle(self):
        x_centroid = 1
        y_centroid = -3

        centroid = np.array([x_centroid, y_centroid])
        height = 2
        width = 2

        expected = np.array([[-1, 1],
                             [1, 1],
                             [1, -1],
                             [-1, -1]
                             ])

        expected[:, 0] += x_centroid
        expected[:, 1] += y_centroid

        result = calculate_vertices_of_axis_aligned_rectangle(center=centroid, width=width, height=height)

        self.assertTrue(np.all(np.isclose(expected, result)), "The rotated lower_base_vertices are not as expected.")

    def test_calculate_clockwise_rotated_2d_point(self):
        original_points = np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]])
        angle = 45
        sqrt_2 = np.sqrt(2)

        expected = np.array([[0, sqrt_2],
                             [sqrt_2, 0],
                             [0, -sqrt_2],
                             [-sqrt_2, 0]
                             ])

        result = calculate_clockwise_rotated_2d_points(points=original_points, angle_deg=angle)

        self.assertTrue(np.all(np.isclose(expected, result)))

    def test_determine_overlap_between_aligned_segments_spanning_positive_and_negative_subset_of_real_axis(self):
        seg1 = np.array([-1, 3])
        seg2 = np.array([2, 5])
        expected = 1
        result = determine_overlap_between_aligned_segments(seg1, seg2)
        self.assertTrue(np.isclose(expected, result))

    def test_determine_overlap_between_aligned_segments_in_negative_subset_of_real_axis(self):
        seg1 = np.array([-9, -4])
        seg2 = np.array([-7, -5])
        expected = 2
        result = determine_overlap_between_aligned_segments(seg1, seg2)
        self.assertTrue(np.isclose(expected, result))

    def test_get_min_max_projections(self):
        points = np.array([[0, 1],
                           [0, 0.5],
                           [1, 0],
                           [-1, 0],
                           [0, -0.5],
                           [0, -1]])
        sqrt_2 = np.sqrt(2)
        axis = np.array([1 / sqrt_2, 1 / sqrt_2])
        expected = np.array([-1 / sqrt_2, 1 / sqrt_2])
        result = get_min_max_projections(points, axis)
        self.assertTrue(np.all(np.isclose(expected, result)))

    def test_get_projected_distance_of_2d_points_onto_axis(self):
        points = np.array([[0, 1],
                           [1, 0]])
        sqrt_2 = np.sqrt(2)
        axis = np.array([1 / sqrt_2, 1 / sqrt_2])
        expected = np.array([1 / sqrt_2, 1 / sqrt_2])
        result = get_projected_distance_of_2d_points_onto_axis(points, axis)
        self.assertTrue(np.all(np.isclose(expected, result)))

    def test_normalise_vector(self):
        vec = np.array([1, 1])
        sqrt_2 = np.sqrt(2)
        expected = np.array([1 / sqrt_2, 1 / sqrt_2])
        result = normalise_vector(vec)
        self.assertTrue(np.all(np.isclose(expected, result)))
