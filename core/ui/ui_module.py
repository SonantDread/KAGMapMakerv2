from utils.vec import vec

class ui_module:
    def __init__(self):
        self.pos = vec(0,0)
        self.id = 0

    def set_id(self, id):
        self.id = id

    def set_pos(self, vec):
        self.pos = vec
