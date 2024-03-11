import yaml
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input, State, callback

from src.arena_config_loader import ArenaConfigLoader
from src.geometry_helper import calculate_vertices_of_rotated_rectangle
from src.separating_axis_theorem import RectangularCuboid, apply_separating_axis_theorem


class ConfigAssistant:
    """Assists in visualising and debugging Animal-AI configurations."""

    def __init__(self, config_path):
        """Constructs the ConfigAssistant class.

        Args:
            config_path (str): Path to YAML Animal-AI configuration file.
        """
        self.config_path = config_path
        self.config_data = self._load_config_data()
        self.physical_items = self._create_rectangular_cuboid_list()
        self.names_items_with_overlap = []

    def check_config_overlap(self):
        """Displays a log of possible overlaps to the terminal."""
        cuboids = self.physical_items
        self.names_items_with_overlap = self._check_overlaps_between_cuboids(cuboids)

    def visualise_config(self):
        """Displays a 2d representation of the class configuration (seen from above)."""
        cuboids = self.physical_items
        self._run_dash_app_cuboid_visualisation(cuboids)

    def _load_config_data(self):
        """Parses and loads the data from the YAML file inputted to class constructor.

        Returns:
            (dict): The loaded data.
        """
        with open(self.config_path) as file:
            config_data = yaml.load(file, Loader=ArenaConfigLoader)
        return config_data

    @staticmethod
    def _check_overlaps_between_cuboids(cuboids):
        """Displays a log of possible overlaps to the terminal.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.

        Returns:
            (set[str]): Names of the items which have an overlap.
        """
        items_with_overlap = set()

        n = len(cuboids)
        for i in range(n):
            for j in range(i + 1, n):
                item1 = cuboids[i]
                item2 = cuboids[j]
                mtv = apply_separating_axis_theorem(item1, item2)

                # If there is an overlap, add the items in question
                if not np.all(np.isclose(mtv, np.array([0, 0]))):
                    items_with_overlap.add(item1.name)
                    items_with_overlap.add(item2.name)

        return items_with_overlap

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

            currentAxis.add_patch(Rectangle(xy=bottom_left, width=width, height=height, edgecolor="k",
                                            lw=1, alpha=0.3, rotation_point=center_of_rotation,
                                            angle=anti_cw_rotation, facecolor=rgb_colour))
            plt.text(x=bottom_left[0] + 0.5 * width, y=bottom_left[1] + 0.5 * height, s=f"{name}")
        plt.show()

    def _run_dash_app_cuboid_visualisation(self, cuboids):
        """Launches Dash application to visualise cuboids.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        # Initial figure
        fig_init = self._visualise_cuboid_bases_plotly(cuboids)

        # TODO: think about how to handle this more gracefully (not really a class
        #  attribute)
        # Initialise the item to be moved
        self.idx_item_to_move = 0

        def get_custom_dcc_slider(pos):
            slider = dcc.Slider(id="x-slider", min=0, max=40, step=0.1, value=pos, marks=None,
                                tooltip={"placement": "top",
                                         "always_visible": True,
                                         "template": "x = {value}",
                                         "style": {"fontSize": "15px"}})
            return slider

        # Create a Dash application for more interactivity
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Graph(figure=fig_init, id='aai-diagram', style={"height": "100vh"}),
            dcc.Slider(id="x-slider", min=0, max=40, step=0.1, value=0, marks=None,
                       tooltip={"placement": "top",
                                "always_visible": True,
                                "template": "x = {value}",
                                "style": {"fontSize": "15px"}}),
            dcc.Slider(id="y-slider", min=0, max=40, step=0.1, value=0, marks=None,
                       tooltip={"placement": "top",
                                "always_visible": True,
                                "template": "y = {value}",
                                "style": {"fontSize": "15px"}}),
            html.Div(id='app_id')
        ])

        # Creates a callback mechanism for when one of the items is selected to be moved
        @callback(
            Output(component_id='x-slider', component_property="value"),
            Output(component_id='y-slider', component_property="value"),
            Input(component_id='aai-diagram', component_property='clickData'),
            prevent_initial_call=True
        )
        def update_sliders(point_clicked):
            """Updates the sliders when one of the items is selected to be moved."""
            if point_clicked is not None:
                self.idx_item_to_move = point_clicked['points'][0]["curveNumber"]
                print(f"You have just clicked: {cuboids[self.idx_item_to_move].name}")
                return cuboids[self.idx_item_to_move].center[0], cuboids[self.idx_item_to_move].center[1]

            else:
                print("You have not clicked an item")
                return 0, 0

        # Creates a callback mechanism for when the sliders are being used to move items
        @callback(
            Output(component_id='aai-diagram', component_property='figure'),
            Input(component_id="x-slider", component_property="value"),
            Input(component_id="y-slider", component_property="value"),
            prevent_initial_call=True
        )
        def update_plot(x_slider_value,
                        y_slider_value):
            """Updates the plot when dash detects user interaction.

            Note:
                - The function arguments come from the component property of the Input.
            """
            idx_item_to_move = self.idx_item_to_move
            # Update the cuboid center coordinates
            cuboids[idx_item_to_move].center[0] = x_slider_value
            cuboids[idx_item_to_move].center[1] = y_slider_value

            cuboids[idx_item_to_move].lower_base_vertices = calculate_vertices_of_rotated_rectangle(
                center=np.array([x_slider_value, y_slider_value]),
                width=cuboids[idx_item_to_move].length,
                height=cuboids[idx_item_to_move].width,
                angle_deg=cuboids[idx_item_to_move].deg_rotation)

            print(f"You have just clicked: {cuboids[idx_item_to_move].name}")
            fig = self._visualise_cuboid_bases_plotly(cuboids)

            return fig

        app.run(port=8000)

    def _visualise_cuboid_bases_plotly(self, cuboids):
        """Displays a 2d representation (x-z/length-width plane) of a list of RectangularCuboid instances.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        # Configure the figure environment and add an arena rectangle
        fig = go.Figure()
        fig.update_xaxes(range=[-2, 42], showgrid=False, zeroline=False, visible=True)
        fig.update_yaxes(range=[-2, 42], showgrid=False, zeroline=False, visible=True)

        # To add an arena border
        fig.add_shape(type="rect",
                      x0=0, y0=0, x1=40, y1=40,
                      line=dict(color=f"rgba({100}, {100}, {100}, {1})", width=1.5, dash=None),
                      fillcolor=f"rgba({255}, {224}, {130}, {0.1})"
                      )
        # To make the axes equal (the cells square)
        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
        )

        for cuboid in cuboids:
            name = cuboid.name
            colour_dict = cuboid.colour
            rgb_colour = (colour_dict["r"],
                          colour_dict["g"],
                          colour_dict["b"]) if cuboid.colour is not None else self._get_default_item_colour(name)

            r, g, b = rgb_colour
            opa = 0.35

            # Concatenation because need to provide first element back to path for shape contour to be complete
            # See first example of https://plotly.com/python/shapes/
            x_path = np.concatenate(
                (cuboid.lower_base_vertices[:, 0], np.reshape(cuboid.lower_base_vertices[0, 0], newshape=(1,))))
            y_path = np.concatenate(
                (cuboid.lower_base_vertices[:, 1], np.reshape(cuboid.lower_base_vertices[0, 1], newshape=(1,))))

            # If this an item with an overlap, make its border red and make its width thicker
            if name in self.names_items_with_overlap:
                line_col = f"rgba({256}, {0}, {0}, {1})"
                line_width = 1.5

            # Else, keep its border black and standard thickness
            else:
                line_col = f"rgba({0}, {0}, {0}, {1})"
                line_width = 1

            fig.add_trace(go.Scatter(x=x_path,
                                     y=y_path,
                                     fill="toself",
                                     line=dict(color=line_col, width=line_width, ),
                                     fillcolor=f"rgba({r}, {g}, {b}, {opa})",
                                     name=name,
                                     marker=dict(opacity=0)
                                     ),
                          )

        # Temporarily disabled for Dash app development
        # fig.show()

        return fig

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

    @staticmethod
    def _get_default_item_colour(item_name):
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
            "GoodGoalMulti": (0, 256, 0),
            "GoodGoalMultiBounce": (0, 256, 0),
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

    @staticmethod
    def _set_item_name_from(type_name, item_ix):
        """Sets a name for an item from its type and index (e.g. if there are several walls)."""
        return f"{type_name} {item_ix}"


# TODO: eventually, can decouple the checking and plotting functionalities of this class

if __name__ == "__main__":
    # # Checking and visualising an entire configuration file
    configuration_path = os.path.join("example_configs", "config.yaml")
    config_assistant = ConfigAssistant(configuration_path)
    config_assistant.check_config_overlap()
    config_assistant.visualise_config()

    # # Visualising a single custom rectangular cuboid
    # lower_base_centroid = np.array([10, 20, 3])
    # dimensions = (10, 10, 30)
    # rotation = 45
    # rec_cuboid = [RectangularCuboid(lower_base_centroid, dimensions, rotation)]
    # # config_assistant._visualise_cuboid_bases_plotly(rec_cuboid)
    # config_assistant._run_dash_app_cuboid_visualisation(rec_cuboid)
