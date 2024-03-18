import sys
from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                             QGraphicsItem, QGraphicsTextItem)
from PyQt6.QtCore import (QRectF, QTimer, QPointF)
from PyQt6.QtGui import (QPainter, QColor, QFont, QPixmap)


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

class Circle(QGraphicsItem):
    def __init__(self, x, y, size):
        super().__init__()
        self.rect = QRectF(x , y, size, size)
        self.color = QColor(255,0,0,255)

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter, option, widget=None):
        fill_color = self.color
        painter.setBrush(fill_color)
        #center the circle


        painter.drawEllipse(self.rect)

class Pieces(QGraphicsItem):
    def __init__(self, x, y, size, color):
        super().__init__()
        self.color = color
        self.size = size
        self.image_path = self.set_pixmap()  # Set the image path based on color
        self.pixmap = QPixmap(self.image_path)
        self.setPos(x, y)

    def set_pixmap(self):
        pass

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter: QPainter, option, widget=None):
        painter.drawPixmap(0, 0, self.size, self.size, self.pixmap)


class Pawn(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/pawn-{self.color[0]}.svg")


class Rook(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/rook-{self.color[0]}.svg")


class Knight(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/knight-{self.color[0]}.svg")


class Bishop(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/bishop-{self.color[0]}.svg")


class Queen(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/queen-{self.color[0]}.svg")


class King(Pieces):
    def set_pixmap(self):
        return QPixmap(f"pieces/king-{self.color[0]}.svg")


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
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self.update_blink)

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
        if self.selected_piece is not None:
            self.blinkTimer.start(500)

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

            try:
                new_position = QPointF(*self.calculate_position(square.x(), square.y()))
            except:
                new_position = None

            if new_position is not None:
                self.selected_piece.setPos(new_position)
            else:
                self.selected_piece.setPos(self.initial_position)

            self.blinkTimer.stop()
            if self.selected_piece is not None:
                self.selected_piece.setOpacity(1.0)

            self.take()

            if self.selected_piece.pos() == self.initial_position:
                print("Invalid move")
                x = self.initial_position.x()
                y = self.initial_position.y()
                circle_size = 20
                #self.addItem(Circle(x + (self.square_size - circle_size) / 2, y + (self.square_size - circle_size) / 2, 20))

            self.selected_piece = None
            self.initial_position = QPointF()

        super().mouseReleaseEvent(event)

    def calculate_position(self, x, y):
        for square in self.squares:
            if square.rect.x() < x < square.rect.x() + self.square_size and square.rect.y() < y < square.rect.y() + self.square_size:
                return square.rect.x(), square.rect.y()

    def update_blink(self):
        if self.selected_piece is not None:
            opacity = self.selected_piece.opacity() - 0.5  # Reduce opacity
        if opacity <= 0:
            opacity = 1.0  # Reset
        self.selected_piece.setOpacity(opacity)

    def take(self):
        if self.selected_piece is not None:
            all_pieces = self.white_pieces + self.black_pieces
            for piece in all_pieces:
                if piece.scenePos() == self.selected_piece.scenePos() and piece != self.selected_piece:
                    if self.selected_piece.color != piece.color:
                        self.removeItem(piece)
                        try:
                            self.black_pieces.remove(piece)
                        except:
                            self.white_pieces.remove(piece)
                    if self.selected_piece.color == piece.color:
                        self.selected_piece.setPos(self.initial_position)









def main():
    app = QApplication(sys.argv)
    scene = Chess()
    scene.setBackgroundBrush(QColor(64, 64, 64))
    view = QGraphicsView(scene)
    view.setGeometry(300, 30, 710, 710)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
