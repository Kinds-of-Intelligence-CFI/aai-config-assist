from dataclasses import dataclass
import numpy as np
from src.geometry_helper import *


def apply_separating_axis_theorem(rectangle1, rectangle2, verbose=True):
    """Determines whether two rectangles overlap and, if so, the minimum translation vector (mtv) to overcome overlap.

    The mtv will be the 0 vector if the rectangles do not overlap.

    Args:
        rectangle1 (Rectangle): An object of type Rectangle defined by its size, vertex coordinates, and rotation value.
        rectangle2 (Rectangle): An object of type Rectangle defined by its size, vertex coordinates, and rotation value.

    Returns:
        (tuple): The direction (list or tuple or np.ndarray) and magnitude (float) of overlap.
    """
    # Start by assuming overlap until assumption is proven wrong
    do_overlap = True

    # Prepare the possible separation axes candidates
    # Store the possible axes in a set to avoid checking the same axis twice
    possible_separation_axes = set()
    for rectangle in [rectangle1, rectangle2]:
        ax1, ax2 = get_potential_separation_axes(rectangle.deg_rotation)
        possible_separation_axes.add(ax1)
        possible_separation_axes.add(ax2)

    # Store the non-zero overlap values per axis in the format {axis: overlap} e.g. {(0, 1): 2, (1, 0): 1.5}
    overlaps = {}

    # Main loop
    for axis in possible_separation_axes:
        # Get min and max projection values of each rectangle on this axis
        min1, max1 = get_min_max_projections(rectangle1.vertices, axis)
        min2, max2 = get_min_max_projections(rectangle2.vertices, axis)
        segment1 = np.array([min1, max1])
        segment2 = np.array([min2, max2])

        # Check overlap of rectangles on this axis
        overlap = determine_overlap_between_aligned_segments(segment1, segment2)

        overlaps[axis] = overlap

        if overlap == 0:
            do_overlap = False

    # Get the minimum overlap axis and value if the rectangles overlap
    if do_overlap:
        min_overlap_distance = min(overlaps.values())
        min_overlap_vector = [key for key in overlaps if overlaps[key] == min_overlap_distance][0]
        mtv = min_overlap_distance * np.array(min_overlap_vector)

        if verbose:
            print(f"Comparing {rectangle1.name} and {rectangle2.name}")
            print(f"* The minimum overlap distance is: {min_overlap_distance}")
            print(f"* The minimum overlap unit vector is: {min_overlap_vector}")
            print(f"* The minimum translation vector is hence their product: {mtv}\n")
    else:
        # There is no overlap, and hence no distance to be covered in either direction
        mtv = np.array([0, 0])

        # if verbose:
        #     print(f"* No overlap was found and hence the minimum translation vector is: {mtv}\n")

    return mtv


def get_potential_separation_axes(deg_angle):
    """Computes the potential separation axes from the angle of rotation of a rectangle.

    We will define the separation axes (with all angles in degrees) as:
       - the axis defined by the rectangle rotation theta
       - the axis defined by theta + 90 [360]; that's 'modulo 360'

    Indeed, for a rectangle, the SAT algorithm defines the only possible separation axes
    as the axis defined by its angle of rotation and the axis normal to that one.

    Note, the potential separation axes should be normalised. This is immediately achieved
    by defining the axes components as the trigonometric function outputs, as done below.

    Args:
        deg_angle (float): The clockwise angle of rotation of the rectangle, from a starting horizontal state.

    Returns:
        (tuple): The two possible separation axes (each defined by a np.ndarray of shape (2, 1)) for the inputted angle.
    """
    # Flip the sign of deg_angle to account for clockwise rotation (trigonometric funcs assume anticlockwise rotation)
    deg_angle = - deg_angle
    rad_angle1 = np.deg2rad(deg_angle)
    rad_angle2 = np.deg2rad((deg_angle + 90) % 360)

    # Note the axes are returned as tuples to be hashable and hence placeable into a set
    ax1 = (np.cos(rad_angle1), np.sin(rad_angle1))
    ax2 = (np.cos(rad_angle2), np.sin(rad_angle2))

    return ax1, ax2


class Rectangle:
    """A rectangle defined by its center, width, height, and degree of rotation in a two dimensional plane."""

    def __init__(self, center, width, height, deg_rotation, depth=0, name=None):
        """Constructs an instance of Rectangle.

        Args:
            center (np.ndarray): The x and y coordinates of the rectangle's centroid.
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            deg_rotation (float): The clockwise angle of rotation of the rectangle, given in degrees.
            depth (float): The third dimension of an orthogonal parallelepiped.
            name (str): Name of the item.
        """
        self.center = center
        self.width = width
        self.height = height
        self.depth = depth
        self.deg_rotation = deg_rotation
        self.name = name
        self.vertices = calculate_vertices_of_rotated_rectangle(center, width, height, deg_rotation)


# TODO (the first 2 are needed and important but will take some refactoring):
#  - may want to rename Rectangle class to Orthogonal Parallelepiped because it now has a notion of depth
#    in this case, maybe it would be good to have a check at the end of apply_sat that just checks whether or
#    not, the depth axes overlap; because only if they do should the mvt be given. Can even have a routine checking
#    which overlap is smaller the depth (vertical, y in AAI) or the planar mtv from the arena flat plane and then return
#    that as the mtv.
#  - on that note, could even offload some of the logic in config_assistant by making it such that you can directly
#    pass the size and position objects as they are (no need to unpack before passing to OrthogonalParallelepiped)
#  - improve the efficiency and elegance of the logic in apply_sat function
#  - put the examples from below into the docstrings (in the correct doctest format)

if __name__ == "__main__":
    # Rectangle 1
    center1 = np.array([2, 3.5])
    width1 = 3
    height1 = 2.5
    rotation1 = 315
    rectangle1 = Rectangle(center1, width1, height1, rotation1)
    print(f"Rectangle 1 vertices:\n{rectangle1.vertices}\n")

    # Rectangle 2
    center2 = np.array([3.5, 2])
    width2 = 2.5
    height2 = 2
    rotation2 = 45
    rectangle2 = Rectangle(center2, width2, height2, rotation2)
    print(f"Rectangle 2 vertices:\n{rectangle2.vertices}\n")

    # Determine the possible separation axes
    possible_separation_axes = set()
    for rectangle in [rectangle1, rectangle2]:
        ax1, ax2 = get_potential_separation_axes(rectangle.deg_rotation)
        possible_separation_axes.add(ax1)
        possible_separation_axes.add(ax2)
    print(f"Possible separation axes:\n{possible_separation_axes}\n")

    mtv = apply_separating_axis_theorem(rectangle1, rectangle2)

    print("Exit ok")
