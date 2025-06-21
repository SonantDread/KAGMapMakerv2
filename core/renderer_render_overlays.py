import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

from base.citem import CItem
from utils.vec2f import Vec2f

class RenderOverlays:
    def __init__(self, renderer, communicator) -> None:
        self.renderer = renderer
        self.communicator = communicator
        self.canvas = renderer.canvas

        self.important_item_names = ["redbarrier"]
        self.items: dict[Vec2f, str] = {}

        self.redbarrier_sprite: QPixmap | None = self.renderer.images.get_image('redbarrier')

        self.barrier_item = QGraphicsPixmapItem()
        self.barrier_item.setZValue(900_000) # render on top of everything except cursor
        self.barrier_item.hide()

        # track the last rendered size to know when to regenerate the barrier pixmap
        self.last_barrier_size = (0, 0)

        self._is_redbarrier_in_scene = False

    def on_place_block(self, placing: CItem, grid_pos: Vec2f) -> None:
        name = placing.name_data.name
        if name not in self.important_item_names:
            return

        self.items[grid_pos] = name
        self.update_redbarrier()

    def on_erase_block(self, grid_pos: Vec2f) -> None:
        if self.items.pop(grid_pos, None):
            self.update_redbarrier()

    def render_extra_overlay(self) -> None:
        self.update_redbarrier()

    def _ensure_item_in_scene(self) -> bool:
        if self._is_redbarrier_in_scene:
            return True

        scene = self.renderer.canvas.canvas
        if scene:
            scene.addItem(self.barrier_item)
            self._is_redbarrier_in_scene = True
            return True

        # scene is not ready, try again on the next frame
        return False

    def update_redbarrier(self) -> None:
        if self.redbarrier_sprite is None or not self._ensure_item_in_scene():
            return

        # check for visibility based on communicator state
        if not self.communicator.view.get("redbarrier", False):
            self.barrier_item.hide()
            return
        self.barrier_item.show()

        # calculate the bounds of the barrier in scene coordinates
        map_width_tiles = self.canvas.size.x
        grid_spacing = self.canvas.grid_spacing

        scene_x1, scene_x2 = self._calculate_barrier_bounds_in_scene_coords(
            map_width_tiles, grid_spacing
        )

        # determine the required pixmap size
        barrier_width = int(scene_x2 - scene_x1)
        barrier_height = int(self.canvas.size.y * grid_spacing)
        current_size = (barrier_width, barrier_height)

        # regenerate the barrier's pixmap only if its size has changed
        if self.last_barrier_size != current_size and barrier_width > 0 and barrier_height > 0:
            scale = self.canvas.default_zoom_scale

            new_pixmap = self._create_tiled_pixmap(
                source_sprite=self.redbarrier_sprite,
                width=barrier_width,
                height=barrier_height,
                scale=scale
            )

            self.barrier_item.setPixmap(new_pixmap)
            self.last_barrier_size = current_size

        # ensure the barrier is positioned correctly
        self.barrier_item.setPos(scene_x1, 0)

    def _calculate_barrier_bounds_in_scene_coords(self, map_width_tiles: int, grid_spacing: float) -> tuple[float, float]:
        barrier_markers = [pos for pos, name in self.items.items() if name == "redbarrier"]

        if len(barrier_markers) == 2:
            # use explicit marker positions
            grid_x1, grid_x2 = barrier_markers[0].x, barrier_markers[1].x
            left_grid_x = min(grid_x1, grid_x2)
            right_grid_x = max(grid_x1, grid_x2) + 1 # +1 to include the tile itself

        else:
            # default percentage-based barrier
            barrier_percent = 0.175
            map_middle_grid = map_width_tiles * 0.5
            barrier_width_grid = math.floor(barrier_percent * map_width_tiles)
            # add a small offset for odd-width maps to keep it centered
            extra_width_grid = 0.5 if map_width_tiles % 2 == 1 else 0.0

            left_grid_x = map_middle_grid - (barrier_width_grid + extra_width_grid)
            right_grid_x = map_middle_grid + (barrier_width_grid + extra_width_grid)

        # convert grid coordinates to scene (pixel) coordinates
        scene_x1 = left_grid_x * grid_spacing
        scene_x2 = right_grid_x * grid_spacing

        return scene_x1, scene_x2

    @staticmethod
    def _create_tiled_pixmap(source_sprite: QPixmap, width: int, height: int, scale: float) -> QPixmap:
        # create a new, large, transparent pixmap to draw on
        composite_pixmap = QPixmap(width, height)
        composite_pixmap.fill(Qt.GlobalColor.transparent)

        # prepare to draw on our new large pixmap
        painter = QPainter(composite_pixmap)

        # the barrier sprite should be scaled just like regular tiles
        scaled_sprite = source_sprite.scaled(
            int(source_sprite.width() * scale),
            int(source_sprite.height() * scale)
        )
        sprite_w, sprite_h = scaled_sprite.width(), scaled_sprite.height()

        if sprite_w == 0 or sprite_h == 0:
            painter.end()
            return composite_pixmap # return transparent pixmap if sprite is invalid

        # tile the scaled sprite across the large pixmap
        for y in range(0, height, sprite_h):
            for x in range(0, width, sprite_w):
                painter.drawPixmap(x, y, scaled_sprite)

        painter.end()
        return composite_pixmap
