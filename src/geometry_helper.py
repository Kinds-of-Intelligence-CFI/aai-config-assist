import numpy as np


def calculate_vertices_of_axis_aligned_rectangle(centroid, width, height):
    """Returns the coordinates of the vertices a, b, c, d (top left, top right, bottom right, bottom left)
       centroid: coordinates of centroid, numpy array 2x1
       width, height: int/float"""
    half_width = 0.5 * width
    half_height = 0.5 * height

    a = centroid + np.array([-half_width, half_height])
    b = centroid + np.array([half_width, half_height])
    c = centroid + np.array([half_width, -half_height])
    d = centroid + np.array([-half_width, -half_height])

    return a, b, c, d


def calculate_clockwise_rotated_2d_point(point, angle_deg):
    """Returns the new coordinates of a point, rotated by a clockwise angle in degrees
       point: original coordinates, numpy array 2x1
       angle_deg: int/float expressed in degrees"""

    angle = np.deg2rad(angle_deg)

    # Note: this is for clockwise 2d rotation, not for the more common anticlockwise counterpart
    rotation_mat = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])

    rotated_point = np.matmul(rotation_mat, point)

    return rotated_point


if __name__ == "__main__":
    # Rotating a point in a 2d plane
    original_point = np.array([2, 2])
    angle_degrees = 90
    new_point = calculate_clockwise_rotated_2d_point(point=original_point, angle_deg=angle_degrees)
    print(new_point)

    # Calculating the vertices of an axis-aligned rectangle from centroid, width, and height
    centroid1 = np.array([0, 0])
    height1 = 2
    width1 = 2
    vertices1 = calculate_vertices_of_axis_aligned_rectangle(centroid=centroid1, width=width1, height=height1)
    print(vertices1)



