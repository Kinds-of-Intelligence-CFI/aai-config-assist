from dataclasses import dataclass
import numpy as np
from geometry_helper import *


def apply_separating_axis_theorem(rectangle1, rectangle2):
    """Returns minimum translation vector for possibly overlapping rectangles 1 and 2"""
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

        if overlap != 0:
            overlaps[axis] = overlap

    # Get the minimum overlap axis and value if the rectangles overlap
    if overlaps:
        min_overlap = np.inf
        dir_min_overlap = None
        for k in overlaps.keys():
            if overlaps[k] < min_overlap:
                min_overlap = overlaps[k]
                dir_min_overlap = k
    else:
        # The overlaps dict is empty: there were no overlaps
        min_overlap = 0
        dir_min_overlap = None

    return dir_min_overlap, min_overlap

def get_potential_separation_axes(deg_angle):
    """We will define the separation axes (with all angles in degrees) as:
       - the axis defined by the rectangle rotation theta
       - the axis defined by theta + 90 [360]; that's 'modulo 360'

       Indeed, for a rectangle, the SAT algorithm defines the only possible separation axes
       as the axis defined by its angle of rotation and the axis normal to that one.

       Note, the potential separation axes should be normalised. This is immediately achieved
       by defining the axes components as the trigonometric function outputs, as done below"""

    rad_angle1 = np.deg2rad(deg_angle)
    rad_angle2 = np.deg2rad((deg_angle + 90) % 360)

    # Note the axes are returned as tuples to be hashable and hence inputtable into a set
    ax1 = (np.cos(rad_angle1), np.sin(rad_angle1))
    ax2 = (np.cos(rad_angle2), np.sin(rad_angle2))

    return ax1, ax2


class Rectangle:
    def __init__(self, center, width, height, deg_rotation):
        self.center = center
        self.width = width
        self.height = height
        self.deg_rotation = deg_rotation
        self.vertices = calculate_vertices_of_rotated_rectangle(center, width, height, deg_rotation)


if __name__ == "__main__":
    # Rectangle 1
    center1 = np.array([2, 3.5])
    width1 = 3
    height1 = 2.5
    rotation1 = 315
    rectangle1 = Rectangle(center1, width1, height1, rotation1)
    print(rectangle1.vertices)

    # Rectangle 2
    center2 = np.array([3.5, 2])
    width2 = 2.5
    height2 = 2
    rotation2 = 45
    rectangle2 = Rectangle(center2, width2, height2, rotation2)
    print(rectangle2.vertices)

    # Determine the possible separation axes
    possible_separation_axes = set()
    for rectangle in [rectangle1, rectangle2]:
        ax1, ax2 = get_potential_separation_axes(rectangle.deg_rotation)
        possible_separation_axes.add(ax1)
        possible_separation_axes.add(ax2)
    # print(possible_separation_axes)

    dir_min_overlap, overlap_val = apply_separating_axis_theorem(rectangle1, rectangle2)
    print(dir_min_overlap)
    print(overlap_val)
    mtv = overlap_val * np.array(dir_min_overlap)
    print(mtv)
    print(f"To overcome overlap you will have to move either item simultaneously by {abs(mtv[0])} in the x-drection "
          f"and by {abs(mtv[1])} in the y-direction")

    print("Exit ok")
