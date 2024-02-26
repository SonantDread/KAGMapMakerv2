class CanvasSettings:
    def __init__(self, canvas):
        self.canvas = canvas
        self.show_grid = True

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.canvas.update()  # Trigger a redraw of the canvas
