from dataclasses import dataclass
import numpy as np
from geometry_helper import *


# def apply_separating_axis_theorem(rectangle1, rectangle2):
#     pass


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

    # apply_separating_axis_theorem()
    print("Exit ok")
