class Tile:
    def __init__(self, img, tile_name, tile_image, pos, rotation = 0, team = 255, z = 0, scale = 1, index = None, color = None, layer = 0):
        self.img = img # the image class is passed here to prevent lag
        self.main(tile_name, tile_image, pos, rotation, team, z, index, color, scale, layer)

    def main(self, tile_name, tile_image, pos, rotation, team, z, index, color, scale, layer):       
        self.tile_name = tile_name
        self.tile_image = tile_image

        # assume scaled positions
        self.x = int(pos[0] / scale / 8)
        self.y = int(pos[1] / scale / 8)

        self.index = self.img.getTileIndexByName(tile_name)
        self.color = self.img.getKAGMapPixelColorByName(tile_name)

        self.z = z
        self.rotation = rotation # 0 = up, 1 = right, 2 = down, 3 = left
        self.team = team

        # unused for now
        self.layer = layer

    def Update(self, tile_name, tile_image, pos, rotation, team, z = 0, index = None, color = None, scale = 1, layer = 0):
        self.main(tile_name, tile_image, pos, rotation, team, z, index, color, scale, layer)

    def get_tile_name(self):
        return self.tile_name

    def get_z(self):
        return self.z
    
    def get_rotation(self):
        return self.rotation
    
    def get_team(self):
        return self.team

    def get_tile_image(self):
        return self.tile_image

    def get_pos(self, scale: int = None):
        # 'scale' should be the canvas scale
        if scale is None:
            return (self.x, self.y)
        else:
            return (self.x * scale * 8, self.y * scale * 8)

    def get_index(self):
        return self.index

    def get_color(self):
        return self.color
    
    def get_layer(self):
        return self.layer
    
    def __str__(self):
        return f"Block Name: {self.get_tile_name()}, Pos: {self.get_pos()}"