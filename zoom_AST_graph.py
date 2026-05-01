
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import Qt


class ZoomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def zoom_in(self):
        self._apply_zoom(1.2)

    def zoom_out(self):
        self._apply_zoom(1 / 1.2)

    def zoom_reset(self):
        self.resetTransform()
        self._zoom = 1

    def _apply_zoom(self, factor):
        next_zoom = self._zoom * factor
        if next_zoom < 0.2 or next_zoom > 8.0:
            return
        self.scale(factor, factor)
        self._zoom = next_zoom

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.zoom_in()
            return
        if event.key() == Qt.Key.Key_Minus:
            self.zoom_out()
            return
        if event.key() == Qt.Key.Key_0:
            self.zoom_reset()
            return
        super().keyPressEvent(event)
