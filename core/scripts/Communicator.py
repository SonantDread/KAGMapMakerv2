# Used for all files to communicate between each other
# All data in this class is shared.

# TODO: any class that is created more than once should be held in this.
# TODO: execution path from app.py should be held in this file

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Communicator(metaclass = SingletonMeta):
    def __init__(self):
        self.picked_tiles = ["tile_ground", "tile_empty"] # TODO: make these start as a class so you can actually place them

    def selectItem(self, tile: str, idx: int = 0): # 1 = lmb, 0 = rmb
        self.picked_tiles[idx] = tile

    def getSelectedTile(self, idx: int) -> str:
        return self.picked_tiles[min(len(self.picked_tiles), max(0, idx))]
    
    def getSelectedTiles(self) -> list:
        return self.picked_tiles
    
    def setCanvas(self, canvas):
        self.canvas = canvas
    
    def getCanvas(self):
        return self.canvas