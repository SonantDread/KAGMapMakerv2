from PIL import Image
from tkinter import filedialog
from Image import Image as img
from PyQt5.QtWidgets import QGraphicsPixmapItem
from Canvas import Canvas as can
import os
import numpy as np

path = os.path.dirname(os.path.abspath(__file__))

class KagImage:
    def __init__(self, canvas):
        self.canvas = canvas
        self.map = self.canvas.blocks

    def saveMap(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Images", "*.png")])
        if not filepath: return False
        cimg  = img()
        
        image = Image.new("RGBA", (self.canvas.width, self.canvas.height), color = (165, 189, 200))

        for key, value in self.map.items():
            x, y = int(key[0] / self.canvas.canvas_scale / 8), int(key[1] / self.canvas.canvas_scale / 8)
            print(x, y)
            
            block = value[1]

            color = cimg.getKAGMapPixelColorByName(block)
            a, r, g, b = color
            color = (r, g, b, a)

            image.putpixel((x, y), color)

        if not os.path.exists(os.path.join(path, "Maps")):
            os.makedirs(os.path.join(path, "Maps"), exist_ok=True)

        image.save(filepath)
        return True
    
    def loadMap(self): # todo: optimize this more
        self.canvas.blockUpdates()
        filepath = filedialog.askopenfilename(defaultextension=".png", filetypes=[("Images", "*.png")])

        if not filepath: return False

        image = Image.open(filepath).convert("RGBA")
        width, height = image.size

        pixel_array = np.array(image)
        items_to_add = []
        canv = can()
        imgb = img()

        blockimgs = {}
        used_blocks = []

        for x in range(width):
            for y in range(height):
                color = pixel_array[x][y]
                r, g, b, a = color
                color = (a, r, g, b)

                block = imgb.getKAGMapNameByPixelColor(color)

                if block == "sky":
                    continue
                
                block_pixmap = None
                if(block not in used_blocks): # dont load image if its already loaded
                    block_pixmap = canv.loadBlockImage(block)

                    blockimgs.update({block: block_pixmap})
                    used_blocks.append(block)
                
                else:
                    block_pixmap = blockimgs[block]

                pixmap_item = QGraphicsPixmapItem(block_pixmap)
                pixmap_item.setScale(self.canvas.canvas_scale)
                pixmap_item.setPos(x * self.canvas.canvas_scale * 8, y * self.canvas.canvas_scale * 8)
                items_to_add.append((pixmap_item, block))

        # clear canvas
        self.canvas.blocks = {}

        # Add all items to the scene in a single operation
        for pixmap_item, block in items_to_add:
            self.canvas.scene().addItem(pixmap_item)
            self.canvas.blocks[(pixmap_item.pos().x(), pixmap_item.pos().y())] = (pixmap_item, block)

        self.canvas.unblockUpdates()

        return True


    def renderMap(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Images", "*.png")], initialfile = "RENDER_")

        if not filepath: return False

        imageclass = img()
        width, height = self.canvas.width, self.canvas.height
        result_image = Image.new("RGBA", (width * 8, height * 8), color = (165, 189, 200))

        for key, value in self.map.items():
            # dictionary looks like: '(x, y): (image, block)'
            x, y = int(key[0] / self.canvas.canvas_scale / 8), int(key[1] / self.canvas.canvas_scale / 8)

            blockimage = imageclass.getBlockPNGByIndex(imageclass.getTileIndexByName(value[1]))

            paste_pos = ((x * 8), (y * 8))
            result_image.paste(blockimage, paste_pos)

        result_image.save(filepath)

        return True