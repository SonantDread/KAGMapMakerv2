# UI layout

import os, importlib.util

from PyQt6.QtWidgets import QWidget

class ui:
    def __init__(self, parent):
        self.parent = parent
        self.modules = []
        self.fetch_modules()
    
    def fetch_modules(self):
        path = os.path.dirname(os.path.realpath(__file__))

        # check if the modules folder exists, create it if it doesnt
        modules_folder = os.path.join(path, "modules")
        if not os.path.exists(modules_folder):
            os.makedirs(modules_folder, exist_ok=True)
            print(f"Created 'modules' folder at: '{modules_folder}'")

        for name in os.listdir(modules_folder):
            if not name.endswith(".py"): # if not python file
                continue

            # ignore importing if it has a '_' at start
            if name.startswith('_'): 
                continue

            module_name = os.path.splitext(name)[0]

            try:
                # load module dynamically
                module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(modules_folder, name))
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                class_name = 'module'
                class_object = getattr(module, class_name)

                # create an instance of the class
                instance = class_object(self.parent)

                # append the instance to the list
                self.modules.append(instance)
                print(f"Imported module: {module_name}")

            except (FileNotFoundError, ModuleNotFoundError, AttributeError) as e:
                print(f"Failed to import module: {module_name}. Error: {e}")

    def load(self):
        for module in self.modules:
            module.setupUi()