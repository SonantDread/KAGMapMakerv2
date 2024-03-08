from Image import Image

class Tile:
    def __init__(self, tile_name, tile_image, pos, layer = 0):
        img = Image()
        # NOTE THAT THE X AND Y NEED TO BE RAW POSITIONS, NOT SCALED
        self.tile_name = tile_name
        self.tile_image = tile_image

        self.x = pos[0]
        self.y = pos[1]

        self.index = img.getTileIndexByName(tile_name)
        self.color = img.getKAGMapPixelColorByName(tile_name)

        # unused for now
        # self.layer = layer

    def get_tile_name(self):
        return self.tile_name

    def get_tile_image(self):
        return self.tile_image

    def get_pos(self, scale: int = None):
        if scale is None:
            return (self.x, self.y)
        else:
            return (self.x * scale * 8, self.y * scale * 8)

    def get_index(self):
        return self.index

    def get_color(self):
        return self.color