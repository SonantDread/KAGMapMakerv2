# KAGMapMakerV2 - An unofficial map maker for King Arthur's Gold.
# Copyright (C) 2026 SonantDread
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
