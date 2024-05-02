import os
import json
from PyQt6.QtCore import QObject, pyqtSignal, QEvent

from utils.windowsettings import Window
from utils.vec import vec

class Config(QObject):
    build = pyqtSignal(QEvent)

    def __init__(self):
        super().__init__()

        self.path = 'settings/config.json'
        self.default = 'settings/readonly_config.json'

        self.data = {}
        if self.validate():
            print("Loading user config")
            self.update(self.path)
        else:
            print("Loading default config")
            self.reset()
    
    def save(self):
        with open(self.path, 'w') as json_file:
            json.dump(self.data, json_file, indent = 4, sort_keys = True)
            print("Saving config")
            print(f"Data: {self.data}")
    
    def update(self, config_path):
        if os.path.exists(config_path):
            with open(config_path, 'r') as json_file:
                data = json_file.read()
                if data:
                    try:
                        self.data = json.loads(data)
                        print("Updating window settings")
                        print(f"Data: {self.data}")
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in {config_path}")
                else:
                    print(f"File {config_path} is empty")
        else:
            print(f"File {config_path} not found")

    def build_from_active_window(self, event):
        with open(self.path, 'w') as json_file:
            # WINDOW
            try: window_config = self.data.get('window', {})
            except Exception as e:
                print(e)
                return

            # window size
            ws = self.window.get_window_size()
            window_config['size'] = {'width': ws.x, 'height': ws.y}
            print(f"Resizing window to {ws.x},{ws.y}")

            # window offsets
            wm = self.window.get_window_offset()
            window_config['offset'] = {'left': wm.x, 'top': wm.y}
            print(f"Setting window offset to {wm.x},{wm.y}")
        
            # SAVE
            self.data['window'] = window_config
            self.save()
            self.build.emit(event)

    def validate(self):
        try:
            with open(self.path, 'r') as json_file:
                data = json_file.read()
                if data:
                    try: 
                        json.loads(data)
                        return True
                    except Exception as e:
                        print(e)
                        return False
                else:
                    print(f"File {self.path} is empty")
                    return False
        except FileNotFoundError:
            print(f"Could not find {self.path}")
            return False

    def reset(self):
        self.update(self.default)