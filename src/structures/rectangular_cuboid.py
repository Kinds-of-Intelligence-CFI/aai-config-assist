from typing import Dict, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt

from src.utils.geometry_helper import calculate_vertices_of_rotated_rectangle


class RectangularCuboid:
    """A rectangular cuboid, defined by its centroid, size, and rotation of its lower base.

    Note:
        - This class was written to be compatible with the preexisting conventions of Animal-AI (AAI).
        - Hence length is AAI's x-direction, width is AAI's z-direction, and height is AAI's y-direction.
        - The only rotation possible for this object is a height-wise, "yaw"-type rotation of the lower base rectangle.
        - The lower base face is always parallel to the 2d plane made up of the 1st and 2nd dimensions of the 3d space.
    """

    X_INDEX = 0
    Z_INDEX = 1
    Y_INDEX = 2
    RED_COMPONENT_INDEX = "r"
    GREEN_COMPONENT_INDEX = "g"
    BLUE_COMPONENT_INDEX = "b"

    def __init__(
        self,
        lower_base_centroid: npt.NDArray,
        dimensions: Tuple,
        rotation: float,
        name: str = "Cuboid",
        colour: Optional[Dict] = None,
    ) -> None:
        """Constructs an instance of RectangularCuboid.

        Args:
            lower_base_centroid (np.ndarray): The length (AAI-x), width (AAI-z), and height (AAI-y) coordinates of the
                lower base's centroid.
            dimensions (tuple): The length (AAI-x), width (AAI-z), and height (AAI-y) of the cuboid.
            rotation (float): The clockwise angle of rotation of the rectangle, given in degrees.
            name (str): Name of the item.
            colour (dict or None): Colour of the item, e.g. {"r": 256, "g": 256, "b": 0}.
        """
        # TODO: Decide on way to address necessity for float array for AAI sliders not to auto adjust
        #  this is a temporary fix to catch non-float arrays.
        #  perhaps eventually we can distinguish between an AAIRectangularCuboid and a base RectangularCuboid
        #  whereby the AAI one requires floating dtype for the lower_base_centroid; to avoid having this strict
        #  enforcement for a generic cuboid that could be non-AAI. Could also handle more gracefully here by
        #  checking for incorrect type and auto changing. But will stick to this for now to realise which parts
        #  of the code are constructing RectangularCuboid objects with non-float arg for lower_base_centroid param.
        if lower_base_centroid.dtype != np.float_:
            arr_dtype = lower_base_centroid.dtype
            raise Exception(
                f"The lower_base_centroid variable should be an array of floats. You are using {arr_dtype}"
            )

        self.center = lower_base_centroid
        self.length = dimensions[self.X_INDEX]
        self.width = dimensions[self.Z_INDEX]
        self.height = dimensions[self.Y_INDEX]
        self.deg_rotation = rotation
        self.name = name
        self.colour = colour

        # The following function works in a 2d planar world. Hence, its definitions of width and height are not the same
        # as those defined in the 3d world (see this class's docstring).
        # The length of the 3d item = the width of the 2d item & the width of the 3d item = the height of the 2d item.
        # This is why the arguments provided below may seem to be in conflict with their parameter names.
        # The center should be only the 2d centroid coordinates, hence the clipping of the 3rd dimension with [:2].
        self.lower_base_vertices = calculate_vertices_of_rotated_rectangle(
            center=self.center[:2],
            width=self.length,
            height=self.width,
            angle_deg=self.deg_rotation,
        )

    def resize(
        self,
        resized_length: Union[float, None] = None,
        resized_width: Union[float, None] = None,
        resized_height: Union[float, None] = None,
    ) -> None:
        """Resizes the cuboid, including calculating and setting the coordinates of its new vertices.

        Args:
            resized_length (float or None): The new length (AAI-x).
            resized_width(float or None): The new width (AAI-z).
            resized_height (float or None): The new height (AAI-y).
        """
        self.length = self.length if resized_length is None else resized_length
        self.width = self.width if resized_width is None else resized_width
        self.height = self.height if resized_height is None else resized_height
        new_vertices = calculate_vertices_of_rotated_rectangle(
            center=self.center[:2],
            width=self.length,
            height=self.width,
            angle_deg=self.deg_rotation,
        )
        self.lower_base_vertices = new_vertices

    @property
    def center_x(self):
        return self.center[self.X_INDEX]

    @center_x.setter
    def center_x(self, value):
        self.center[self.X_INDEX] = value

    @property
    def center_z(self):
        return self.center[self.Z_INDEX]

    @center_z.setter
    def center_z(self, value):
        self.center[self.Z_INDEX] = value

    @property
    def center_y(self):
        return self.center[self.Y_INDEX]

    @center_y.setter
    def center_y(self, value):
        self.center[self.Y_INDEX] = value

    @property
    def colour_red(self):
        return self.colour[self.RED_COMPONENT_INDEX]

    @property
    def colour_green(self):
        return self.colour[self.GREEN_COMPONENT_INDEX]

    @property
    def colour_blue(self):
        return self.colour[self.BLUE_COMPONENT_INDEX]
