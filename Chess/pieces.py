from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainter, QColor, QPixmap


class MapSquare(QGraphicsItem):
    def __init__(self, x, y, size, color):
        super().__init__()
        self.rect = QRectF(x, y, size, size)
        self.color = color
        self.old_color = None
        self.is_legal = False

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter, option, widget=None):
        fill_color = QColor(*self.color)
        painter.fillRect(self.rect, fill_color)


class Pieces(QGraphicsItem):
    def __init__(self, x, y, size, color, number_of_moves=0):
        super().__init__()
        self.color = color
        self.size = size
        self.image_path = self.set_pixmap()  # Set the image path based on color
        self.pixmap = QPixmap(self.image_path)
        self.setPos(x, y)
        self.number_of_moves = number_of_moves
        self.moves = self.moves()

    def set_pixmap(self):
        pass

    def moves(self):
        pass

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter: QPainter, option, widget=None):
        painter.drawPixmap(0, 0, self.size, self.size, self.pixmap)


class Pawn(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/pawn-{self.color[0]}.svg")

    def moves(self):
        if self.number_of_moves == 0:
            if self.color == "white":
                return [(-1, 0), (-2, 0)]
            else:
                return [(1, 0), (2, 0)]
        else:
            return self.after_first_move()

    def after_first_move(self):
        if self.color == "white":
            return [(-1, 0)]
        else:
            return [(1, 0)]

    def try_take(self):
        if self.color == "white":
            return [(-1, -1), (-1, 1)]
        else:
            return [(1, -1), (1, 1)]


class Rook(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/rook-{self.color[0]}.svg")

    def moves(self):
        return [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
                (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7),
                (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]


class Knight(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/knight-{self.color[0]}.svg")

    def moves(self):
        return [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]


class Bishop(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/bishop-{self.color[0]}.svg")

    def moves(self):
        return [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7),
                (1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7),
                (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7),
                (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]


class Queen(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/queen-{self.color[0]}.svg")

    def moves(self):
        return [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, -1), (0, -2), (0, -3), (0, -4), (0, -5),
                (0, -6), (0, -7), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (-1, 0), (-2, 0), (-3, 0),
                (-4, 0), (-5, 0), (-6, 0), (-7, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (1, -1),
                (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7), (-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5),
                (-6, 6), (-7, 7), (-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)]


class King(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/king-{self.color[0]}.svg")

    def moves(self):
        return [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
