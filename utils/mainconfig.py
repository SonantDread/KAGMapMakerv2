import os
import json
from PyQt6.QtCore import QObject, pyqtSignal, QEvent

from utils.windowsettings import Window
from utils.vec import vec

class Config(QObject):
    resize = pyqtSignal(QEvent)

    def __init__(self):
        super().__init__()

        self.path = 'config.json'
        self.default = 'readonly_config.json'

        self.data = {}
        if self.validate():
            self.update(self.path)
        else:
            self.update(self.default)
    
    def save(self):
        with open(self.path, 'w') as json_file:
            json.dumps(self.data, json_file, indent = 4, sort_keys = True)
            print("Saving config")
            print(f"Data: {self.data}")
    
    def update(self, config_path):
        if os.path.exists(config_path):
            with open(config_path, 'r') as json_file:
                data = json_file.read()
                if data:
                    try:
                        self.data = json.loads(data)
                        print("Updating config")
                        print(f"Data: {self.data}")
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {config_path}")
                else:
                    print(f"File {config_path} is empty")
        else:
            print(f"File {config_path} not found")

    def resize_to_window(self, event):
        with open(self.path, 'w') as json_file:
            ws = self.window.get_window_size()
            
            window_config = self.data.get('window', {})
            window_config['size'] = {'width': str(ws.x), 'height': str(ws.y)}
            self.data['window'] = window_config

            print(f"Resizing window to {ws.x},{ws.y}")
            
            self.save()
            self.resize.emit(event)

    def validate(self):
        try:
            with open(self.path, 'r') as json_file:
                data = json_file.read()
                if data:
                    json.loads(data)
                    return True
                else:
                    print(f"File {self.path} is empty")
                    return False
        except FileNotFoundError:
            print(f"Could not find {self.path}")
            return False
