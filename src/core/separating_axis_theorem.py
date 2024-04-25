import numpy as np

from src.utils.geometry_helper import *


def apply_separating_axis_theorem(rec_cuboid1, rec_cuboid2, verbose=True, overlap_decimals=3):
    """Determines whether two rectangles overlap and, if so, the minimum translation vector (mtv) to overcome overlap.

    The mtv will be the 0 vector if the rectangles do not overlap.

    Args:
        rec_cuboid1 (RectangularCuboid): An object of type RectangularCuboid.
        rec_cuboid2 (RectangularCuboid): An object of type RectangularCuboid.
        verbose (bool): Descriptive print statements if True, none if False.
        overlap_decimals (int): Decimal precision that overlap values and vectors are printed with.

    Returns:
        (np.ndarray): The minimum translation vector to overcome overlap between the two cuboids (0 vec, if no overlap)
    """
    # Check whether the items overlap in the depth-direction
    depth_segment1 = np.array([rec_cuboid1.center[2], rec_cuboid1.center[2] + rec_cuboid1.height])
    depth_segment2 = np.array([rec_cuboid2.center[2], rec_cuboid2.center[2] + rec_cuboid2.height])
    depth_overlap = determine_overlap_between_aligned_segments(depth_segment1, depth_segment2)

    if np.isclose(a=depth_overlap, b=0):
        # If the items do not overlap in depth direction, then they could be stacked but not overlapping
        mtv = np.array([0, 0])
        return mtv

    # Start by assuming overlap until assumption is proven wrong
    do_overlap = True

    # Prepare the possible separation axes candidates
    # Store the possible axes in a set to avoid checking the same axis twice
    possible_separation_axes = set()
    for cuboid in [rec_cuboid1, rec_cuboid2]:
        ax1, ax2 = get_potential_separation_axes(cuboid.deg_rotation)
        possible_separation_axes.add(ax1)
        possible_separation_axes.add(ax2)

    # Store the non-zero overlap values per axis in the format {axis: overlap} e.g. {(0, 1): 2, (1, 0): 1.5}
    overlaps = {}

    # Main loop
    for axis in possible_separation_axes:
        # Get min and max projection values of each rectangle on this axis
        min1, max1 = get_min_max_projections(rec_cuboid1.lower_base_vertices, axis)
        min2, max2 = get_min_max_projections(rec_cuboid2.lower_base_vertices, axis)
        segment1 = np.array([min1, max1])
        segment2 = np.array([min2, max2])

        # Check overlap of rectangles on this axis
        overlap = determine_overlap_between_aligned_segments(segment1, segment2)

        overlaps[axis] = overlap

        # This function ensures that any overlap value under 1e-08 is not recorded as an overlap
        # Though, may want to know when items are overlapping even a tiny bit, so could revert to: if overlap == 0
        if np.isclose(overlap, 0):
            do_overlap = False

    # Get the minimum overlap axis and value if the rectangles overlap
    if do_overlap:
        min_overlap_distance = min(overlaps.values())
        min_overlap_vector = [key for key in overlaps if overlaps[key] == min_overlap_distance][0]
        mtv = min_overlap_distance * np.array(min_overlap_vector)

        if verbose:
            print(f"Overlap between {rec_cuboid1.name} and {rec_cuboid2.name}")
            # print(f"* The minimum overlap distance is: {min_overlap_distance}")
            # print(f"* The minimum overlap unit vector is: {min_overlap_vector}")
            # print(f"* The minimum translation vector is hence their product: {mtv}")
            print(f"* Must move the objects away simultaneously by "
                  f"{round_up(mtv[0], overlap_decimals)} in the x-dir "
                  f"and {round_up(mtv[1], overlap_decimals)} in the z-dir "
                  f"(or, alternatively, by {depth_overlap} in the y-dir)"
                  )
            print("")
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


# TODO: put the examples from below into the docstrings (in the correct doctest format)

if __name__ == "__main__":
    from src.structures.rectangular_cuboid import RectangularCuboid
    # Rectangular Cuboid 1
    center1 = np.array([2, 3.5, 5])
    dimensions1 = (1, 2, 3)
    rotation1 = 315
    name1 = "Cuboid 1"
    colour1 = {"r": 0, "g": 100, "b": 50}
    rectangular_cuboid1 = RectangularCuboid(center1, dimensions1, rotation1, name1, )
    print(f"Rectangular cuboid 1 vertices:\n{rectangular_cuboid1.lower_base_vertices}\n")
    
    # Rectangular Cuboid 2
    center2 = np.array([2, 3.5, 5])
    dimensions2 = (2, 2, 3)
    rotation2 = 325
    name2 = "Cuboid 2"
    colour2 = {"r": 0, "g": 200, "b": 50}
    rectangular_cuboid2 = RectangularCuboid(center2, dimensions2, rotation2, name2, )
    print(f"Rectangular cuboid 2 vertices:\n{rectangular_cuboid2.lower_base_vertices}\n")

    # Determine the possible separation axes
    possible_sep_axes = set()
    for rectangle in [rectangular_cuboid1, rectangular_cuboid2]:
        axis1, axis2 = get_potential_separation_axes(rectangle.deg_rotation)
        possible_sep_axes.add(axis1)
        possible_sep_axes.add(axis2)
    print(f"Possible separation axes:\n{possible_sep_axes}\n")

    mtv = apply_separating_axis_theorem(rectangular_cuboid1, rectangular_cuboid2)

    # Defining a Rectangular Cuboid
    lower_base_centroid = np.array([1, 2, 3])
    dimensions = (2, 2, 3)
    rotation = 45
    rec_cuboid = RectangularCuboid(lower_base_centroid, dimensions, rotation)
