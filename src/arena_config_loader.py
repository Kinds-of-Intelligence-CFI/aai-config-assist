import yaml


class ArenaConfigLoader(yaml.SafeLoader):
    """Loader with custom constructors for the custom tags (e.g. !ArenaConfig) in the configuration YAMLs."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_constructor('!Arena', self.construct_arena)
        self.add_constructor('!ArenaConfig', self.construct_arena_config)
        self.add_constructor('!Item', self.construct_item)
        self.add_constructor('!Vector3', self.construct_vector3)
        self.add_constructor('!RGB', self.construct_rgb)

    def construct_arena(self, loader, node):
        return loader.construct_mapping(node)

    def construct_arena_config(self, loader, node):
        return loader.construct_mapping(node)

    def construct_item(self, loader, node):
        return loader.construct_mapping(node)

    def construct_vector3(self, loader, node):
        return loader.construct_mapping(node)

    def construct_rgb(self, loader, node):
        return loader.construct_mapping(node)


if __name__ == "__main__":
    # Load a configuration yaml file
    config_path = "example_configs/config_broken.yaml"
    with open(config_path) as file:
        config_data = yaml.load(file, Loader=ArenaConfigLoader)
    # print(config_data)
    # print([element for element in config_data["arenas"][0]["items"] if element["name"] != "arena"])
    print("Exit ok")
