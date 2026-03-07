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
Handles the history for the canvas.
"""
from core.Canvas.canvas_commands import PlaceTileCommand

class HistoryManager:
    """
    Manages a stack of commands for undo and redo functionality.
    """
    def __init__(self):
        self._history: list[PlaceTileCommand] = []
        # points to the last executed command
        self._index: int = -1

    def execute_command(self, command: PlaceTileCommand):
        """
        Executes a new command and adds it to the history.
        This will clear any 'redo' history.
        """
        # if we have undone actions, clear them from the history
        if self._index < len(self._history) - 1:
            self._history = self._history[:self._index + 1]

        self._history.append(command)
        command.execute()
        self._index += 1

        # limit history size
        if len(self._history) > 1000:
            self._history.pop(0)
            self._index -= 1

    def undo(self):
        """
        Undoes the last command.
        """
        if self.can_undo():
            self._history[self._index].undo()
            self._index -= 1

    def redo(self):
        """
        Redoes the next command in the history.
        """
        if self.can_redo():
            self._index += 1
            self._history[self._index].execute()

    def can_undo(self) -> bool:
        """
        Check if there is an action to undo.
        """
        return self._index >= 0

    def can_redo(self) -> bool:
        """
        Check if there is an action to redo.
        """
        return self._index < len(self._history) - 1

    def clear(self):
        """
        Clears the entire history stack.
        """
        self._history.clear()
        self._index = -1
