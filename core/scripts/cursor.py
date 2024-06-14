from base.Tile import Tile

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Cursor(metaclass=SingletonMeta):
    def __init__(self):
        self.picked_tiles = [None, None]

    def selectTile(self, tile: Tile, idx=0):
        self.picked_tiles[idx] = tile

    def getSelectedTile(self, idx: int) -> Tile:
        return self.picked_tiles[min(len(self.picked_tiles), max(0, idx))]
