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

        self.redbarrier_sprite: QPixmap = self.renderer.images.get_image('redbarrier')

        self.is_item_in_scene = False
        self.build_overlays()

        self.last_composite_size = (0, 0) # track size to avoid regenerating the final pixmap

    def build_overlays(self) -> None:
        # called when map is reset
        self.is_item_in_scene = False
        self.overlay_item = QGraphicsPixmapItem()
        self.overlay_item.setZValue(900_000) # render on top of most things
        self.overlay_item.hide()

        self._ensure_item_in_scene()

    def _ensure_item_in_scene(self) -> bool:
        if self.is_item_in_scene:
            return True

        scene = self.renderer.canvas.canvas
        if scene:
            scene.addItem(self.overlay_item)
            self.is_item_in_scene = True
            return True

        return False

    def on_place_block(self, placing: CItem, grid_pos: Vec2f) -> None:
        name = placing.name_data.name
        if name not in self.important_item_names:
            return

        self.items[grid_pos] = name
        self.render_extra_overlay() # trigger a redraw

    def on_erase_block(self, grid_pos: Vec2f) -> None:
        if self.items.pop(grid_pos, None):
            self.render_extra_overlay() # trigger a redraw

    def render_extra_overlay(self) -> None:
        if self.redbarrier_sprite is None or not self._ensure_item_in_scene():
            return

        is_redbarrier_visible = self.communicator.view.get("redbarrier", False)
        is_nobuild_visible = self.communicator.view.get("nobuild_edges", False)

        if not is_redbarrier_visible and not is_nobuild_visible:
            self.overlay_item.hide()
            return

        self.overlay_item.show()

        map_width_scene = self.canvas.size.x * self.canvas.grid_spacing
        map_height_scene = self.canvas.size.y * self.canvas.grid_spacing

        # create a single large transparent pixmap to draw everything on
        composite_pixmap = QPixmap(int(map_width_scene), int(map_height_scene))
        composite_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(composite_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)

        # draw the main red barrier if visible
        if is_redbarrier_visible:
            self._draw_main_barrier(painter)

        # draw the no-build edge barriers if visible
        if is_nobuild_visible:
            self._draw_nobuild_edges(painter)

        painter.end()

        # final combined pixmap on our single item
        self.overlay_item.setPixmap(composite_pixmap)
        self.overlay_item.setPos(0, 0) # position the item at the top-left of the scene

    def _draw_main_barrier(self, painter: QPainter):
        map_width_tiles = self.canvas.size.x
        grid_spacing = self.canvas.grid_spacing

        scene_x1, scene_x2 = self._calculate_barrier_bounds_in_scene_coords(map_width_tiles, grid_spacing)

        width = int(scene_x2 - scene_x1)
        height = int(self.canvas.size.y * grid_spacing)

        if width > 0 and height > 0:
            tiled_pixmap = self._create_tiled_pixmap(self.redbarrier_sprite, width, height)
            painter.drawPixmap(int(scene_x1), 0, tiled_pixmap)

    def _draw_nobuild_edges(self, painter: QPainter):
        map_width_tiles = self.canvas.size.x
        map_height_tiles = self.canvas.size.y
        grid_spacing = self.canvas.grid_spacing
        zone_thickness_grid = 2

        zone_thickness_scene = zone_thickness_grid * grid_spacing
        map_width_scene = map_width_tiles * grid_spacing
        map_height_scene = map_height_tiles * grid_spacing

        edge_configs = {
            'top': (0, 0, map_width_scene, zone_thickness_scene + (1 * grid_spacing)),
            'left': (0, 0, zone_thickness_scene, map_height_scene),
            'right': (map_width_scene - zone_thickness_scene, 0, zone_thickness_scene, map_height_scene),
        }

        for _, config in edge_configs.items():
            x, y, width, height = map(int, config)
            if width > 0 and height > 0:
                tiled_pixmap = self._create_tiled_pixmap(self.redbarrier_sprite, width, height)
                painter.drawPixmap(x, y, tiled_pixmap)

    def _calculate_barrier_bounds_in_scene_coords(self, map_width_tiles: int, grid_spacing: float) -> tuple[float, float]:
        barrier_markers = [pos for pos, name in self.items.items() if name == "redbarrier"]
        if len(barrier_markers) == 2:
            grid_x1, grid_x2 = barrier_markers[0].x, barrier_markers[1].x
            left_grid_x = min(grid_x1, grid_x2)
            right_grid_x = max(grid_x1, grid_x2) + 1

        else:
            barrier_percent = 0.175
            map_middle_grid = map_width_tiles * 0.5
            barrier_width_grid = math.floor(barrier_percent * map_width_tiles)
            extra_width_grid = 0.5 if map_width_tiles % 2 == 1 else 0.0
            left_grid_x = map_middle_grid - (barrier_width_grid + extra_width_grid)
            right_grid_x = map_middle_grid + (barrier_width_grid + extra_width_grid)

        return left_grid_x * grid_spacing, right_grid_x * grid_spacing

    def _create_tiled_pixmap(self, source_sprite: QPixmap, width: int, height: int) -> QPixmap:
        # create a tiled pixmap of a certain size
        scale = self.canvas.default_zoom_scale
        composite_pixmap = QPixmap(width, height)
        composite_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(composite_pixmap)

        scaled_sprite = source_sprite.scaled(
            int(source_sprite.width() * scale),
            int(source_sprite.height() * scale)
        )
        sprite_w, sprite_h = scaled_sprite.width(), scaled_sprite.height()

        if sprite_w == 0 or sprite_h == 0:
            painter.end()
            return composite_pixmap

        for y in range(0, height, sprite_h):
            for x in range(0, width, sprite_w):
                painter.drawPixmap(x, y, scaled_sprite)

        painter.end()
        return composite_pixmap
