import json

from utils.window import Window
from utils.vec import vec

class Config:
    def __init__(self):
        self.data = {}
        self.update()
        self.window = Window(self)
    
    # save JSON file from class
    def save(self):
        with open('config.json', 'w') as json_file:
            json.dump(self.data, json_file)
            print("Saving config")
    
    # load JSON file into class
    def update(self):
        with open('config.json', 'r') as json_file:
            self.data = json.load(json_file)
            print("Updating config")

    def resize_to_window(self):
        with open('config.json', 'w') as json_file:
            ws = self.window.get_window_size(self)
            print(ws)
            
            window_config = Config().data['window']
            window_config['width'] = str(ws.x)
            window_config['height'] = str(ws.y)

            self.data['window'] = window_config

            json.dump(self.data, json_file)
            print("Resize config")
