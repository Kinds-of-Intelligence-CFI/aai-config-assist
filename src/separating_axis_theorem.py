from dataclasses import dataclass
import numpy as np
from geometry_helper import *


# def apply_separating_axis_theorem(rectangle1, rectangle2):
#     """Returns minimum translation vector for possibly overlapping rectangles 1 and 2"""
#     # Store the possible axes in a set to avoid checking the same axis twice
#     possible_separation_axes = set()
#     for rectangle in [rectangle1, rectangle2]:
#         ax1, ax2 = get_potential_separation_axes(rectangle.deg_rotation)
#         possible_separation_axes.add(ax1)
#         possible_separation_axes.add(ax2)


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
    print(possible_separation_axes)

    # apply_separating_axis_theorem()
    print("Exit ok")
