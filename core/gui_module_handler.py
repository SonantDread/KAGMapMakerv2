"""
Handles scripts for the GUI.
"""
import importlib.util
import glob
import os

from PyQt6.QtWidgets import QMainWindow

from utils.file_handler import FileHandler


class GUIModuleHandler:
    """
    Handles scripts for the GUI.
    """
    def __init__(self, window: QMainWindow):
        self.fh = FileHandler()
        self.app_window = window
        self.modules = self._get_modules()

    def setup_modules(self) -> None:
        """
        Sets up the GUI modules by loading and initializing them.

        Iterates over the list of modules retrieved by `_get_modules`, checks if each module exists,
        loads the module, and creates an instance of the module's `Module` class.

        If the module instance has a `setup_ui` method, it is called to set up the module's UI.

        The module instance is then added to the list of modules.

        Parameters:
            None

        Returns:
            None
        """
        loaded_modules = []
        for path in self.modules:
            if not self.fh.does_path_exist(path):
                continue

            module = self._load_module(path)
            if module and hasattr(module, 'Module'):
                module_instance = module.Module(self.app_window)
                if hasattr(module_instance, 'setup_ui'):
                    module_instance.setup_ui()

                loaded_modules.append(module_instance)

        self.modules = loaded_modules

    def _get_modules(self) -> list:
        """
        Retrieves a list of GUI modules from the modules directory.

        Returns:
            A list of paths to GUI modules from the modules directory.
        """
        path = self.fh.paths.get("gui_modules_path")

        if not self.fh.does_path_exist(path):
            return []

        files = glob.glob(f"{path}/*.py")

        return files

    def _load_module(self, module_path: str):
        """
        Loads a module from the given path.

        Args:
            module_path (str): The path to the module file.

        Returns:
            The loaded module object, or None if loading fails.
        """
        try:
            module_name = os.path.basename(module_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        except ModuleNotFoundError as e:
            print(f"Error loading module {module_path}: {e}")
            return None
