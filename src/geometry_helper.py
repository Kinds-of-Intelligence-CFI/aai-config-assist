import numpy as np


def calculate_vertices_of_rotated_rectangle(centroid, width, height, angle_deg):
    vertices = calculate_vertices_of_axis_aligned_rectangle(centroid, width, height)
    rotated_vertices = calculate_clockwise_rotated_2d_point(vertices, angle_deg)
    return rotated_vertices


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

    vertices = np.array([a, b, c, d])
    return vertices


def calculate_clockwise_rotated_2d_point(points, angle_deg):
    """Returns the new coordinates of points(s), rotated by a clockwise angle in degrees
       points: original coordinates, numpy array nx2 with n, the number of points
       angle_deg: int/float expressed in degrees"""

    angle = np.deg2rad(angle_deg)

    # Note: this is for clockwise 2d rotation, not for the more common anticlockwise counterpart
    rotation_mat = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])

    rotated_point = np.matmul(rotation_mat, points.T)
    return rotated_point.T

def get_min_max_projections(points, axis):
    """Returns the minimum and maximum projection values of all the points onto axis"""
    projections = get_projected_distance_of_2d_points_onto_axis(points, axis)
    min_distance = min(projections)
    max_distance = max(projections)
    return min_distance, max_distance

def get_projected_distance_of_2d_points_onto_axis(points, axis):
    """Returns the distance along the axis points: original coordinates, numpy array nx2 with n, the number of points
       axis: unit (normalised!) vector defining the axis, 2x1 numpy array"""
    # TODO: decide whether to normalise here or not
    # axis = normalise_vector(axis)
    projected_points = np.dot(points, axis)
    return projected_points


def normalise_vector(vec):
    normalised_vec = vec / np.linalg.norm(vec)
    return normalised_vec


if __name__ == "__main__":
    # Calculating the rotated vertices of a rectangle from centroid, width, height, and rotation in degrees
    centroid2 = np.array([0, 0])
    height2 = 2
    width2 = 2
    rotation2 = 45
    vertices2 = calculate_vertices_of_rotated_rectangle(centroid=centroid2, width=width2,
                                                        height=height2, angle_deg=rotation2)
    print(np.shape(vertices2))
    print(vertices2)

    # Calculating the vertices of an axis-aligned rectangle from centroid, width, and height
    centroid1 = np.array([0, 0])
    height1 = 2
    width1 = 2
    vertices1 = calculate_vertices_of_axis_aligned_rectangle(centroid=centroid1, width=width1, height=height1)
    print(np.shape(vertices1))
    print(vertices1)

    # Rotating a points in a 2d plane
    original_point = np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]])
    angle_degrees = 45
    new_points = calculate_clockwise_rotated_2d_point(points=original_point, angle_deg=angle_degrees)
    print(np.shape(new_points))
    print(new_points)

    # Normalise an axis vector
    axis = np.array([1, -1])
    normalised_axis = normalise_vector(axis)
    print(normalised_axis[0])
    print((normalised_axis / np.linalg.norm(normalised_axis))[0])

    # TODO: strangely, approximation of the float makes this check false, though the formula in the function is correct
    print(normalised_axis == normalised_axis / np.linalg.norm(normalised_axis))

    # Project a points onto an axis
    points = np.array([[4, 1], [4, 1], [5, 1]])
    new_axis = np.array([1, -1])
    normalised_new_axis = normalise_vector(new_axis)
    new_points = get_projected_distance_of_2d_points_onto_axis(points, normalised_new_axis)
    print(new_points)