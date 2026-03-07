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
Manages the left sidebar.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from core.modules.picker import Picker
from core.modules.teams import Teams
from utils.file_handler import FileHandler

class GUIModuleHandler:
    """
    Sets up the left sidebar and handles the layout.
    """
    def __init__(self, window: QWidget):
        self.fh = FileHandler()
        self.app_window = window
        self.modules = []

        self.central_widget = QWidget(self.app_window)

        self.container = QVBoxLayout(self.central_widget)
        self.container.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.central_widget.setFixedSize(400, 280)

        self.setup_modules()

    def setup_modules(self):
        """
        Creates the left sidebar.
        """
        buffer = 20
        current_height = 0

        picker = Picker(self.app_window)
        current_height += picker.tab_holder.height() + buffer + 16

        teams = Teams(self.app_window, current_height)
        current_height += teams.widget.height() + buffer

        self.container.addWidget(picker)
        self.container.addWidget(teams)

        self.modules.extend([picker, teams])
