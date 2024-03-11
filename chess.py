import sys
import time

from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QMessageBox, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QRectF, QTimer, QDateTime, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QKeyEvent, QPixmap, QTransform
import random


class MapSquare(QGraphicsItem):
    def __init__(self, x, y, size, color):
        super().__init__()
        self.rect = QRectF(x, y, size, size)
        self.color = color

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter, option, widget=None):
        fill_color = QColor(*self.color)
        painter.fillRect(self.rect, fill_color)

class Pieces(QGraphicsPixmapItem):  # Update: Inherit from QGraphicsPixmapItem
    def __init__(self, x, y, size,color):
        super().__init__()
        self.color = color
        self.pixmap = self.set_pixmap()
        self.setPixmap(self.pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio))
        self.setPos(x, y)

    def set_pixmap(self):
        pass

class Pawn(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/pawn_{self.color}.png")

class Rook(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/rook_{self.color}.png")

class Knight(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/knight_{self.color}.png")

class Bishop(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/bishop_{self.color}.png")

class Queen(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/queen_{self.color}.png")

class King(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/king_{self.color}.png")


class Chess(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.square_size = 80
        self.w_square = 8
        self.h_square = 8
        self.squares = []
        self.white_pieces = []
        self.black_pieces = []
        self.selected_piece = None
        self.initial_position = QPointF()
        self.initialize_map()

    def initialize_map(self):
        for row in range(self.h_square):
            for col in range(self.w_square):
                if (row + col) % 2 == 0:
                    color = (51, 102, 33, 255)
                else:
                    color = (255, 255, 204, 255)
                x = col * self.square_size
                y = row * self.square_size
                self.squares.append(MapSquare(x, y, self.square_size, color))
                self.addItem(self.squares[-1])

        self.add_labels()  # Add labels after squares are created

        # add white pawns
        for i in range(8):
            self.white_pieces.append(Pawn(i * 80, self.square_size * 6, self.square_size, "white"))
            self.black_pieces.append(Pawn(i * 80, self.square_size * 1, self.square_size, "black"))

        for col in [0, 7]:  # Loop for the left and right rooks
            x_pos = col * self.square_size
            self.white_pieces.append(Rook(x_pos, self.square_size * 7, self.square_size, "white"))
            self.black_pieces.append(Rook(x_pos, 0, self.square_size, "black"))

            # Knights
        for col in [1, 6]:
            x_pos = col * self.square_size
            self.white_pieces.append(Knight(x_pos, self.square_size * 7, self.square_size, "white"))
            self.black_pieces.append(Knight(x_pos, 0, self.square_size, "black"))

            # Bishops
        for col in [2, 5]:
            x_pos = col * self.square_size
            self.white_pieces.append(Bishop(x_pos, self.square_size * 7, self.square_size, "white"))
            self.black_pieces.append(Bishop(x_pos, 0, self.square_size, "black"))

            # Queen
        self.white_pieces.append(Queen(3 * self.square_size, self.square_size * 7, self.square_size, "white"))
        self.black_pieces.append(Queen(3 * self.square_size, 0, self.square_size, "black"))

        # King
        self.white_pieces.append(King(4 * self.square_size, self.square_size * 7, self.square_size, "white"))
        self.black_pieces.append(King(4 * self.square_size, 0, self.square_size, "black"))

        for piece in self.white_pieces:
            self.addItem(piece)
        for piece in self.black_pieces:
            self.addItem(piece)

    def add_labels(self):
            font = QFont("Arial", 16, QFont.Weight.Bold)
            font_color = QColor(255, 255, 255)
            # Labels for files (a-h)
            for col in range(self.w_square):
                file_label = QGraphicsTextItem(chr(ord("a") + col))  # Calculate letters
                file_label.setFont(font)
                file_label.setDefaultTextColor(font_color)
                file_label.setPos(col * self.square_size + 30, self.h_square * self.square_size + 10)
                self.addItem(file_label)

            # Labels for ranks (1-8)
            for row in range(self.h_square):
                rank_label = QGraphicsTextItem(str(self.h_square - row))  # Inverted for chess
                rank_label.setFont(font)
                rank_label.setDefaultTextColor(font_color)
                rank_label.setPos(self.w_square * self.square_size + 30, row * self.square_size + 30)
                self.addItem(rank_label)

    def mousePressEvent(self, event):
        items = self.items(event.scenePos())

        # Check if any piece is clicked
        for item in items:
            if isinstance(item, Pieces):
                self.selected_piece = item
                self.initial_position = item.pos()
                break

        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if self.selected_piece is not None:
            # Move the piece with the mouse
            new_position = event.scenePos() - QPointF(self.square_size / 2, self.square_size / 2)
            self.selected_piece.setPos(new_position)

    def mouseReleaseEvent(self, event):
        if self.selected_piece is not None:
            # Check if the piece is released on a valid square
            square = event.scenePos()

            print(square.x(), square.y())
            print(self.calculate_position(square.x(), square.y()))

            new_position = QPointF(*self.calculate_position(square.x(), square.y()))

            self.selected_piece.setPos(new_position)


            self.selected_piece = None
            self.initial_position = QPointF()

        super().mouseReleaseEvent(event)

    def calculate_position(self, x, y):
        for square in self.squares:
            if square.rect.x() < x < square.rect.x() + self.square_size  and square.rect.y() < y < square.rect.y() + self.square_size:
                return square.rect.x(), square.rect.y()



def main():
    app = QApplication(sys.argv)
    scene = Chess()
    scene.setBackgroundBrush(QColor(64,64,64))
    view = QGraphicsView(scene)
    view.setSceneRect(0, 0, 720, 720)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
