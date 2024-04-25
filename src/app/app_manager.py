import yaml
import numpy as np
from dash import Dash, Output, Input, State, callback

from src.processing.loader import Loader
from src.processing.preprocessor import Preprocessor
from src.core.checker import Checker
from src.core.visualiser import Visualiser
from src.processing.dumper import Dumper
from src.utils.geometry_helper import calculate_vertices_of_rotated_rectangle
from src.app.setup import set_up_app_layout
from src.structures.rectangular_cuboid import RectangularCuboid
from src.utils.physical_item_helper import get_default_item_parameter


class AppManager:
    def __init__(self, config_path: str):
        self.config_path = config_path

        # Get the default item parameters
        with open("src/app/item_default_parameters.yaml", "r") as file:
            self.default_item_parameters = yaml.safe_load(file)
        self.all_aai_item_names = list(self.default_item_parameters.keys())

        # Load the YAML data in
        self.loader = Loader
        yaml_config_data = self.loader.load_config_data(self.config_path)

        # Transform the YAML data into convenient Python objects
        self.preprocessor = Preprocessor(self.default_item_parameters, self.all_aai_item_names)
        self.arenas = self.preprocessor.create_arenas_list(yaml_config_data)

        # Instantiate required classes
        self.checker = Checker()
        self.visualiser = Visualiser()

        self.curr_arena_ix = 0

    def run_app(self, ):
        """Launches Dash application to visualise cuboids."""
        cuboids = self.arenas[self.curr_arena_ix].physical_items
        idx_item_to_move = [0]
        num_auto_items_displayed = [0]
        # TODO: write some kind of initialisation script for any time a new arena is shown on screen
        #  this should involve checking which items overlap, setting the curr_arena_ix appropriately,
        #  and things like that.
        names_items_with_overlap = self.checker.check_overlaps_between_cuboids(cuboids)
        fig_init = self.visualiser.visualise_cuboid_bases(cuboids, list(names_items_with_overlap))

        app = Dash(__name__, )
        app.layout = set_up_app_layout(fig_init, self.all_aai_item_names)

        self._update_sliders_callback(cuboids, idx_item_to_move)
        self._update_plot_callback(cuboids, idx_item_to_move, num_auto_items_displayed)
        # TODO: think about where the pass_mark and t are going to come from. Perhaps all callbacks should have the
        #  arenas passed to them
        self._dump_current_layout_to_config_callback(cuboids,
                                                     pass_mark=self.arenas[self.curr_arena_ix].pass_mark,
                                                     t=self.arenas[self.curr_arena_ix].t)

        app.run(port=8000)

    @staticmethod
    def _update_sliders_callback(cuboids, idx_item_to_move):
        """Creates a callback mechanism for when one of the items is selected to be moved."""

        @callback(
            Output(component_id='x-slider', component_property="value"),
            Output(component_id='y-slider', component_property="value"),
            Output(component_id='z-slider', component_property="value"),
            Output(component_id="xz-rotation-slider", component_property="value"),
            Input(component_id='aai-diagram', component_property='clickData'),
            prevent_initial_call=True
        )
        def _update_sliders(point_clicked, _idx_item_to_move=idx_item_to_move):
            """Updates the sliders when one of the items is selected to be moved."""
            if point_clicked is not None:
                print("you have clicked an item")
                _idx_item_to_move[0] = point_clicked['points'][0]["curveNumber"]
                print(f"You have just clicked: {cuboids[_idx_item_to_move[0]].name}")
                return (cuboids[_idx_item_to_move[0]].center[0],  # The x-direction
                        cuboids[_idx_item_to_move[0]].center[2],  # The y-direction
                        cuboids[_idx_item_to_move[0]].center[1],  # The z-direction
                        cuboids[_idx_item_to_move[0]].deg_rotation
                        )

            else:
                print("You have not clicked an item")
                return 0, 0, 0

    def _update_plot_callback(self, cuboids, idx_item_to_move, num_auto_items_displayed):
        """Creates a callback mechanism for when the sliders are being used to move items.

        Note:
            Creates a callback mechanism for spawning a new item into the arena and into the physical_items
            These share a callback because Dash only supports one callback per unique output (here, the arena).
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
        def _update_plot(x_slider_value,
                         y_slider_value,
                         z_slider_value,
                         xz_rotation,
                         item_dropdown_value,
                         num_auto_items_created,
                         spawn_x_dim,
                         spawn_z_dim,
                         spawn_y_dim,
                         _cuboids=cuboids,
                         _idx_item_to_move=idx_item_to_move,
                         _num_auto_items_displayed=num_auto_items_displayed):
            """Updates the plot when dash detects user interaction.

            Note:
                - The function arguments come from the component property of the Input.
            """
            # Must perform the spawning before the slider adjustment to avoid mistakenly reacting to the sliders
            # which the user may not have interacted with but will still be considered here as an input.
            # To avoid this behaviour, the idx_item_to_move is changed to that of the new item, in this if-branch.
            if num_auto_items_created != _num_auto_items_displayed[0]:
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
                spawned_colour = get_default_item_parameter(item_name=item_dropdown_value,
                                                            param_name="colour",
                                                            default_item_parameters=self.default_item_parameters)
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
                _cuboids += [spawned_auto_cuboid]
                _num_auto_items_displayed[0] = num_auto_items_created
                _idx_item_to_move[0] = -1
                xz_rotation = spawned_rotation
                print(f"You have just created: {spawned_name}")

            else:
                # Update the cuboid center coordinates
                # Note: when calling visualise_config, cuboids is the physical_items class attribute
                _cuboids[_idx_item_to_move[0]].center[0] = x_slider_value
                _cuboids[_idx_item_to_move[0]].center[2] = y_slider_value
                _cuboids[_idx_item_to_move[0]].center[1] = z_slider_value
                _cuboids[_idx_item_to_move[0]].deg_rotation = xz_rotation

            # Note that the center parameter expects the 2D planar values
            # AAI-x (cuboid[...].center[0]) and AAI-z (cuboid[...].center[1])
            _cuboids[_idx_item_to_move[0]].lower_base_vertices = calculate_vertices_of_rotated_rectangle(
                center=np.array(
                    [_cuboids[_idx_item_to_move[0]].center[0], _cuboids[_idx_item_to_move[0]].center[1]]),
                width=_cuboids[_idx_item_to_move[0]].length,
                height=_cuboids[_idx_item_to_move[0]].width,
                angle_deg=xz_rotation)

            print(f"The item currently being moved is: {_cuboids[_idx_item_to_move[0]].name}")

            self.arenas[self.curr_arena_ix].overlapping_items = self.checker.check_overlaps_between_cuboids(cuboids)
            curr_overlapping_items = self.arenas[self.curr_arena_ix].overlapping_items

            fig = self.visualiser.visualise_cuboid_bases(cuboids, curr_overlapping_items)

            return fig

    @staticmethod
    def _dump_current_layout_to_config_callback(cuboids, pass_mark, t):
        """Creates a callback mechanism for dumping the current physical items to a new configuration file."""
        arena = {"pass_mark": pass_mark, "t": t, "items": cuboids}
        arena_config_dumper = Dumper([arena], destination_file_path="")

        @callback(
            Output(component_id='new-config-path-output', component_property="value"),
            State(component_id="new-config-path", component_property="value"),
            Input(component_id='new-config-path-button', component_property="n_clicks"),
            prevent_initial_call=True
        )
        def _dump_current_layout_to_config(new_config_path, n_clicks):
            if n_clicks > 0:
                arena_config_dumper.destination_file_path = new_config_path
                arena_config_dumper.dump()
                print(f"You have generated a new config YAML file at {new_config_path}.")
                return ""  # Empty the string after the process has completed


def application_manager_example():
    application_manager = AppManager("example_configs/config.yaml")
    application_manager.run_app()


# TODO [DONE]: Think about modularising app callbacks (to app_callbacks.py) THOUGH remember that they require instance
#  variables that you would not have in another module. Think about how to deal with that.

# TODO: Write many tests for all functionalities since it seems like this tool will be used a lot

# TODO [DONE]: eventually, can decouple the checking and plotting functionalities of this class

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

# TODO: Think about the problem of global vs local variables in the callbacks. That is, I can only access the variables
#  such as idx_item_to_move and num_auto_items_displayed by passing them once to the wrapper method, then a second time
#  to the inner callback method (with a different name to not shadow the global (=passed to wrapper) variable.

# TODO: Think about the issue of using lists to denote idx_item_to_move and num_auto_items_displayed; yes, it solves
#  the problem of the variables pointing to the same entity so that the correct variables are updated. But does this
#  introduce strange side effects whereby nothing is truly encapsulated? Is it desirable that I am modifying a variable
#  that is linked to the same object as a variable from the outer scope. Consider this issue more closely.


if __name__ == "__main__":
    application_manager_example()
