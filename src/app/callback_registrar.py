# To avoid circular imports
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional, Tuple, List
import os

if TYPE_CHECKING:
    from src.app.app_manager import AppManager

import numpy as np
import matplotlib.figure
from dash import Output, Input, State, callback

from src.processing.dumper import Dumper
from src.structures.rectangular_cuboid import RectangularCuboid
from src.structures.arena import Arena
from src.utils.geometry_helper import calculate_vertices_of_rotated_rectangle
from src.utils.physical_item_helper import get_default_item_parameter
from src.utils.utils import create_directory_if_not_exists


class CallbackRegistrar:
    DEFAULT_SLIDER_VALUE = 0
    FALLBACK_ITEM_SIZE = 1
    DEFAULT_SPAWNED_ITEM_ROTATION = 0
    DEFAULT_SPAWNED_LOCATION_X = 0
    DEFAULT_SPAWNED_LOCATION_Y = 0
    DEFAULT_SPAWNED_LOCATION_Z = 0
    SPAWNED_ITEM_NAME_IDENTIFIER = "Auto"

    def __init__(self, app_manager: AppManager) -> None:
        self.app_manager = app_manager

    def register_callbacks(self) -> None:
        self._register_update_sliders_callback()
        self._register_move_cuboids_callback()
        self._register_spawn_item_callback()
        self._register_dump_current_layout_to_config_callback()
        self._register_remove_current_item_callback()
        self._register_resize_current_item_callback()

    def _register_update_sliders_callback(self) -> None:
        """Creates a callback mechanism for when one of the items is selected to be moved."""

        @callback(
            Output(component_id='output-current-item', component_property="children", allow_duplicate=True),
            Output(component_id='x-slider', component_property="value"),
            Output(component_id='y-slider', component_property="value"),
            Output(component_id='z-slider', component_property="value"),
            Output(component_id="xz-rotation-slider", component_property="value"),
            Input(component_id='aai-diagram', component_property='clickData'),
            prevent_initial_call=True
        )
        def _update_sliders(point_clicked: Dict) -> Tuple[str, float, float, float, float]:
            """Updates the current item indicator and sliders when one of the AAI arena items is clicked."""
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items

            if point_clicked is not None:
                self.app_manager.curr_item_to_move_ix = point_clicked['points'][0]["curveNumber"]
                ix = self.app_manager.curr_item_to_move_ix
                return (self._get_currently_selected_item_display_text(cuboids[ix].name),
                        cuboids[ix].center_x,
                        cuboids[ix].center_y,
                        cuboids[ix].center_z,
                        cuboids[ix].deg_rotation)
            else:
                return ("",
                        self.DEFAULT_SLIDER_VALUE,
                        self.DEFAULT_SLIDER_VALUE,
                        self.DEFAULT_SLIDER_VALUE,
                        self.DEFAULT_SLIDER_VALUE)

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
                        spawn_x_dim: str,
                        spawn_z_dim: str,
                        spawn_y_dim: str) -> matplotlib.figure.Figure:
            cuboids = self.app_manager.arenas[self.app_manager.curr_arena_ix].physical_items
            spawned_lower_base_centroid = np.array([self.DEFAULT_SPAWNED_LOCATION_X,
                                                    self.DEFAULT_SPAWNED_LOCATION_Z,
                                                    self.DEFAULT_SPAWNED_LOCATION_Y], dtype=float)
            # Convert the dimensions (either str from callback or int from blank dimension fallback)
            spawned_dimensions = self._transform_str_to_float_dimensions(spawn_x_dim, spawn_z_dim, spawn_y_dim)
            spawned_rotation = self.DEFAULT_SPAWNED_ITEM_ROTATION
            spawned_name = f"{item_dropdown_value} {self.SPAWNED_ITEM_NAME_IDENTIFIER} {num_spawn_button_clicks}"
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
            create_directory_if_not_exists(os.path.dirname(new_config_path))

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

    def _register_remove_current_item_callback(self) -> None:
        @callback(
            Output(component_id="aai-diagram", component_property="figure", allow_duplicate=True),
            Output(component_id='output-current-item', component_property="children", allow_duplicate=True),
            Input(component_id="remove-item-button", component_property="n_clicks"),
            prevent_initial_call=True
        )
        def _remove_current_item(num_remove_item_button_clicks: int) -> Tuple[matplotlib.figure.Figure, str]:
            if num_remove_item_button_clicks > 0:
                # Remove cuboid
                curr_arena_ix = self.app_manager.curr_arena_ix
                curr_item_ix = self.app_manager.curr_item_to_move_ix
                cuboids_pre_removal = self.app_manager.arenas[curr_arena_ix].physical_items
                self.app_manager.arenas[curr_arena_ix].physical_items = (cuboids_pre_removal[0:curr_item_ix] +
                                                                         cuboids_pre_removal[curr_item_ix + 1:])
                cuboids_post_removal = self.app_manager.arenas[curr_arena_ix].physical_items

                # Regenerate arena figure
                overlapping_items = self._update_curr_arena_overlapping_items(cuboids_post_removal)
                fig = self.app_manager.visualiser.visualise_cuboid_bases(cuboids_post_removal, overlapping_items)
                return fig, "No item selected"

    def _register_resize_current_item_callback(self) -> None:
        @callback(
            Output(component_id="aai-diagram", component_property="figure", allow_duplicate=True),
            Input(component_id="resize-item-button", component_property="n_clicks"),
            State(component_id="resize-x", component_property="value"),
            State(component_id="resize-z", component_property="value"),
            State(component_id="resize-y", component_property="value"),
            prevent_initial_call=True
        )
        def _resize_current_item(num_resize_item_button_clicks: int,
                                 resize_x_dim: str,
                                 resize_z_dim: str,
                                 resize_y_dim: str) -> matplotlib.figure.Figure:
            if num_resize_item_button_clicks > 0:

                resize_x_dim, resize_z_dim, resize_y_dim = self._transform_str_to_float_dimensions(resize_x_dim,
                                                                                                   resize_z_dim,
                                                                                                   resize_y_dim)

                # Resize the cuboid
                curr_arena_ix = self.app_manager.curr_arena_ix
                curr_item_ix = self.app_manager.curr_item_to_move_ix
                cuboids_pre_edit = self.app_manager.arenas[curr_arena_ix].physical_items
                center = cuboids_pre_edit[curr_item_ix].center
                deg_rotation = cuboids_pre_edit[curr_item_ix].deg_rotation
                self.app_manager.arenas[curr_arena_ix].physical_items[curr_item_ix].length = resize_x_dim
                self.app_manager.arenas[curr_arena_ix].physical_items[curr_item_ix].width = resize_z_dim
                self.app_manager.arenas[curr_arena_ix].physical_items[curr_item_ix].height = resize_y_dim
                new_vertices = calculate_vertices_of_rotated_rectangle(center=center[:2],
                                                                       width=resize_x_dim,
                                                                       height=resize_z_dim,
                                                                       angle_deg=deg_rotation)
                self.app_manager.arenas[curr_arena_ix].physical_items[curr_item_ix].lower_base_vertices = new_vertices
                cuboids_post_edit = self.app_manager.arenas[curr_arena_ix].physical_items

                # Regenerate arena figure
                overlapping_items = self._update_curr_arena_overlapping_items(cuboids_post_edit)
                fig = self.app_manager.visualiser.visualise_cuboid_bases(cuboids_post_edit, overlapping_items)
                return fig

    def _update_pre_plotting_attributes(self, cuboids, item_ix, xz_rotation) -> matplotlib.figure.Figure:
        self._update_curr_item_lower_base_vertices(cuboids, item_ix, xz_rotation)
        print(f"The item currently being moved is: {cuboids[item_ix].name}")
        curr_overlapping_items = self._update_curr_arena_overlapping_items(cuboids)
        fig = self.app_manager.visualiser.visualise_cuboid_bases(cuboids, curr_overlapping_items)
        return fig

    def _update_curr_arena_overlapping_items(self, cuboids) -> List[str]:
        arena_ix = self.app_manager.curr_arena_ix
        self.app_manager.arenas[
            arena_ix].overlapping_items = self.app_manager.checker.check_overlaps_between_cuboids(cuboids)
        return self.app_manager.arenas[arena_ix].overlapping_items

    @staticmethod
    def _update_curr_item_lower_base_vertices(cuboids, item_ix, xz_rotation) -> None:
        # Note: center param expects x, and z center coordinates
        cuboids[item_ix].lower_base_vertices = calculate_vertices_of_rotated_rectangle(
            center=np.array([cuboids[item_ix].center_x, cuboids[item_ix].center_z]),
            width=cuboids[item_ix].length,
            height=cuboids[item_ix].width,
            angle_deg=xz_rotation)

    def _generate_spawn_name(self, item_dropdown_value: str, num_spawn_button_clicks: int) -> str:
        return f"{item_dropdown_value} {self.SPAWNED_ITEM_NAME_IDENTIFIER} {num_spawn_button_clicks}"

    @staticmethod
    def _get_currently_selected_item_display_text(item_name: str) -> str:
        return f"Current item: {item_name}"

    def _transform_str_to_float_dimensions(self,
                                           number_text1: str,
                                           number_text2: str,
                                           number_text3: str) -> Tuple[float, ...]:
        float_fallback_size = float(self.FALLBACK_ITEM_SIZE)
        float_list = [float_fallback_size, float_fallback_size, float_fallback_size]
        for index, number_text in enumerate([number_text1, number_text2, number_text3]):
            if number_text != "":
                float_list[index] = float(number_text)
        return tuple(float_list)


# TODO: Further modularise. Make sure that every method is SINGLE PURPOSE as described by the method name
#  go through the whole class to check where you can modularise further

# TODO: consider splitting the sliders callback into one callback for the current item board and one for the sliders
#  or even one per sliders. Consider how you can do this callback waterfall whereby the click always causes all the
#  others

# TODO: Get rid of magic numbers and strings (e.g. which index corresponds to the x, y, or z component: that's also
#  magic)

# TODO: Could encapsulate the following lines into a wrapper function
#  (that only gets called once at init or when the current arena changes to not repeat this at each dump).
#  In dump current layout to config

# TODO: should not set style (for _get_currently_selected_item...) in the CallbackRegistrar.
#  should instead find a way to simply get the name of the item from the callback and leave the responsibility of
#  displaying the information appropriately to the setup.py and style_guide.py.
#  should really just have two HTML components. One that says "Current item" and another that says None by default
#  and that is waiting for information from the callback who does nothing but pass the name of the current item,
#  no display etc... it is not its responsibility. Anywhere there is a magic string e.g. "No item selected":
#  make sure to draw that from a bank of constants (so it's centralised and there is no duplication and that
#  responsibility is well separated).

# TODO: Error handling

# TODO: look out for (maybe) combining implementations in removing and resizing callbacks which have some similarities

# TODO: must improve implementation of the resize_current_item method. Two points to study:
#  1. The fact that we can't use variables to denote the app manager's attributes (the objects won't be linked)
#   perhaps there is a way around this to stop having such long expressions throughout the file but still be pointing
#   to the correct object
#  2. There has to be a more automated way of 'updating' all of the necessary attributes of a RectangularCuboid
#   because multiple times I've had to 'reevaluate' the lower base vertices of the RectangularCuboid and it feels like
#   that responsibility should remain with the cuboid itself when one of its attributes is changed. Think about this.

# TODO: In general there should be a reflection about how to make callback design more seamless
