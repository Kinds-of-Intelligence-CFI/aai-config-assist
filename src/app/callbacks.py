import numpy as np
from dash import Output, Input, State, callback

from src.processing.dumper import Dumper
from src.utils.physical_item_helper import get_default_item_parameter
from src.structures.rectangular_cuboid import RectangularCuboid
from src.utils.geometry_helper import calculate_vertices_of_rotated_rectangle


def register_callbacks(app_manager):
    # Create a callback mechanism for when one of the items is selected to be moved
    @callback(
        Output(component_id='x-slider', component_property="value"),
        Output(component_id='y-slider', component_property="value"),
        Output(component_id='z-slider', component_property="value"),
        Output(component_id="xz-rotation-slider", component_property="value"),
        Input(component_id='aai-diagram', component_property='clickData'),
        prevent_initial_call=True
    )
    def _update_sliders(point_clicked):
        """Updates the sliders when one of the items is selected to be moved."""
        cuboids = app_manager.arenas[app_manager.curr_arena_ix].physical_items

        if point_clicked is not None:
            app_manager.curr_item_to_move_ix = point_clicked['points'][0]["curveNumber"]
            ix = app_manager.curr_item_to_move_ix
            print(f"You have just clicked: {cuboids[ix].name}")
            return (cuboids[ix].center[0],  # The x-direction
                    cuboids[ix].center[2],  # The y-direction
                    cuboids[ix].center[1],  # The z-direction
                    cuboids[ix].deg_rotation  # x-z rotation
                    )
        else:
            print("You have not clicked an item")
            return 0, 0, 0

    # Creates a callback mechanism for when the sliders are being used to move items.
    # Note:
    # Creates a callback mechanism for spawning a new item into the arena and into the physical_items
    # These share a callback because Dash only supports one callback per unique output (here, the arena).
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
    def _update_plot(x_slider_value,
                     y_slider_value,
                     z_slider_value,
                     xz_rotation,
                     item_dropdown_value,
                     num_spawn_button_clicks,
                     spawn_x_dim,
                     spawn_z_dim,
                     spawn_y_dim, ):
        """Updates the plot when dash detects user interaction.

        Note:
            - The function arguments come from the component property of the Input.
        """
        cuboids = app_manager.arenas[app_manager.curr_arena_ix].physical_items

        # Must perform the spawning before the slider adjustment to avoid mistakenly reacting to the sliders
        # which the user may not have interacted with but will still be considered here as an input.
        # To avoid this behaviour, the curr_item_to_move_ix is changed to that of the new item, in this if-branch.
        if num_spawn_button_clicks != app_manager.num_auto_items_displayed:
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
            spawned_name = f"{item_dropdown_value} Auto {num_spawn_button_clicks}"
            spawned_colour = get_default_item_parameter(item_name=item_dropdown_value,
                                                        param_name="colour",
                                                        default_item_parameters=app_manager.default_item_parameters)
            spawned_auto_cuboid = RectangularCuboid(lower_base_centroid=spawned_lower_base_centroid,
                                                    dimensions=spawned_dimensions,
                                                    rotation=spawned_rotation,
                                                    name=spawned_name,
                                                    colour=spawned_colour
                                                    )
            # TODO: Strange behaviour whereby simply writing cuboids += [spawned...] does not work. Not sure why.
            #  Doing temp = cuboids AND temp += [spawned...] worked
            #  But since I was encountering this issue in numerous places, I went with this local var approach
            #  Will have to think about this as an independent issue at some point.
            cuboids += [spawned_auto_cuboid]
            app_manager.num_auto_items_displayed = num_spawn_button_clicks
            app_manager.curr_item_to_move_ix = -1
            item_ix = app_manager.curr_item_to_move_ix
            xz_rotation = spawned_rotation
            print(f"You have just created: {spawned_name}")

        else:
            # Update the cuboid center coordinates
            # Note: when calling visualise_config, cuboids is the physical_items class attribute
            item_ix = app_manager.curr_item_to_move_ix
            cuboids[item_ix].center[0] = x_slider_value
            cuboids[item_ix].center[2] = y_slider_value
            cuboids[item_ix].center[1] = z_slider_value
            cuboids[item_ix].deg_rotation = xz_rotation

        # Note that the center parameter expects the 2D planar values
        # AAI-x (cuboid[...].center[0]) and AAI-z (cuboid[...].center[1])
        cuboids[item_ix].lower_base_vertices = calculate_vertices_of_rotated_rectangle(
            center=np.array([cuboids[item_ix].center[0], cuboids[item_ix].center[1]]),
            width=cuboids[item_ix].length,
            height=cuboids[item_ix].width,
            angle_deg=xz_rotation)

        print(f"The item currently being moved is: {cuboids[item_ix].name}")

        arena_ix = app_manager.curr_arena_ix
        app_manager.arenas[arena_ix].overlapping_items = app_manager.checker.check_overlaps_between_cuboids(cuboids)
        curr_overlapping_items = app_manager.arenas[arena_ix].overlapping_items
        fig = app_manager.visualiser.visualise_cuboid_bases(cuboids, curr_overlapping_items)

        return fig

    # Creates a callback mechanism for dumping the current physical items to a new configuration file."""
    @callback(
        Output(component_id='new-config-path-output', component_property="value"),
        State(component_id="new-config-path", component_property="value"),
        Input(component_id='new-config-path-button', component_property="n_clicks"),
        prevent_initial_call=True
    )
    def _dump_current_layout_to_config(new_config_path, n_clicks, ):
        # Could encapsulate the following lines into a wrapper function (that only gets called once at init or when
        # the current arena changes to not repeat this at each dump).

        # All of these are being read only and not overwritten which is why we can create new vars.
        # Think mutability problem and requirement for AppManager instance attributes to be
        # updated during the callbacks.
        curr_arena = app_manager.arenas[app_manager.curr_arena_ix]
        pass_mark = curr_arena.pass_mark
        t = curr_arena.t
        cuboids = curr_arena.physical_items

        arena = {"pass_mark": pass_mark, "t": t, "items": cuboids}
        arena_config_dumper = Dumper([arena], destination_file_path="")
        if n_clicks > 0:
            arena_config_dumper.destination_file_path = new_config_path
            arena_config_dumper.dump()
            print(f"You have generated a new config YAML file at {new_config_path}.")
            return ""  # Empty the string after the process has completed

#  TODO: Note that while overcoming many issues, this way of defining callbacks precludes type hinting using the#
#   src.app.AppManager (or whatever it's called now); because that would result in a circular import. Maybe there is
#   a#  work around, but this is still a big readability and functionality improvement over what we had before so will
#   stick#  to this for now.

#  TODO: Will be able to remove all the [0] indexing to get the value of the variables (that no
#   longer need be mutable)

#  TODO: Could set some variables at the start of the register_callbacks function (e.g. cuboids, etc...)
#   to not have to always reference the app_manager over and over

# TODO: Now priority after cleaning up the naming and comments in this file and app_manager will be dual: split the
#  long callback in this file. AND move the instantiation of all the other classes to a factory or another location
#  to be able to do clean dependency injection. Maybe create an AppInitialiser with all the instantiation and an
#  AppRunner to run the app. Then can either create an AppManager which initialises an initialiser and a runner and
#  runs the application or just do that in a main.py file.

#  TODO: Eventually, can make this file into a class so that you can unit test your callback functions

# TODO: there is this whole issue of immutable vs mutable types and how I can make sure the AppManager attribute values
#  persist during and post callbacks
