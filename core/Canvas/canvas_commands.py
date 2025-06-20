from abc import ABC, abstractmethod

class Command(ABC):
    """
    An abstract base class for a command that can be executed and undone.
    """
    @abstractmethod
    def execute(self) -> None:
        """
        Applies the command's action.
        """
        pass

    @abstractmethod
    def undo(self) -> None:
        """
        Reverts the command's action.
        """
        pass

class PlaceTileCommand(Command):
    """
    A command to place (or erase) a single tile on the canvas.
    """
    def __init__(self, canvas, grid_pos: tuple, new_item, previous_item):
        self.canvas = canvas
        self.grid_pos = grid_pos
        # the tile being placed
        self.new_item = new_item
        # the tile that was there before (or None)
        self.previous_item = previous_item

    def execute(self) -> None:
        """
        Executes the placement of the new tile.
        """
        self.canvas.perform_place_item(self.grid_pos, self.new_item)

    def undo(self) -> None:
        """
        Undoes the placement by restoring the previous tile.
        """
        # if the previous item was None, we need to place an empty/sky tile to erase
        item_to_restore = self.previous_item
        if item_to_restore is None:
            item_to_restore = self.canvas.item_list.get_item_by_name('sky').copy()

        self.canvas.perform_place_item(self.grid_pos, item_to_restore)
