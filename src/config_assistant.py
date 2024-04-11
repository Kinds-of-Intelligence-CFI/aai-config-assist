import yaml
import os
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input, State, callback

from src.arena_config_dumper import ArenaConfigDumper
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

        self.pass_mark = self.config_data["arenas"][0]["pass_mark"]
        self.t = self.config_data["arenas"][0]["t"]

        # Get the name of all Animal-AI items
        with open("definitions/item_default_parameters.yaml", "r") as file:
            self.all_aai_item_names = list(yaml.safe_load(file).keys())
        # print(self.all_aai_item_names)

    def check_config_overlap(self):
        """Displays a log of possible overlaps to the terminal."""
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

        # TODO: think about how to handle this more gracefully (not really a class attribute)
        #  Actually could be seen as the assistant/manager's current_idx_item_to_move attribute
        #  Makes sense for the manager to hold this in memory and be able to share this with all the
        #  workers (if you decide to go full OOP which may not be desirable).
        # Initialise the item to be moved
        self.idx_item_to_move = 0
        self.num_auto_items_created = 0

        # Some styling parameters
        font_size = 17
        font_family = "Helvetica"
        background_colour = 'rgba(231,235,235,0.5)'
        tooltip_placement = 'top'
        margin_between_components = 12
        margin_at_bottom_of_components = margin_between_components * 3
        margin_left = 3
        margin_right = 3
        component_height = 21
        border_radius = 3

        # Create a Dash application for more interactivity
        app = Dash(__name__, )
        app.layout = html.Div([
            html.Div([
                dcc.Graph(figure=fig_init, id='aai-diagram', style={"height": "100vh"}),
            ], style={'display': 'inline-block', 'width': '60%', 'verticalAlign': 'middle'}),

            html.Div([

                html.H2("Place new item",
                        id='heading-place-new-item',
                        style={"fontFamily": font_family, "font-weight": "normal",
                               'marginLeft': f"{margin_left / 3}%"}),

                dcc.Dropdown(self.all_aai_item_names, id='item-dropdown', style={"fontSize": f"{font_size}px",
                                                                                 "fontFamily": font_family,
                                                                                 'marginLeft': f"{margin_left - 1.5}%",
                                                                                 'marginRight': f"{margin_right}%"
                                                                                 }),

                html.Div(id='item-dropdown-output', style={'marginBottom': margin_between_components,
                                                           "fontSize": f"{font_size}px",
                                                           "fontFamily": font_family,
                                                           'marginLeft': f"{margin_left - 1.5}%",
                                                           'marginRight': f"{margin_right}%"
                                                           }),

                dcc.Input(placeholder='Length (x)', type='text', value='', id="spawn-x",
                          style={"fontSize": f"{font_size}px", "fontFamily": font_family,
                                 'marginBottom': margin_between_components,
                                 'marginTop': margin_between_components,
                                 'marginLeft': f"{margin_left}%",
                                 # 'marginRight': f"{margin_right}%",
                                 }
                          ),
                dcc.Input(placeholder='Width (z)', type='text', value='', id="spawn-z",
                          style={"fontSize": f"{font_size}px", "fontFamily": font_family,
                                 'marginBottom': margin_between_components,
                                 'marginTop': margin_between_components,
                                 # 'marginLeft': f"{margin_left}%",
                                 # 'marginRight': f"{margin_right}%",
                                 }
                          ),
                dcc.Input(placeholder='Height (y)', type='text', value='', id="spawn-y",
                          style={"fontSize": f"{font_size}px", "fontFamily": font_family,
                                 'marginBottom': margin_between_components,
                                 'marginTop': margin_between_components,
                                 # 'marginLeft': f"{margin_left}%",
                                 # 'marginRight': f"{margin_right}%",
                                 }
                          ),

                html.Div(html.Button('Spawn new item', id='new-item-button', n_clicks=0,
                                     style={'height': component_height,
                                            "fontSize": f"{font_size}px",
                                            "fontFamily": font_family,
                                            'marginBottom': margin_between_components * 2,
                                            'marginTop': margin_between_components,
                                            'marginLeft': f"{margin_left}%",
                                            'marginRight': f"{margin_right}%",
                                            "cursor": "pointer",
                                            },
                                     ), ),

                html.Div(id='new-item-button-output', style={'whiteSpace': 'pre-line'}),

                html.H2("Move item",
                        id='heading-move-an-item',
                        style={"fontFamily": font_family, "font-weight": "normal",
                               'marginLeft': f"{margin_left / 3}%"}),

                dcc.Slider(id="x-slider", min=0, max=40, step=1, value=0, marks=None,
                           tooltip={"placement": tooltip_placement,
                                    "always_visible": True,
                                    "template": "x = {value}",
                                    "style": {"fontSize": f"{font_size}px",
                                              "fontFamily": font_family,
                                              }, }, ),

                dcc.Slider(id="y-slider", min=0, max=20, step=0.1, value=0, marks=None,
                           tooltip={"placement": tooltip_placement,
                                    "always_visible": True,
                                    "template": "y = {value}",
                                    "style": {"fontSize": f"{font_size}px", "fontFamily": font_family, }, }, ),

                dcc.Slider(id="z-slider", min=0, max=40, step=1, value=0, marks=None,
                           tooltip={"placement": tooltip_placement,
                                    "always_visible": True,
                                    "template": "z = {value}",
                                    "style": {"fontSize": f"{font_size}px", "fontFamily": font_family, }}),

                dcc.Slider(id="xz-rotation-slider", min=0, max=360, step=1, value=0, marks=None,
                           tooltip={"placement": tooltip_placement,
                                    "always_visible": True,
                                    "template": "xz = {value} deg",
                                    "style": {"fontSize": f"{font_size}px", "fontFamily": font_family, }}),

                html.H2("Generate new config",
                        id='heading-generate-a-new-configuration-file',
                        style={"fontFamily": font_family, "font-weight": "normal",
                               'marginLeft': f"{margin_left / 3}%"}),

                dcc.Input(id="new-config-path",
                          style={'width': '80%',
                                 'height': component_height,
                                 "fontSize": f"{font_size}px",
                                 "fontFamily": font_family,
                                 'marginBottom': margin_between_components,
                                 # 'marginTop': margin_between_components,
                                 'marginLeft': f"{margin_left}%",
                                 'marginRight': f"{margin_right}%",
                                 "border-style": "solid",
                                 "border-width": 0.5,
                                 "border-radius": border_radius,
                                 },
                          type="text",
                          placeholder="example_configs/new_config.yaml"),

                html.Div(html.Button('Generate new YAML config', id='new-config-path-button', n_clicks=0,
                                     style={'height': component_height,
                                            "fontSize": f"{font_size}px",
                                            "fontFamily": font_family,
                                            'marginBottom': margin_at_bottom_of_components,
                                            'marginTop': margin_between_components,
                                            'marginLeft': f"{margin_left}%",
                                            'marginRight': f"{margin_right}%",
                                            "cursor": "pointer",
                                            # Un-commenting these fields undesirably removes clicking animation
                                            # "border-radius": border_radius,
                                            # "border-width": 1,
                                            # "background-color": "white",
                                            },
                                     ), ),

                html.Div(id='new-config-path-output', style={'whiteSpace': 'pre-line'}),

            ], style={'display': 'inline-block', 'width': '40%', 'verticalAlign': 'bottom'}),

            html.Div(id='app_id')

        ], style={'backgroundColor': background_colour})

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
                spawned_colour = {"r": 1, "g": 1, "b": 1}
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
            # TODO: test whether commenting the if statement directly above would be safe considering that the item's
            #  colour when/if the colour is always defined in the RectangularCuboid

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
                                     marker=dict(opacity=0),
                                     showlegend=True,
                                     mode="lines",
                                     ),
                          )

            # Customise the legend
            fig.update_layout(
                # width=1000,  # To make the figure square
                # height=1000,  # To make the fiture square
                # template="plotly_dark",
                legend=dict(
                    # itemwidth=100,
                    x=15,  # Try -1, 0, 1
                    y=1,  # Try -1, 0, 1
                    traceorder='normal',
                    font=dict(
                        family='Helvetica',
                        size=20,
                        color='Black'
                    ),
                    # Customise the look of the legend
                    bgcolor='rgba(231,235,235,0.5)',
                    bordercolor='black',
                    borderwidth=1,
                    orientation='v',
                    xanchor='left',
                    yanchor='top',
                )
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

                size = items["sizes"][j] if "sizes" in items else {"x": 1, "y": 1, "z": 1, }
                colour = items["colors"][j] if "colors" in items else self._get_default_item_colour(name)

                # TODO: can also put default colours here (and stop doing it in visualiser, think about pros/cons)
                #  and set an error message in both if the item is not recognised and decide whether or not
                #  to fail gracefully: crash the app or give a default size and colour

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

        Note:
            - Copied the default values from official Animal-AI repository at Arena-Objects.yaml.
            - Some default colours were not available on the official repo and were inferred from the images.

        Args:
            item_name (str): Name of the physical Animal-AI item.

        Returns:
            (dict[str]): The red, green, blue (rgb) components of the default colour for the inputted item.
        """
        with open(f"definitions/item_default_parameters.yaml", "r") as file:
            item_defaults_dict = yaml.safe_load(file)

        item_name = item_name.split(" ")[0]

        try:
            default_colour = {"r": item_defaults_dict[item_name]["colour"][0],
                              "g": item_defaults_dict[item_name]["colour"][1],
                              "b": item_defaults_dict[item_name]["colour"][2]}
        except KeyError:
            # For now, we have chosen to deal with missing colour AND unrecognised name by setting colour to white
            warnings.warn(f"The item {item_name} is not recognised and is missing a 'colors' field in the .yaml "
                          f"configuration. Either add a 'colors' field for this item or add the item to the "
                          f"default_colour_dict above.")
            default_colour = {"r": 255, "g": 255, "b": 255}

        return default_colour

    @staticmethod
    def _get_default_item_size(item_name):
        """Provides the default colour of a particular Animal-AI item.

        Note:
            - Copied the default values from official Animal-AI repository at Arena-Objects.yaml.

        Args:
            item_name (str): Name of the physical Animal-AI item.

        Returns:
            (dict[str]): The x, y, z components of the default size for the inputted item.
        """
        with open(f"definitions/item_default_parameters.yaml", "r") as file:
            item_defaults_dict = yaml.safe_load(file)

        item_name = item_name.split(" ")[0]

        param = "size"

        try:
            default_size = {"x": item_defaults_dict[item_name][param][0],
                            "y": item_defaults_dict[item_name][param][1],
                            "z": item_defaults_dict[item_name][param][2]}
        except KeyError:
            # For now, we have chosen to deal with missing colour AND unrecognised name by setting colour to white
            warnings.warn(f"The item {item_name} is not recognised and is missing a 'colors' field in the .yaml "
                          f"configuration. Either add a 'colors' field for this item or add the item to the "
                          f"default_colour_dict above.")
            default_size = {"x": 1, "y": 1, "z": 1}

        return default_size

    @staticmethod
    def _set_item_name_from(type_name, item_ix):
        """Sets a name for an item from its type and index (e.g. if there are several walls)."""
        return f"{type_name} {item_ix}"


# TODO: make the item_defaults_dict a class attribute of the configuration assistant so that you do not have to do
#  opening and closing over and over
# TODO: Update how _get_default_size is implemented (taking into consideration that you need to start checking
#  whether a requested item is in a list of 'defaults'; else, you may want to let the user know
# TODO: fix the fact that new objects spawning do not have the right colour
# TODO: Implement raising appropriate exceptions when unrecognised items are encountered
# TODO: Write many tests for all functionalities since it seems like this tool will be used a lot
# TODO: eventually, can decouple the checking and plotting functionalities of this class
# TODO: remove the border and background on the x, y, z sliders to declutter the look

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
