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
    DEFAULT_SLIDER_VALUE = 0
    DEFAULT_SPAWNED_ITEM_SIZE = 1
    DEFAULT_SPAWNED_ITEM_ROTATION = 0
    DEFAULT_SPAWNED_LOCATION_X = 0
    DEFAULT_SPAWNED_LOCATION_Y = 0
    DEFAULT_SPAWNED_LOCATION_Z = 0
    SPAWNED_ITEM_NAME_IDENTIFIER = "AUTO"

    def __init__(self, app_manager: AppManager) -> None:
        self.app_manager = app_manager

    def register_callbacks(self) -> None:
        self._register_update_sliders_callback()
        self._register_move_cuboids_callback()
        self._register_spawn_item_callback()
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
            """Updates the sliders when one of the AAI arena items is clicked."""
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items

            if point_clicked is not None:
                self.app_manager.curr_item_to_move_ix = point_clicked['points'][0]["curveNumber"]
                ix = self.app_manager.curr_item_to_move_ix
                print(f"You have just clicked: {cuboids[ix].name}")
                return (cuboids[ix].center_x,
                        cuboids[ix].center_y,
                        cuboids[ix].center_z,
                        cuboids[ix].deg_rotation)
            else:
                print("You have not clicked an item")
                return (self.DEFAULT_SLIDER_VALUE,) * 4

    def _register_move_cuboids_callback(self) -> None:
        @callback(
            Output(component_id="aai-diagram", component_property="figure", allow_duplicate=True),
            Input(component_id="x-slider", component_property="value"),
            Input(component_id="y-slider", component_property="value"),
            Input(component_id="z-slider", component_property="value"),
            Input(component_id="xz-rotation-slider", component_property="value"),
            prevent_initial_call=True
        )
        def _move_cuboids(x_slider_value: float,
                          y_slider_value: float,
                          z_slider_value: float,
                          xz_rotation: float) -> matplotlib.figure.Figure:
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items
            item_ix = self.app_manager.curr_item_to_move_ix
            cuboids[item_ix].center_x = x_slider_value
            cuboids[item_ix].center_y = y_slider_value
            cuboids[item_ix].center_z = z_slider_value
            cuboids[item_ix].deg_rotation = xz_rotation
            fig = self._update_pre_plotting_attributes(cuboids, item_ix, xz_rotation)
            return fig

    def _register_spawn_item_callback(self) -> None:
        @callback(
            Output(component_id="aai-diagram", component_property="figure", allow_duplicate=True),
            State(component_id="item-dropdown", component_property="value"),
            Input(component_id='new-item-button', component_property="n_clicks"),
            State(component_id="spawn-x", component_property="value"),
            State(component_id="spawn-z", component_property="value"),
            State(component_id="spawn-y", component_property="value"),
            prevent_initial_call=True
        )
        def _spawn_item(item_dropdown_value: str,
                        num_spawn_button_clicks: int,
                        spawn_x_dim: float,
                        spawn_z_dim: float,
                        spawn_y_dim: float) -> matplotlib.figure.Figure:
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items
            spawned_lower_base_centroid = np.array([self.DEFAULT_SPAWNED_LOCATION_X,
                                                    self.DEFAULT_SPAWNED_LOCATION_Z,
                                                    self.DEFAULT_SPAWNED_LOCATION_Y], dtype=float)

            # Fallback if user leaves the new item dimensions blank
            if spawn_x_dim == "":
                spawn_x_dim = self.DEFAULT_SPAWNED_ITEM_SIZE
            if spawn_z_dim == "":
                spawn_z_dim = self.DEFAULT_SPAWNED_ITEM_SIZE
            if spawn_y_dim == "":
                spawn_y_dim = self.DEFAULT_SPAWNED_ITEM_SIZE

            # Convert the dimensions (either str from callback or int from blank dimension fallback)
            spawned_dimensions = (float(spawn_x_dim), float(spawn_z_dim), float(spawn_y_dim))
            spawned_rotation = self.DEFAULT_SPAWNED_ITEM_ROTATION
            spawned_name = f"{item_dropdown_value} Auto {num_spawn_button_clicks}"
            spawned_colour = get_default_item_parameter(item_name=item_dropdown_value,
                                                        param_name="colour",
                                                        default_item_params=self.app_manager.default_item_parameters)
            spawned_auto_cuboid = RectangularCuboid(lower_base_centroid=spawned_lower_base_centroid,
                                                    dimensions=spawned_dimensions,
                                                    rotation=spawned_rotation,
                                                    name=spawned_name,
                                                    colour=spawned_colour)
            cuboids += [spawned_auto_cuboid]
            self.app_manager.curr_item_to_move_ix = -1
            item_ix = self.app_manager.curr_item_to_move_ix
            xz_rotation = spawned_rotation
            print(f"You have just created: {spawned_name}")
            fig = self._update_pre_plotting_attributes(cuboids, item_ix, xz_rotation)
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

    def _update_pre_plotting_attributes(self, cuboids, item_ix, xz_rotation):
        self._update_curr_item_lower_base_vertices(cuboids, item_ix, xz_rotation)
        print(f"The item currently being moved is: {cuboids[item_ix].name}")
        curr_overlapping_items = self._update_curr_arena_overlapping_items(cuboids)
        fig = self.app_manager.visualiser.visualise_cuboid_bases(cuboids, curr_overlapping_items)
        return fig

    def _update_curr_arena_overlapping_items(self, cuboids):
        arena_ix = self.app_manager.curr_arena_ix
        self.app_manager.arenas[
            arena_ix].overlapping_items = self.app_manager.checker.check_overlaps_between_cuboids(cuboids)
        return self.app_manager.arenas[arena_ix].overlapping_items

    @staticmethod
    def _update_curr_item_lower_base_vertices(cuboids, item_ix, xz_rotation):
        # Note: center param expects x, and z center coordinates
        cuboids[item_ix].lower_base_vertices = calculate_vertices_of_rotated_rectangle(
            center=np.array([cuboids[item_ix].center_x, cuboids[item_ix].center_z]),
            width=cuboids[item_ix].length,
            height=cuboids[item_ix].width,
            angle_deg=xz_rotation)

    def _generate_spawn_name(self, item_dropdown_value: str, num_spawn_button_clicks: int) -> str:
        return f"{item_dropdown_value} {self.SPAWNED_ITEM_NAME_IDENTIFIER} {num_spawn_button_clicks}"

# TODO: Further modularise. Make sure that every method is SINGLE PURPOSE as described by the method name
#  go through the whole class to check where you can modularise further
# TODO: Get rid of magic numbers and strings (e.g. which index corresponds to the x, y, or z component: that's also
#  magic)
# TODO: Could encapsulate the following lines into a wrapper function
#  (that only gets called once at init or when the current arena changes to not repeat this at each dump).
#  In dump current layout to config
# TODO: Error handling
