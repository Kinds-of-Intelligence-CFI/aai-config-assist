import yaml
from dash import Dash

from src.processing.loader import Loader
from src.processing.preprocessor import Preprocessor
from src.core.checker import Checker
from src.core.visualiser import Visualiser
from src.app.setup import set_up_app_layout
from src.app.callbacks import register_callbacks


class AppManager:
    def __init__(self, config_path: str):
        self.config_path = config_path

        # Get the default item parameters
        with open("src/definitions/item_default_parameters.yaml", "r") as file:
            self.default_item_parameters = yaml.safe_load(file)
        self.all_aai_item_names = list(self.default_item_parameters.keys())

        # Load the YAML data in
        yaml_config_data = Loader.load_config_data(self.config_path)

        # Transform the YAML data into convenient Python objects
        preprocessor = Preprocessor(self.default_item_parameters, self.all_aai_item_names)
        self.arenas = preprocessor.create_arenas_list(yaml_config_data)

        # Instantiate required classes
        self.checker = Checker()
        self.visualiser = Visualiser()

        self.curr_arena_ix = 0
        self.curr_item_to_move_ix = 0
        self.num_auto_items_displayed = 0

    def run_app(self,):
        """Launches Dash application to visualise cuboids."""
        app = Dash(__name__,)
        app.layout = set_up_app_layout(self._get_fig_init(), self.all_aai_item_names)
        register_callbacks(app_manager=self)
        app.run(port=8000)

    def _get_fig_init(self):
        cuboids = self.arenas[self.curr_arena_ix].physical_items
        names_items_with_overlap = self.checker.check_overlaps_between_cuboids(cuboids)
        fig_init = self.visualiser.visualise_cuboid_bases(cuboids, list(names_items_with_overlap))
        return fig_init


def application_manager_example():
    application_manager = AppManager("example_configs/config.yaml")
    application_manager.run_app()


# TODO: write some kind of initialisation script for any time a new arena is shown on screen
#  this should involve checking which items overlap, setting the curr_arena_ix appropriately,
#  and things like that.

# TODO: write an initialisation function that can be called everytime a new arena is selected (see notion)
#  though this would require making the app itself an instance attribute and running self.app.layout = ... in the init
#  func.

# TODO: look into splitting the long callback using the dash extensions

# TODO: Write many tests for all functionalities since it seems like this tool will be used a lot

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

# TODO: Think about the issue of using lists to denote idx_item_to_move and num_auto_items_displayed; yes, it solves
#  the problem of the variables pointing to the same entity so that the correct variables are updated. But does this
#  introduce strange side effects whereby nothing is truly encapsulated? Is it desirable that I am modifying a variable
#  that is linked to the same object as a variable from the outer scope. Consider this issue more closely.


if __name__ == "__main__":
    application_manager_example()
