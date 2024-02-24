import yaml
from src.arena_config_loader import ArenaConfigLoader
from src.separating_axis_theorem import Rectangle, RectangularCuboid, apply_separating_axis_theorem
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as RectangleMatplotlib  # Can remove renaming when SAT Rectangle is renamed
import os


class ConfigAssistant:
    """Assists in visualising and debugging Animal-AI configurations"""

    def __init__(self, config_path):
        """Constructs the ConfigAssistant class.

        Args:
            config_path (str): Path to YAML Animal-AI configuration file.
        """
        self.config_path = config_path
        self.config_data = self._load_config_data()
        self.physical_items = self._create_rectangular_cuboid_list()

    def check_config_overlap(self):
        """Displays a log of possible overlaps to the terminal."""
        cuboids = self.physical_items
        self._check_overlaps_between_cuboids(cuboids)

    def visualise_config(self):
        """Displays a 2d representation of the class configuration (seen from above)."""
        cuboids = self.physical_items
        self._visualise_cuboid_bases_plotly(cuboids)

    def _load_config_data(self):
        """Parses and loads the data from the YAML file inputted to class constructor.

        Returns:
            (dict): The loaded data.
        """
        with open(self.config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data

    def _check_overlaps_between_cuboids(self, cuboids):
        """Displays a log of possible overlaps to the terminal.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        N = len(cuboids)
        for i in range(N):
            for j in range(i + 1, N):
                item1 = cuboids[i]
                item2 = cuboids[j]
                apply_separating_axis_theorem(item1, item2)

    def _visualise_cuboid_bases_matplotlib(self, cuboids):
        """Displays a 2d representation (x-z/length-width plane) of a list of RectangularCuboid instances.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        fig = plt.figure()
        plt.xlim(0, 40.5)
        plt.ylim(0, 40.5)
        currentAxis = plt.gca()

        for cuboid in cuboids:
            center_of_rotation = tuple(cuboid.center[:2])

            # See RectangularCuboid class definition to understand why these permutations may seem contradictory
            width = cuboid.length
            height = cuboid.width

            name = cuboid.name
            anti_cw_rotation = - cuboid.deg_rotation
            colour_dict = cuboid.colour
            rgb_colour = (colour_dict["r"] / 256,
                          colour_dict["g"] / 256,
                          colour_dict["b"] / 256) if cuboid.colour is not None else self._get_default_item_colour(name)

            # Bottom left coordinates PRIOR TO ROTATION are needed for matplotlib.patches (get from centroid, as below)
            bottom_left = center_of_rotation + np.array([-0.5 * width, -0.5 * height])

            currentAxis.add_patch(RectangleMatplotlib(xy=bottom_left, width=width, height=height, edgecolor="k",
                                                      lw=1, alpha=0.3, rotation_point=center_of_rotation,
                                                      angle=anti_cw_rotation, facecolor=rgb_colour))
            plt.text(x=bottom_left[0] + 0.5 * width, y=bottom_left[1] + 0.5 * height, s=f"{name}")
        plt.show()

    def _visualise_cuboid_bases_plotly(self, cuboids):
        """Displays a 2d representation (x-z/length-width plane) of a list of RectangularCuboid instances.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.update_xaxes(range=[-1, 41], showgrid=True)
        fig.update_yaxes(range=[-1, 41], showgrid=True)


        for cuboid in cuboids:
            center_of_rotation = tuple(cuboid.center[:2])

            # See RectangularCuboid class definition to understand why these permutations may seem contradictory
            width = cuboid.length
            height = cuboid.width

            name = cuboid.name
            colour_dict = cuboid.colour
            rgb_colour = (colour_dict["r"],
                          colour_dict["g"],
                          colour_dict["b"]) if cuboid.colour is not None else self._get_default_item_colour(name)

            r, g, b = rgb_colour
            opa = 0.4

            # Concatenation because need to provide first element back to path for shape contour to be complete
            # See first example of https://plotly.com/python/shapes/
            x_path = np.concatenate((cuboid.lower_base_vertices[:, 0], np.reshape(cuboid.lower_base_vertices[0, 0], newshape=(1,))))
            y_path = np.concatenate((cuboid.lower_base_vertices[:, 1], np.reshape(cuboid.lower_base_vertices[0, 1], newshape=(1,))))

            fig.add_trace(go.Scatter(x=x_path,
                                     y=y_path,
                                     fill="toself",
                                     line=dict(color=f"rgba({0}, {0}, {0}, {1})", width=1,),
                                     fillcolor=f"rgba({r}, {g}, {b}, {opa})",
                                     name=name,
                                     marker=dict(opacity=0)
                                     ),
                          )

        fig.show()

    def _get_default_item_colour(self, item_name):
        """Provides the default colour of a particular Animal-AI item.

        Args:
            item_name (str): Name of the physical Animal-AI item.

        Returns:
            (tuple): The red, green, blue (rgb) components of the default colour for the inputted item.
        """
        # These are placeholders until I get the exact colours for the Animal-AI items
        item_colour_dict = {
            "GoodGoal": (0, 256, 0),
            "GoodGoalBounce": (0, 256, 0),
            "BadGoal": (256, 0, 0),
            "BadGoalBounce": (256, 0, 0),
            "GoodGoalMulti": (0, 256, 256),
            "GoodGoalMultiBounce": (0, 256, 256),
            "DeathZone": (256, 0, 0),
            "HotZone": (255, 165, 0),
            "CardBox1": (200, 200, 200),
            "CardBox2": (200, 200, 200),
            "UObject": (200, 200, 200),
            "LObject": (200, 200, 200),
            "LObject2": (200, 200, 200),
            "WallTransparent": (50, 50, 50)
        }

        item_name = item_name.split(" ")[0]

        default_colour = item_colour_dict.get(item_name, (10, 10, 100))

        return default_colour

    def _create_rectangular_cuboid_list(self):
        """Creates a list of RectangularCuboid instances corresponding to the objects in the configuration data.

        Returns:
            (list): The RectangularCuboid instances.
        """
        rec_cuboids = []

        # Extract the item_types from the configuration file and omit the agent
        item_types = self.config_data["arenas"][0]["items"]

        # For every item type
        for i, items in enumerate(item_types):
            num_items = len(items["positions"])

            # For every item in the item type
            for j in range(num_items):
                # Extract the useful data
                name = self._set_item_name_from(type_name=items["name"], item_ix=j)
                position = items["positions"][j]
                rotation = items["rotations"][j] if "rotations" in items else 0

                if "Agent" in name:
                    size = {"x": 1, "y": 1, "z": 1}
                    colour = {"r": 0, "g": 0, "b": 0}
                else:
                    size = items["sizes"][j]
                    colour = items["colors"][j] if "colors" in items else None

                # Transform some of the extracted data
                xzy_lower_base_centroid = np.array([position["x"], position["z"], position["y"]])
                xzy_dimensions = (size["x"], size["z"], size["y"])

                # Instantiate a RectangularCuboid with the extracted and transformed data
                rec_cuboid = RectangularCuboid(lower_base_centroid=xzy_lower_base_centroid,
                                               dimensions=xzy_dimensions,
                                               rotation=rotation,
                                               name=name,
                                               colour=colour
                                               )

                # Add this instance to the rectangular_cuboids list
                rec_cuboids += [rec_cuboid]

        return rec_cuboids

    def _set_item_name_from(self, type_name, item_ix):
        """Sets a name for an item from its type and index (e.g. if there are several walls)."""
        return f"{type_name} {item_ix}"

# TODO: eventually, can decouple the checking and plotting functionalities of this class

if __name__ == "__main__":
    config_path = os.path.join("example_configs", "config.yaml")
    config_assistant = ConfigAssistant(config_path)
    config_assistant.check_config_overlap()
    config_assistant.visualise_config()

    # # Visualising a single custom rectangular cuboid
    # lower_base_centroid = np.array([10, 20, 3])
    # dimensions = (10, 10, 30)
    # rotation = 45
    # rec_cuboid = [RectangularCuboid(lower_base_centroid, dimensions, rotation)]
    # config_assistant._visualise_cuboid_bases(rec_cuboid)

    print("Exit ok")
