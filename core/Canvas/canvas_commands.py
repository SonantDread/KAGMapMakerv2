"""
Manages undo/redo functions in the canvas.
"""
class PlaceTileCommand:
    """
    A command to place (or erase) a single tile on the canvas.
    """
    def __init__(self, canvas, grid_pos: 'Vec2f', new_item, previous_item):
        self.canvas = canvas
        self.grid_pos = grid_pos

        self.new_item = new_item
        self.previous_item = previous_item

    def execute(self) -> None:
        """
        Executes the placement of the new tile.
        """
        self.canvas.place_item(self.grid_pos, self.new_item, add_to_history=False)

    def undo(self) -> None:
        """
        Undoes the placement by restoring the previous tile.
        """
        item_to_restore = self.previous_item
        if item_to_restore is None:
            item_to_restore = self.canvas.item_list.get_item_by_name('sky').copy()

        self.canvas.place_item(self.grid_pos, item_to_restore, add_to_history=False)
