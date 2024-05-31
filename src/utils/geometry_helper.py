from typing import Tuple, Callable

import numpy as np
import numpy.typing as npt

# These are the proportions of the x (width in this module) and z (height in this module) components
# that the non-rectangular object thicknesses occupy with respect to the overall shape dimensions
SMALL_RATIO = 0.25
LARGE_RATIO = 0.75


def calculate_vertices_of_rotated_rectangle(center: npt.NDArray,
                                            width: float,
                                            height: float,
                                            angle_deg: float) -> npt.NDArray:
    """Calculates the 4 vertex coordinates of a rectangle in the x-y plane rotated about its centroid.

    Args:
        center (np.ndarray): The x and y coordinates of the rectangle's centroid.
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.
        angle_deg (float): The clockwise angle of rotation of the rectangle, given in degrees.

    Returns:
        np.ndarray: Array (4, 2) containing the 4 x and y coordinate pairs of the rotated rectangle's lower_base_vertices. The
            array gives the rotated coordinates of the top-left, top-right, bottom-right, bottom-left lower_base_vertices of the
            original, un-rotated rectangle.
    """
    vertices = calculate_vertices_of_axis_aligned_rectangle(center, width, height)
    rotated_vertices = calculate_clockwise_rotated_2d_points(vertices, angle_deg, center)
    return rotated_vertices


def calculate_vertices_of_axis_aligned_rectangle(center: npt.NDArray, width: float, height: float) -> npt.NDArray:
    """Calculates the 4 vertex coordinates of a rectangle whose sides are aligned with the x and y axes.

    Args:
        center (np.ndarray): The x and y coordinates of the rectangle's centroid.
        width (float): The width of the rectangle.
        height (float): The height of the rectangle.

    Returns:
      np.ndarray: Array (4x2) containing the 4 x and y coordinate pairs of the rectangle lower_base_vertices.
    """
    half_width = 0.5 * width
    half_height = 0.5 * height

    a = center + np.array([-half_width, half_height])
    b = center + np.array([half_width, half_height])
    c = center + np.array([half_width, -half_height])
    d = center + np.array([-half_width, -half_height])

    vertices = np.array([a, b, c, d])
    return vertices


def calculate_vertices_of_rotated(center: npt.NDArray,
                                  width: float,
                                  height: float,
                                  angle_deg: float,
                                  get_vertices: Callable = calculate_vertices_of_axis_aligned_rectangle) -> npt.NDArray:
    vertices = get_vertices(center, width, height)
    rotated_vertices = calculate_clockwise_rotated_2d_points(vertices, angle_deg, center)
    return rotated_vertices


# TODO: methods specific to LBlock can be moved to the LBlock class if it gets created (same for all specific shapes)
def calculate_vertices_of_rotated_l_block(center: npt.NDArray,
                                          width: float,
                                          height: float,
                                          angle_deg: float) -> npt.NDArray:
    return calculate_vertices_of_rotated(center,
                                         width,
                                         height,
                                         angle_deg,
                                         calculate_vertices_of_axis_aligned_l_block)


def calculate_vertices_of_axis_aligned_l_block(center: npt.NDArray, width: float, height: float) -> npt.NDArray:
    # TODO: the magic numbers below are approximations of AAI item dimensions
    a, b, c, d = calculate_vertices_of_axis_aligned_rectangle(center, width, height)
    c1 = b + np.array([0, - SMALL_RATIO * height])
    c2 = c1 + np.array([- LARGE_RATIO * width, 0])
    c3 = c2 + np.array([0, - (c2[1] - d[1])])
    return np.array([a, b, c1, c2, c3, d])


def calculate_vertices_of_rotated_u_block(center: npt.NDArray,
                                          width: float,
                                          height: float,
                                          angle_deg: float) -> npt.NDArray:
    return calculate_vertices_of_rotated(center,
                                         width,
                                         height,
                                         angle_deg,
                                         calculate_vertices_of_axis_aligned_u_block)


def calculate_vertices_of_axis_aligned_u_block(center: npt.NDArray, width: float, height: float) -> npt.NDArray:
    # TODO: the magic numbers below are approximations of AAI item dimensions
    a, b, c, d = calculate_vertices_of_axis_aligned_rectangle(center, width, height)
    c1 = c
    c2 = c1 + np.array([- SMALL_RATIO * width, 0])
    c3 = c2 + np.array([0, + LARGE_RATIO * height])
    c4 = c3 + np.array([-0.5 * width, 0])
    c5 = c4 + np.array([0, - LARGE_RATIO * height])
    return np.array([a, b, c1, c2, c3, c4, c5, d])


def calculate_vertices_of_rotated_j_block(center: npt.NDArray,
                                          width: float,
                                          height: float,
                                          angle_deg: float) -> npt.NDArray:
    return calculate_vertices_of_rotated(center,
                                         width,
                                         height,
                                         angle_deg,
                                         calculate_vertices_of_axis_aligned_j_block)


def calculate_vertices_of_axis_aligned_j_block(center: npt.NDArray, width: float, height: float) -> npt.NDArray:
    a, _, c, d = calculate_vertices_of_axis_aligned_rectangle(center, width, height)
    b1 = a + np.array([SMALL_RATIO * width, 0])
    b2 = b1 + np.array([0, - LARGE_RATIO * height])
    b3 = b2 + np.array([LARGE_RATIO * width, 0])
    return np.array([a, b1, b2, b3, c, d])


def calculate_clockwise_rotated_2d_points(points: npt.NDArray,
                                          angle_deg: float,
                                          center_of_rotation: npt.NDArray = np.array([0, 0])) -> npt.NDArray:
    """Calculates the new coordinates of 2d points rotated by a given angle about a center of rotation.

    Args:
        points (np.ndarray): The x and y coordinates of all the points to be rotated, stacked vertically.
            If N points are provided, the array will be of dimension (N, 2).
        angle_deg (float): The clockwise angle of rotation of the points, given in degrees.
        center_of_rotation (np.ndarray): The x and y coordinates of the center of rotation.

    Returns:
        np.ndarray: The x and y coordinates of all the rotated points.
    """
    # Translate the points by center_of_rotation
    points -= center_of_rotation

    # Perform the rotation
    angle = np.deg2rad(angle_deg)
    # Note: this is for clockwise 2d rotation, not for the more common anticlockwise counterpart
    rotation_mat = np.array([
        [np.cos(angle), np.sin(angle)],
        [-np.sin(angle), np.cos(angle)]
    ])
    rotated_points = np.matmul(rotation_mat, points.T).T

    # Reverse the translation by center_of_rotation
    rotated_points += center_of_rotation
    return rotated_points


def determine_overlap_between_aligned_segments(segment1: npt.NDArray, segment2: npt.NDArray) -> float:
    """Determines the overlap value between segments 1 and 2.

    Each segment is defined by a min and max value corresponding to their start and stop points on the same line.

    Args:
        segment1 (np.ndarray): The min and max values of segment 1 along a common line, in an array of dimension (1, 2)
        segment2 (np.ndarray): The min and max values of segment 2 along a common line, in an array of dimension (1, 2)

    Returns:
        float: The overlap distance between the two inputted segments.
    """
    start1, stop1 = min(segment1), max(segment1)
    start2, stop2 = min(segment2), max(segment2)
    overlap = max(0, min(stop2, stop1) - max(start2, start1))
    return overlap


def get_min_max_projections(points: npt.NDArray, axis: npt.NDArray) -> Tuple[float, float]:
    """Computes the minimum and maximum projection values of the inputted points onto an axis.

    This is equivalent to the boundaries of the total projection distance covered by a polygon when all of its
    lower_base_vertices (defined in points), are projected onto a vector (defined as axis).

    Args:
        points (np.ndarray): The x and y coordinates of all the points to be rotated, stacked vertically.
            If N points are provided, the array will be of dimension (N, 2).
        axis (np.ndarray): A normalised axis defined by an x and y coordinate given in an array of dimension (1, 2).

    Returns:
        tuple(float, float): The minimum and maximum values of the projections of all inputted points onto the axis.
    """
    projections = get_projected_distance_of_2d_points_onto_axis(points, axis)
    min_distance = min(projections)
    max_distance = max(projections)
    return min_distance, max_distance


def get_projected_distance_of_2d_points_onto_axis(points: npt.NDArray, axis: npt.NDArray) -> npt.NDArray:
    """Compute the projected distance (the dot product) of a set of points onto an axis.

    Args:
        points (np.ndarray): The x and y coordinates of all the points to be rotated, stacked vertically.
            If N points are provided, the array will be of dimension (N, 2).
        axis (np.ndarray): A normalised axis defined by an x and y coordinate given in an array of dimension (1, 2).

    Returns:
        np.ndarray: The distances obtained from projecting the inputted points onto the inputted axis. The resulting
            array has the same dimension as the inputted points array.
    """
    # TODO: decide whether to normalise here or not
    # axis = normalise_vector(axis)
    projected_points = np.dot(points, axis)
    return projected_points


def normalise_vector(vec: npt.NDArray) -> npt.NDArray:
    """Normalises a vector.

    Args:
        vec (np.ndarray): An array of component values, as many values as the dimensionality of the vector space.

    Returns:
        np.ndarray: A normalised vector whose component values sum to 1.
    """
    normalised_vec = vec / np.linalg.norm(vec)
    return normalised_vec


def round_up(val: float, num_decimals: int) -> float:
    """Rounds up a number to a number of decimals.

    Args:
        val (float): The original number.
        num_decimals (int): The number of decimals after which rounding should occur.


    Examples:
        >>> round_up(4.1231, 2)
        4.13

    Returns:
        (float): The rounded number.
    """
    factor = 10 ** num_decimals
    new_val = np.ceil(val * factor) / factor
    return new_val


if __name__ == "__main__":
    def geometry_helper_example() -> None:
        print("* Calculating the rotated lower base vertices of a rectangle from center, width, height, and rotation "
              "(deg)")
        centroid2 = np.array([0, 0])
        height2 = 2
        width2 = 2
        rotation2 = 45
        vertices2 = calculate_vertices_of_rotated_rectangle(center=centroid2, width=width2,
                                                            height=height2, angle_deg=rotation2)
        print(f"Shape of final vertices: {np.shape(vertices2)}")
        print(f"Final vertices:\n{vertices2}")
        print("")

        print("* Calculating the lower_base_vertices of an axis-aligned rectangle from center, width, and height")
        centroid1 = np.array([0, 0])
        height1 = 2
        width1 = 2
        vertices1 = calculate_vertices_of_axis_aligned_rectangle(center=centroid1, width=width1, height=height1)
        print(f"Shape of vertices: {np.shape(vertices1)}")
        print(f"Vertices:\n{vertices1}")
        print("")

        print("* Rotating points in a 2d plane")
        original_point = np.array([[-1, 1], [1, 1], [1, -1], [-1, -1]])
        angle_degrees = 45
        new_points = calculate_clockwise_rotated_2d_points(points=original_point, angle_deg=angle_degrees)
        print(f"Shape of new points: {np.shape(new_points)}")
        print(f"New points:\n{new_points}")
        print("")

        print("* Normalise an axis vector")
        axis = np.array([1, -1])
        normalised_axis = normalise_vector(axis)
        print(f"Normalised axis 0th component: {normalised_axis[0]}")
        print(f"Manually normalised axis 0th component: {(normalised_axis / np.linalg.norm(normalised_axis))[0]}")
        # TODO: strangely, approximation of the float makes this check false, though the formula in the function is
        #  correct
        print(f"Equality between norm vecs: {normalised_axis == normalised_axis / np.linalg.norm(normalised_axis)}")
        print("")

        print("* Project a points onto an axis")
        points = np.array([[4, 1], [4, 1], [5, 1], [6, 2], [-1, 5]])
        new_axis = np.array([1, -1])
        normalised_new_axis = normalise_vector(new_axis)
        new_points = get_projected_distance_of_2d_points_onto_axis(points, normalised_new_axis)
        print(f"New points: {new_points}")
        print("")

        print("* Get min and max values of projected points onto an axis")
        points = np.array([[4, 1], [4, 1], [5, 1], [6, 2], [-1, 5]])
        new_axis = np.array([1, -1])
        normalised_new_axis = normalise_vector(new_axis)
        min_val, max_val = get_min_max_projections(points, normalised_new_axis)
        print(f"Min and max vals: {min_val, max_val}")
        print("")

        print("* Determine the overlap between two segments")
        segment1 = np.array([-1, 2])
        segment2 = np.array([-3, 1])
        overlap = determine_overlap_between_aligned_segments(segment1, segment2)
        print(f"Overlap: {overlap}")


    geometry_helper_example()
    import doctest

    doctest.testmod()
