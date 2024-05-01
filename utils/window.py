from utils.vec import vec

class Window:
    def __init__(self, window):
        self.window = window

    def get_window_size(self):
        return vec(self.window.width(), self.window.height())
