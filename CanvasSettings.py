class CanvasSettings:
    def __init__(self, canvas):
        self.canvas = canvas
        self.show_grid = True

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.canvas.viewport().repaint()  # Force an immediate repaint of the viewport (redraw the canvas)
    
    # TODO: brush size
    # TODO: lock x / y after holding left click
