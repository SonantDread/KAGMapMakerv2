from core.Canvas.canvas_commands import Command

class HistoryManager:
    """
    Manages a stack of commands for undo and redo functionality.
    """
    def __init__(self):
        self._history: list[Command] = []
        # points to the last executed command
        self._index: int = -1

    def execute_command(self, command: Command):
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
