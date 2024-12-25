"""
Used for all files to communicate between each other
All data in this class is shared.
"""

class SingletonMeta(type):
    """
    Used to share code between all instances of the class.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Communicator(metaclass = SingletonMeta):
    """
    Used to communicate information between classes.
    """
    def __init__(self):
        self.picked_tiles = ["tile_ground", "tile_empty"]
        self.canvas = None
        self.exec_path = None
        self.settings = {}

    def select_item(self, tile: str, idx: int = 0): # 1 = lmb, 0 = rmb
        """
        Selects an item to be used in the application.

        Args:
            tile (str): The name of the tile to select.
            idx (int, optional): The index of the selected tile. Defaults to 0.

        Returns:
            None
        """
        self.picked_tiles[idx] = tile

    def set_exec_path(self, path: str):
        """
        Sets the execution path for the application.

        Args:
            path (str): The path to set as the execution path.

        Returns:
            None
        """
        self.exec_path = path

    def get_selected_tile(self, idx: int) -> str:
        """
        Retrieves the name of the tile at the specified index.

        Args:
            idx (int): The index of the tile to retrieve.

        Returns:
            str: The name of the tile at the specified index.
        """
        return self.picked_tiles[min(len(self.picked_tiles), max(0, idx))]

    def set_canvas(self, canvas):
        """
        Sets the canvas for the Communicator class.

        Args:
            canvas: The canvas to be set.

        Returns:
            None
        """
        self.canvas = canvas

    def get_canvas(self):
        """
        Retrieves the currently set canvas.
        
        Returns:
            The currently set canvas.
        """
        return self.canvas
