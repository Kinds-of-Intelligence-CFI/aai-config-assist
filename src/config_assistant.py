import yaml
import os
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
from dash import Dash, Output, Input, State, callback

from src.arena_config_dumper import ArenaConfigDumper
from src.arena_config_loader import ArenaConfigLoader
from src.separating_axis_theorem import RectangularCuboid, apply_separating_axis_theorem
from src.geometry_helper import calculate_vertices_of_rotated_rectangle
from src.app_setup import set_up_app_layout


class ConfigAssistant:
    """Assists in visualising and debugging Animal-AI configurations."""

    def __init__(self, config_path):
        """Constructs the ConfigAssistant class.

        Args:
            config_path (str): Path to YAML Animal-AI configuration file.
        """
        self.config_path = config_path

        # Get the default item parameters
        with open("definitions/item_default_parameters.yaml", "r") as file:
            self.default_item_parameters = yaml.safe_load(file)
        self.all_aai_item_names = list(self.default_item_parameters.keys())

        # Load and process the configuration data
        self.config_data = self._load_config_data()
        self.physical_items = self._create_rectangular_cuboid_list()
        self.names_items_with_overlap = []
        self.pass_mark = self.config_data["arenas"][0]["pass_mark"]
        self.t = self.config_data["arenas"][0]["t"]

    def check_config_overlap(self):
        """Displays a log of possible overlaps in the class configuration to the terminal."""
        cuboids = self.physical_items
        self.names_items_with_overlap = self._check_overlaps_between_cuboids(cuboids)

    def visualise_config(self):
        """Displays a 2d representation of the class configuration (seen from above)."""
        cuboids = self.physical_items  # Not a copy but points to the same object
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
        """Displays a log of possible overlaps in the cuboids list to the terminal.

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

    # TODO: review this method
    def _run_dash_app_cuboid_visualisation(self, cuboids):
        """Launches Dash application to visualise cuboids.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """

        # Initialise the item to be moved
        self.idx_item_to_move = 0
        self.num_auto_items_created = 0
        fig_init = self._visualise_cuboid_bases_plotly(cuboids)

        # Create a Dash application for more interactivity
        app = Dash(__name__,)
        app.layout = set_up_app_layout(fig_init, self.all_aai_item_names)

        # Creates a callback mechanism for when one of the items is selected to be moved
        @callback(
            Output(component_id='x-slider', component_property="value"),
            Output(component_id='y-slider', component_property="value"),
            Output(component_id='z-slider', component_property="value"),
            Output(component_id="xz-rotation-slider", component_property="value"),
            Input(component_id='aai-diagram', component_property='clickData'),
            prevent_initial_call=True
        )
        def update_sliders(point_clicked):
            """Updates the sliders when one of the items is selected to be moved."""
            if point_clicked is not None:
                print("you have clicked an item")
                self.idx_item_to_move = point_clicked['points'][0]["curveNumber"]
                print(f"You have just clicked: {cuboids[self.idx_item_to_move].name}")
                return (cuboids[self.idx_item_to_move].center[0],  # The x-direction
                        cuboids[self.idx_item_to_move].center[2],  # The y-direction
                        cuboids[self.idx_item_to_move].center[1],  # The z-direction
                        cuboids[self.idx_item_to_move].deg_rotation
                        )

            else:
                print("You have not clicked an item")
                return 0, 0, 0

        # Creates a callback mechanism for when the sliders are being used to move items
        # AND Creates a callback mechanism for spawning a new item into the arena and into the physical_items
        # These share a callback because Dash can only support one callback per unique output (here, the arena diagram)
        @callback(
            Output(component_id='aai-diagram', component_property='figure'),
            Input(component_id="x-slider", component_property="value"),
            Input(component_id="y-slider", component_property="value"),
            Input(component_id="z-slider", component_property="value"),
            Input(component_id="xz-rotation-slider", component_property="value"),
            State(component_id="item-dropdown", component_property="value"),
            Input(component_id='new-item-button', component_property="n_clicks"),
            State(component_id="spawn-x", component_property="value"),
            State(component_id="spawn-z", component_property="value"),
            State(component_id="spawn-y", component_property="value"),
            prevent_initial_call=True
        )
        def update_plot(x_slider_value,
                        y_slider_value,
                        z_slider_value,
                        xz_rotation,
                        item_dropdown_value,
                        num_auto_items_created,
                        spawn_x_dim,
                        spawn_z_dim,
                        spawn_y_dim, ):
            """Updates the plot when dash detects user interaction.

            Note:
                - The function arguments come from the component property of the Input.
            """
            # Must perform the spawning before the slider adjustment to avoid mistakenly reacting to the sliders
            # which the user may not have interacted with but will still be considered here as an input.
            # To avoid this behaviour, the self.idx_item_to_move is changed to that of the new item, in this if-branch.
            if num_auto_items_created != self.num_auto_items_created:
                # A new auto item is being spawned
                # Make the name something like {item_dropdown_value} + AUTO + n_clicks (shows which auto-spawn it was)
                # that way it will conserve uniqueness while still working for the dumper which just needs the first
                # word to be the same
                spawned_lower_base_centroid = np.array([0, 0, 0])

                # Fallback if user leaves the new item dimensions blank
                if spawn_x_dim == "":
                    spawn_x_dim = 1
                if spawn_z_dim == "":
                    spawn_z_dim = 1
                if spawn_y_dim == "":
                    spawn_y_dim = 1

                # Convert the dimensions (either str from callback or int from blank dimension fallback)
                spawned_dimensions = (float(spawn_x_dim), float(spawn_z_dim), float(spawn_y_dim))
                spawned_rotation = 0
                spawned_name = f"{item_dropdown_value} Auto {num_auto_items_created}"
                spawned_colour = self._get_default_item_parameter(item_name=item_dropdown_value, param_name="colour")
                spawned_auto_cuboid = RectangularCuboid(lower_base_centroid=spawned_lower_base_centroid,
                                                        dimensions=spawned_dimensions,
                                                        rotation=spawned_rotation,
                                                        name=spawned_name,
                                                        colour=spawned_colour
                                                        )
                self.physical_items += [spawned_auto_cuboid]
                self.num_auto_items_created = num_auto_items_created
                self.idx_item_to_move = -1
                xz_rotation = spawned_rotation
                print(f"You have just created: {spawned_name}")

            else:
                # Update the cuboid center coordinates
                # Note: when calling visualise_config, cuboids is the physical_items class attribute
                cuboids[self.idx_item_to_move].center[0] = x_slider_value
                cuboids[self.idx_item_to_move].center[2] = y_slider_value
                cuboids[self.idx_item_to_move].center[1] = z_slider_value
                cuboids[self.idx_item_to_move].deg_rotation = xz_rotation

            # Note that the center parameter expects the 2D planar values
            # AAI-x (cuboid[...].center[0]) and AAI-z (cuboid[...].center[1])
            cuboids[self.idx_item_to_move].lower_base_vertices = calculate_vertices_of_rotated_rectangle(
                center=np.array([cuboids[self.idx_item_to_move].center[0], cuboids[self.idx_item_to_move].center[1]]),
                width=cuboids[self.idx_item_to_move].length,
                height=cuboids[self.idx_item_to_move].width,
                angle_deg=xz_rotation)

            print(f"The item currently being moved is: {cuboids[self.idx_item_to_move].name}")
            self.check_config_overlap()
            fig = self._visualise_cuboid_bases_plotly(cuboids)

            return fig

        # Creates a callback mechanism for dumping the current physical items to a new configuration file
        arena = {"pass_mark": self.pass_mark, "t": self.t, "items": self.physical_items}
        arena_config_dumper = ArenaConfigDumper([arena], destination_file_path="")

        @callback(
            Output(component_id='new-config-path-output', component_property="value"),
            State(component_id="new-config-path", component_property="value"),
            Input(component_id='new-config-path-button', component_property="n_clicks"),
            prevent_initial_call=True
        )
        def dump_current_layout_to_config(new_config_path, n_clicks):
            if n_clicks > 0:
                arena_config_dumper.destination_file_path = new_config_path
                arena_config_dumper.dump()
                print(f"You have generated a new config YAML file at {new_config_path}.")
                return ""  # Empty the string after the process has completed

        app.run(port=8000)

    def _visualise_cuboid_bases_plotly(self, cuboids):
        """Displays a 2d representation (x-z/length-width plane) of a list of RectangularCuboid instances.

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        # Configure the figure environment and add an arena rectangle
        fig = go.Figure()
        fig.update_xaxes(range=[-1, 41], showgrid=False, zeroline=False, visible=True, )
        fig.update_yaxes(range=[-1, 41], showgrid=False, zeroline=False, visible=True, )

        # Add an Arena border
        fig.add_shape(type="rect",
                      x0=0, y0=0, x1=40, y1=40,
                      line=dict(color=f"rgba({100}, {100}, {100}, {1})", width=1.5, dash=None),
                      fillcolor=f"rgba({255}, {224}, {130}, {0.1})"
                      )

        # Make the axes equal to get a square arena
        fig.update_yaxes(scaleanchor="x", scaleratio=1, )

        for cuboid in cuboids:
            name = cuboid.name

            # Note: all AAI items should be coloured upon generating the item cuboid list; this fallback is simply
            # in place for non-AAI custom cuboids that may lack a colour attribute (see example main at file bottom).
            if cuboid.colour is not None:
                r, g, b = cuboid.colour["r"], cuboid.colour["g"], cuboid.colour["b"]
            else:
                r, g, b = 0, 0, 0

            # Concatenate because need to provide first element back to contour path for shape contour to be complete
            # See first example of https://plotly.com/python/shapes/
            x_path = np.concatenate(
                (cuboid.lower_base_vertices[:, 0], np.reshape(cuboid.lower_base_vertices[0, 0], newshape=(1,))))
            y_path = np.concatenate(
                (cuboid.lower_base_vertices[:, 1], np.reshape(cuboid.lower_base_vertices[0, 1], newshape=(1,))))

            if name in self.names_items_with_overlap:
                # Make overlapping item's border red and make its width thicker
                line_col = f"rgba({256}, {0}, {0}, {1})"
                line_width = 1.5
            else:
                # Keep non-overlapping item's border black and standard thickness
                line_col = f"rgba({0}, {0}, {0}, {1})"
                line_width = 1

            fig.add_trace(go.Scatter(x=x_path,
                                     y=y_path,
                                     fill="toself",
                                     line=dict(color=line_col, width=line_width, ),
                                     fillcolor=f"rgba({r}, {g}, {b}, {0.35})",
                                     name=name,
                                     marker=dict(opacity=0),
                                     showlegend=True,
                                     mode="lines",
                                     ),
                          )

            fig.update_layout(
                legend=dict(x=15,
                            y=1,
                            traceorder='normal',
                            font=dict(family='Helvetica', size=20, color='Black'),
                            bgcolor='rgba(231,235,235,0.5)',
                            bordercolor='black',
                            borderwidth=1,
                            orientation='v',
                            xanchor='left',
                            yanchor='top',
                            )
            )

        return fig

    def _visualise_cuboid_bases_matplotlib(self, cuboids):
        """Displays a 2d representation (x-z/length-width plane) of a list of RectangularCuboid instances (Deprecated).

        Args:
            cuboids (list[RectangularCuboid]): The RectangularCuboid instances to be visualised.
        """
        warnings.warn(f"Please note that you are calling the {self._visualise_cuboid_bases_matplotlib.__name__}"
                      f" method which is the previous version of the newer plotting method "
                      f"{self._visualise_cuboid_bases_plotly.__name__}.", DeprecationWarning)

        plt.figure()
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
            if cuboid.colour is not None:
                rgb_colour = (colour_dict["r"] / 256,
                              colour_dict["g"] / 256,
                              colour_dict["b"] / 256)
            else:
                rgb_colour = self._get_default_item_parameter(item_name=name, param_name="colour")

            # Bottom left coordinates prior to rotation are needed for matplotlib.patches (get from centroid, as below)
            bottom_left = center_of_rotation + np.array([-0.5 * width, -0.5 * height])

            currentAxis.add_patch(Rectangle(xy=bottom_left, width=width, height=height, edgecolor="k",
                                            lw=1, alpha=0.3, rotation_point=center_of_rotation,
                                            angle=anti_cw_rotation, facecolor=rgb_colour))
            plt.text(x=bottom_left[0] + 0.5 * width, y=bottom_left[1] + 0.5 * height, s=f"{name}")
        plt.show()

    def _create_rectangular_cuboid_list(self):
        """Creates a list of RectangularCuboid instances corresponding to the objects in the configuration data.

        Returns:
            (list[RectangularCuboid]): The RectangularCuboid instances.
        """
        rec_cuboids = []
        item_types = self.config_data["arenas"][0]["items"]

        # For every item type
        for i, items in enumerate(item_types):
            # Check whether the item type is valid
            if items["name"] not in self.all_aai_item_names:
                raise Exception(f"The name {items['name']} that you have provided "
                                f"is not in the default items list.")
            num_items = len(items["positions"])

            # For every item in the item type
            for j in range(num_items):
                # Extract the useful data
                name = self._set_item_name_from(type_name=items["name"], item_ix=j)
                position = items["positions"][j]
                rotation = items["rotations"][j] if "rotations" in items else 0
                size = items["sizes"][j] if "sizes" in items else self._get_default_item_parameter(name, "size")
                colour = items["colors"][j] if "colors" in items else self._get_default_item_parameter(name, "colour")

                # Transform parts of the extracted data
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

    def _get_default_item_parameter(self, item_name, param_name):
        """Provides the default parameter value of a particular Animal-AI item.

        Note:
            - Copied the default values from official Animal-AI repository at Arena-Objects.yaml.
            - Some default values were not available on the official repo and were inferred from the images.

        Args:
            item_name (str): Name of the physical Animal-AI item.
            param_name (str): Parameter type that is being requested (colour or size for the time being)

        Returns:
            (dict[str]): The components of the default colour for the inputted item.
        """
        item_name = item_name.split(" ")[0]

        param_name_to_keys = {"colour": ["r", "g", "b"],
                              "size": ["x", "y", "z"],
                              }
        param_keys = param_name_to_keys[param_name]

        try:
            default_values = self.default_item_parameters[item_name][param_name]
        except KeyError:
            # Eventually, could implement a custom exception to avoid repeating KeyError
            raise KeyError(f"The item {item_name}'s {param_name} value is not defined in the default definitions. "
                           f"Please add the value to the definitions to move on without errors.")

        return dict(zip(param_keys, default_values))

    @staticmethod
    def _set_item_name_from(type_name, item_ix):
        """Sets a name for an item from its type and index (e.g. if there are several walls)."""
        return f"{type_name} {item_ix}"


# TODO: Write many tests for all functionalities since it seems like this tool will be used a lot

# TODO: eventually, can decouple the checking and plotting functionalities of this class

# TODO: remove the border and background on the x, y, z sliders to declutter the look

# TODO: for the time being, the user can place a new None item if they have not selected an item from the dropdown
#  address this more gracefully.

# TODO: (line 450 in visualise cuboid method) the if statement is only useful when representing cuboids that are
#  hand-created via the RectangularCuboid class (neither from a YAML config, nor from the interactive assistant) how
#  then might we deal with this issue? Because now we may miss that a colour was not set upstream during the creation
#  of the rectangular cuboid list, but we still need this not to crash when attempting to display a custom-made
#  rectangular cuboid for testing. Because as of now, it is impossible to simply plot a cuboid.

# TODO: (line 540, in create rectangular cuboid list, linked to above TODO) can also put default colours here (and
#  stop doing it in visualiser, think about pros/cons) and set an error message in both if the item is not recognised
#  and decide whether or not to fail gracefully: crash the app or give a default size and colour

# TODO: (line 130 in run dash app) think about how to handle the idx_to_move more gracefully (not really a class
#  attribute) Actually could be seen as the assistant/manager's current_idx_item_to_move attribute Makes sense for
#  the manager to hold this in memory and be able to share this with all the workers (if you decide to go full OOP
#  which may not be desirable).

if __name__ == "__main__":
    configuration_path = os.path.join("example_configs", "config.yaml")
    config_assistant = ConfigAssistant(configuration_path)

    # Checking and visualising an entire configuration file
    config_assistant.check_config_overlap()
    config_assistant.visualise_config()

    # # Visualising a single custom rectangular cuboid
    # lower_base_centroid = np.array([10, 20, 3])
    # dimensions = (10, 10, 30)
    # rotation = 45
    # rec_cuboid = [RectangularCuboid(lower_base_centroid, dimensions, rotation)]
    # # config_assistant._visualise_cuboid_bases_plotly(rec_cuboid)
    # config_assistant._run_dash_app_cuboid_visualisation(rec_cuboid)
