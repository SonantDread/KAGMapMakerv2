from utils.vec import vec

class Window:
    def __init__(self, config):
        self.Config = config

    def get_window_size(self):
        return vec(self.Config.data['Window']['size']['width'], self.Config.data['Window']['size']['height'])