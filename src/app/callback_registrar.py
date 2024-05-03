# To avoid circular imports
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import matplotlib.figure

if TYPE_CHECKING:
    from src.app.app_manager import AppManager

import numpy as np
from dash import Output, Input, State, callback

from src.processing.dumper import Dumper
from src.utils.physical_item_helper import get_default_item_parameter
from src.structures.rectangular_cuboid import RectangularCuboid
from src.structures.arena import Arena
from src.utils.geometry_helper import calculate_vertices_of_rotated_rectangle


class CallbackRegistrar:
    def __init__(self, app_manager: AppManager) -> None:
        self.app_manager = app_manager

    def register_callbacks(self) -> None:
        self._register_update_sliders_callback()
        self._register_update_plot_callback()
        self._register_dump_current_layout_to_config_callback()

    def _register_update_sliders_callback(self) -> None:
        """Creates a callback mechanism for when one of the items is selected to be moved."""
        @callback(
            Output(component_id='x-slider', component_property="value"),
            Output(component_id='y-slider', component_property="value"),
            Output(component_id='z-slider', component_property="value"),
            Output(component_id="xz-rotation-slider", component_property="value"),
            Input(component_id='aai-diagram', component_property='clickData'),
            prevent_initial_call=True
        )
        def _update_sliders(point_clicked: Dict) -> Tuple[float, float, float, float]:
            """Updates the sliders when one of the items is selected to be moved."""
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items

            if point_clicked is not None:
                self.app_manager.curr_item_to_move_ix = point_clicked['points'][0]["curveNumber"]
                ix = self.app_manager.curr_item_to_move_ix
                print(f"You have just clicked: {cuboids[ix].name}")
                return (cuboids[ix].center[0],  # The x-direction
                        cuboids[ix].center[2],  # The y-direction
                        cuboids[ix].center[1],  # The z-direction
                        cuboids[ix].deg_rotation  # x-z rotation
                        )
            else:
                print("You have not clicked an item")
                return 0, 0, 0, 0

    def _register_update_plot_callback(self) -> None:
        """Creates a callback mechanism for when the sliders are being used to move items.

        Note:
            - Creates a callback mechanism for spawning a new item into the arena and into the physical_items.
            - These share a callback because Dash only supports one callback per unique output (here, the arena).
        """

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
        def _update_plot(x_slider_value: float,
                         y_slider_value: float,
                         z_slider_value: float,
                         xz_rotation: float,
                         item_dropdown_value: str,
                         num_spawn_button_clicks: int,
                         spawn_x_dim: float,
                         spawn_z_dim: float,
                         spawn_y_dim: float) -> matplotlib.figure.Figure:
            """Updates the plot when dash detects user interaction.

            Note:
                - The function arguments come from the component property of the Input.
            """
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items

            # Must perform the spawning before the slider adjustment to avoid mistakenly reacting to the sliders
            # which the user may not have interacted with but will still be considered here as an input.
            # To avoid this behaviour, the curr_item_to_move_ix is changed to that of the new item, in this if-branch.
            if num_spawn_button_clicks != self.app_manager.num_auto_items_displayed:
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
                                                            default_item_parameters=self.app_manager.default_item_parameters)
                spawned_auto_cuboid = RectangularCuboid(lower_base_centroid=spawned_lower_base_centroid,
                                                        dimensions=spawned_dimensions,
                                                        rotation=spawned_rotation,
                                                        name=spawned_name,
                                                        colour=spawned_colour
                                                        )
                cuboids += [spawned_auto_cuboid]
                self.app_manager.num_auto_items_displayed = num_spawn_button_clicks
                self.app_manager.curr_item_to_move_ix = -1
                item_ix = self.app_manager.curr_item_to_move_ix
                xz_rotation = spawned_rotation
                print(f"You have just created: {spawned_name}")

            else:
                # Update the cuboid center coordinates
                # Note: when calling visualise_config, cuboids is the physical_items class attribute
                item_ix = self.app_manager.curr_item_to_move_ix
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

            arena_ix = self.app_manager.curr_arena_ix
            self.app_manager.arenas[
                arena_ix].overlapping_items = self.app_manager.checker.check_overlaps_between_cuboids(cuboids)
            curr_overlapping_items = self.app_manager.arenas[arena_ix].overlapping_items
            fig = self.app_manager.visualiser.visualise_cuboid_bases(cuboids, curr_overlapping_items)

            return fig

    def _register_dump_current_layout_to_config_callback(self) -> None:
        """Creates a callback mechanism for dumping the current physical items to a new configuration file."""

        @callback(
            Output(component_id='new-config-path-output', component_property="value"),
            State(component_id="new-config-path", component_property="value"),
            Input(component_id='new-config-path-button', component_property="n_clicks"),
            prevent_initial_call=True
        )
        def _dump_current_layout_to_config(new_config_path: str, n_clicks: int) -> Optional[str]:
            # Could encapsulate the following lines into a wrapper function (that only gets called once at init or when
            # the current arena changes to not repeat this at each dump).

            # All of these are being read only and not overwritten which is why we can create new vars.
            # Think mutability problem and requirement for AppManager instance attributes to be
            # updated during the callbacks.
            curr_arena = self.app_manager.arenas[self.app_manager.curr_arena_ix]
            pass_mark = curr_arena.pass_mark
            t = curr_arena.t
            cuboids = curr_arena.physical_items

            arena = Arena(pass_mark=pass_mark, t=t, physical_items=cuboids, overlapping_items=[""])
            arena_config_dumper = Dumper([arena], destination_file_path="")
            if n_clicks > 0:
                arena_config_dumper.destination_file_path = new_config_path
                arena_config_dumper.dump()
                print(f"You have generated a new config YAML file at {new_config_path}.")
                return ""  # Empty the string after the process has completed

# TODO: Split long callback into 2,3 callbacks (e.g. with dash extension multiple callbacks with same output)
# TODO: Error handling
