# Project Next Steps
- [ ] Write a guide on how to add a new callback to the callback registrar.
- [ ] Decide how to do constant management across the whole library (e.g. in a long YAML constants file in the src dir) and apply
the rule to all the instances of constants across the codebase (in [style_guide](src/app/style_guide.py), in [setup.py](src/app/setup.py), in [callback_registrar](src/app/callback_registrar.py) etc...). May decide to keep in specific modules or may find that some constants are relevant across modules rather than in a single module only.
- [ ] Could allow user to pass their own style guide and item defaults to the AppManager.
- [ ] Completely remove magic numbers from the entire repository.
- [ ] Could have a user-friendly way of editing the style of the figure (a style guide for the arena figure accessed by [visualiser.py](src/core/visualiser.py) for example)
- [ ] Modularise functions in [callback_registrar.py](src/app/callback_registrar.py) and [preprocessor.py](src/processing/preprocessor.py).

