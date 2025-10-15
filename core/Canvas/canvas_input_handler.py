"""
Handles inputs directly on the canvas.
"""
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QGraphicsView

from utils.vec2f import Vec2f

class CanvasInputHandler(QGraphicsView):
    """
    Handles PyQt6 events for the canvas.
    """
    def __init__(self, *args, **kwargs)-> None:
        super().__init__(*args, **kwargs)
        self._holding_lmb = False
        self._holding_rmb = False
        self._holding_scw = False
        self._holding_space = False
        self._last_pan_point = None

    def mousePressEvent(self, event) -> None:
        """
        Handles mouse press events on the canvas.
        """
        if event is None:
            return

        self.update_mouse_pos(event)

        # place blocks
        if event.button() == Qt.MouseButton.LeftButton:
            self._holding_lmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos)

        elif event.button() == Qt.MouseButton.RightButton:
            self._holding_rmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos, click_index=0)

        if event.button() == Qt.MouseButton.MiddleButton:
            self._last_pan_point = event.pos()
            self._holding_scw = True

    def resizeEvent(self, event) -> None:
        """
        Handles the resize event of the QGraphicsView to adjust the scene accordingly.
        """
        if event is None:
            return

        super().resizeEvent(event)

    def keyPressEvent(self, event: Optional[QKeyEvent]):
        """
        Handles key press events on the canvas.
        """
        if event is None:
            return

        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._last_pan_point = self.get_cursor_pos_on_canvas()
            self._holding_space = True

    def keyReleaseEvent(self, event: Optional[QKeyEvent]):
        """
        Handles key release events on the canvas.
        """
        if event is None:
            return

        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._holding_space = False
            self._set_cursor()

    def mouseDoubleClickEvent(self, event) -> None:
        """
        Handles mouse press events on the canvas.
        """
        if event is None:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._holding_lmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos)

        elif event.button() == Qt.MouseButton.RightButton:
            self._holding_rmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos, click_index=0)

    def mouseReleaseEvent(self, event) -> None:
        """
        Handles mouse release events on the canvas.
        """
        if event is None:
            return

        self.update_mouse_pos(event)

        if event.button() == Qt.MouseButton.LeftButton:
            self._holding_lmb = False

        elif event.button() == Qt.MouseButton.RightButton:
            self._holding_rmb = False

        elif event.button() == Qt.MouseButton.MiddleButton:
            self._holding_scw = False

    def mouseMoveEvent(self, event) -> None:
        """
        Handles mouse movement events on the canvas.
        """
        if event is None:
            return

        pos = self.get_grid_pos(event)
        old_pos = self.communicator.old_mouse_pos

        same_tile = pos == old_pos

        if self._holding_lmb and not same_tile:
            self.draw_to_cursor(event, 1)

        elif self._holding_rmb and not same_tile:
            self.draw_to_cursor(event, 0)

        viewport = self.viewport()

        if self._holding_scw or self._holding_space:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if viewport is not None:
                viewport.setCursor(Qt.CursorShape.ClosedHandCursor)

            # calculate how much the mouse has moved
            if self._last_pan_point is not None:
                delta = event.pos() - self._last_pan_point
                self._last_pan_point = event.pos()

                h_scroll = self.horizontalScrollBar()
                v_scroll = self.verticalScrollBar()
                if h_scroll is not None:
                    h_scroll.setValue(h_scroll.value() - delta.x())

                if v_scroll is not None:
                    v_scroll.setValue(v_scroll.value() - delta.y())

        else:
            self._set_cursor()

        # render the cursor
        scene_pos = self.mapToScene(event.pos())
        x, y = self.snap_to_grid((scene_pos.x(), scene_pos.y()))
        if self.renderer is not None and hasattr(self.renderer, "render_cursor"):
            grid_spacing = self.grid_spacing if self.grid_spacing is not None else 1
            self.renderer.render_cursor(Vec2f(x * grid_spacing, y * grid_spacing))

    def _set_cursor(self) -> None:
        """
        Sets the cursor to an ArrowCursor and prevents dragging.
        """
        viewport = self.viewport()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        if viewport is not None:
            viewport.unsetCursor()

    def wheelEvent(self, event) -> None:
        """
        Handles wheel events on the canvas, allowing for zooming and panning.
        """
        if event is None:
            return

        delta_y = event.angleDelta().y()

        if self.zoom_change_factor is None:
            return

        factor = pow(self.zoom_change_factor, abs(delta_y) / 120)
        if delta_y < 0:
            factor = 1 / factor

        view_pos = event.position()
        scene_pos = self.mapToScene(view_pos.toPoint())
        self.scale(factor, factor)

        new_scene_pos = self.mapToScene(view_pos.toPoint())
        delta = new_scene_pos - scene_pos

        h_scroll = self.horizontalScrollBar()
        v_scroll = self.verticalScrollBar()
        if h_scroll is not None:
            h_scroll.setValue(int(h_scroll.value() - delta.x()))
        if v_scroll is not None:
            v_scroll.setValue(int(v_scroll.value() - delta.y()))
