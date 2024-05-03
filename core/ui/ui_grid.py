import os, importlib.util

class ui:
    def __init__(self):
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
            if not name.endswith(".py"):
                continue

            module_name = os.path.splitext(name)[0]

            try:
                # load module dynamically
                module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(modules_folder, name))
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                # get the class within the module
                class_name = module_name.capitalize()
                class_object = getattr(module, class_name)

                # create an instance of the class
                instance = class_object()

                # append the instance to the list
                self.modules.append(instance)
                print(f"Imported module: {module_name}")

            except (FileNotFoundError, ModuleNotFoundError, AttributeError) as e:
                print(f"Failed to import module: {module_name}. Error: {e}")