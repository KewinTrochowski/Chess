import sys
from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                             QGraphicsItem, QGraphicsTextItem, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea)
from PyQt6.QtCore import (QRectF, QTimer, QPointF, QObject, pyqtSignal, QThread, Qt)
from PyQt6.QtGui import (QPainter, QColor, QFont, QPixmap)
import threading
import queue

class Logger(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ruchy")
        self.setGeometry(50, 50, 200, 300)

        scroll_area = QScrollArea()
        self.setCentralWidget(scroll_area)

        # Tworzenie etykiety
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.label)

        self.text = ""


    def update_text(self, text):
        self.text = self.text + text + "\n"
        self.label.setText(self.text)

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
    def __init__(self, x, y, size, color):
        super().__init__()
        self.color = color
        self.size = size
        self.image_path = self.set_pixmap()  # Set the image path based on color
        self.pixmap = QPixmap(self.image_path)
        self.setPos(x, y)
        self.moves = self.moves()
        self.number_of_moves = 0

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
        if self.color == "white":
            return [(-1, 0), (-2, 0)]
        else:
            return [(1, 0), (2, 0)]

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


class Chess(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.square_size = 80
        self.w_square = 8
        self.h_square = 8
        self.squares = []
        self.white_pieces = []
        self.black_pieces = []
        self.highlight_color = (255, 30, 0, 255)
        self.which_turn = "white"
        self.selected_piece = None
        self.initial_position = QPointF()
        self.logger = Logger()
        self.initialize_map()
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self.update_blink)

        self.log_queue = queue.Queue()
        self.log_worker = threading.Thread(target=self.process_log_updates)
        self.log_worker.daemon = True
        self.log_worker.start()

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

        self.logger.show()


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

        self.reset_color()

        # Check if any piece is clicked
        for item in items:
            if isinstance(item, Pieces):
                self.selected_piece = item
                self.initial_position = item.pos()
                break

        super().mousePressEvent(event)
        if self.selected_piece is not None:
            x = self.initial_position.x()
            y = self.initial_position.y()
            try:
                self.find_legal_moves(x, y)
            except:
                pass
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

            # print(square.x(), square.y())
            # print(self.calculate_position(square.x(), square.y()))
            try:
                new_position = QPointF(*self.calculate_position(square.x(), square.y()))
            except:
                new_position = None

            if new_position is not None:
                if self.squares[int(new_position.x() / self.square_size + new_position.y() / self.square_size * 8)].is_legal:
                    self.selected_piece.setPos(new_position)
                else:
                    self.selected_piece.setPos(self.initial_position)
            else:
                self.selected_piece.setPos(self.initial_position)

            self.blinkTimer.stop()
            if self.selected_piece is not None:
                self.selected_piece.setOpacity(1.0)

            self.take()

            if self.selected_piece.pos() != self.initial_position:

                self.update_logger()

                self.selected_piece.number_of_moves += 1
                if self.which_turn == "white":
                    self.which_turn = "black"
                else:
                    self.which_turn = "white"
                self.reset_color()

                if self.selected_piece.__class__.__name__ == "Pawn":
                    if self.selected_piece.number_of_moves == 1:
                        self.selected_piece.moves = self.selected_piece.after_first_move()
                    self.pawn_promotion()

                if self.selected_piece.__class__.__name__ == "King":
                    self.castling()




        self.selected_piece = None
        self.initial_position = QPointF()
        super().mouseReleaseEvent(event)

    def find_legal_moves(self, x, y):
        cord_x, cord_y = self.calculate_position(x + 1, y + 1)
        cord_x, cord_y = cord_x / self.square_size, cord_y / self.square_size
        legal_moves = self.calculate_legal_moves((cord_y, cord_x), self.selected_piece)

        for move in legal_moves:
            self.highlight_square(move[1], move[0])  # x, y -> y, x because of the way the board is created

    def highlight_square(self, x, y):
        x = int(x)
        y = int(y)
        self.squares[x + y * 8].old_color = self.squares[x + y * 8].color
        self.squares[x + y * 8].color = self.highlight_color
        self.squares[x + y * 8].is_legal = True
        self.squares[x + y * 8].update()

    def to_chess_notation(self, x, y):
        dic = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        row = int(8 - x)
        col = dic[y]
        return f"{col}{row}"

    def calculate_legal_moves(self, pos, piece):
        # print(f"Legal moves for {self.to_chess_notation(pos[0], pos[1])}")
        legal_moves, final_legal_moves = [], []
        for move in piece.moves:
            x = pos[0] + move[0]
            y = pos[1] + move[1]
            if 0 <= x <= 7 and 0 <= y <= 7:
                # print(self.to_chess_notation(x, y))
                legal_moves.append((x, y))
        if piece.color == self.which_turn:
            final_legal_moves = self.find_farthest_moves(legal_moves, piece)

        return final_legal_moves

    def find_farthest_moves(self, legal_moves, piece):
        directions = [[], [], [], [], [], [], [], []]


        if piece.__class__.__name__ == "Knight":
            directions = legal_moves
        else:
            piece_x, piece_y = piece.pos().x() / self.square_size, piece.pos().y() / self.square_size
            for move in legal_moves:
                y, x = move
                new_x = piece_x - x
                new_y = piece_y - y

                # Check each direction for farthest possible move and first enemy piece encountered
                if new_x == 0:
                    if new_y > 0:
                        for i in range(1, int(new_y) + 1):
                            if (piece_y - i, piece_x) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[0].append((piece_y - i, piece_x))
                            else:
                                directions[0].append((piece_y - i, piece_x))
                                break
                    else:
                        for i in range(1, abs(int(new_y)) + 1):
                            if (piece_y + i, piece_x) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[1].append((piece_y + i, piece_x))
                            else:
                                directions[1].append((piece_y + i, piece_x))
                                break
                elif new_y == 0:
                    if new_x > 0:
                        for i in range(1, int(new_x) + 1):
                            if (piece_y, piece_x - i) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[2].append((piece_y, piece_x - i))
                            else:
                                directions[2].append((piece_y, piece_x - i))
                                break
                    else:
                        for i in range(1, abs(int(new_x)) + 1):
                            if (piece_y, piece_x + i) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[3].append((piece_y, piece_x + i))
                            else:
                                directions[3].append((piece_y, piece_x + i))
                                break
                elif new_x == new_y:
                    if new_x > 0:
                        for i in range(1, int(new_x) + 1):
                            if (piece_y - i, piece_x - i) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[4].append((piece_y - i, piece_x - i))
                            else:
                                directions[4].append((piece_y - i, piece_x - i))
                                break
                    else:
                        for i in range(1, abs(int(new_x)) + 1):
                            if (piece_y + i, piece_x + i) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[5].append((piece_y + i, piece_x + i))
                            else:
                                directions[5].append((piece_y + i, piece_x + i))
                                break
                elif new_x == -new_y:
                    if new_x > 0:
                        for i in range(1, int(new_x) + 1):
                            if (piece_y + i, piece_x - i) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[6].append((piece_y + i, piece_x - i))
                            else:
                                directions[6].append((piece_y + i, piece_x - i))
                                break
                    else:
                        for i in range(1, abs(int(new_x)) + 1):
                            if (piece_y - i, piece_x + i) not in [
                                (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                self.white_pieces + self.black_pieces]:
                                directions[7].append((piece_y - i, piece_x + i))
                            else:
                                directions[7].append((piece_y - i, piece_x + i))
                                break
            for i in range(len(directions)):
                directions[i] = list(set(directions[i]))

            directions = [item for sublist in directions for item in sublist]

        moves = []
        # delete moves on the same color
        for move in directions:
            dlt = False
            for p in self.white_pieces + self.black_pieces:
                if move in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                    if piece.color == p.color:
                        dlt = True
                    if piece.color != p.color and piece.__class__.__name__ == "Pawn":
                        dlt = True
            if not dlt:
                moves.append(move)

        #check if pawn can take

        if piece.__class__.__name__ == "Pawn":
            for move in piece.try_take():
                mx = move[0] + piece.pos().y() / self.square_size
                my = move[1] + piece.pos().x() / self.square_size

                for p in self.white_pieces + self.black_pieces:
                    if (mx,my) in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                        if piece.color != p.color:
                            moves.append((mx,my))

        # check for castling
        if piece.__class__.__name__ == "King":
            moves = self.check_castling(piece,moves)



        return moves

    def check_castling(self,piece,moves):
        if piece.number_of_moves == 0:
            if piece.color == "white":
                # check if 7,5 and 7,6 are empty
                if (7, 5) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                  self.white_pieces + self.black_pieces]:
                    if (7, 6) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p
                                      in self.white_pieces + self.black_pieces]:
                        # check if 7,7 is rook
                        for p in self.white_pieces:
                            if (7, 7) in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                                if p.__class__.__name__ == "Rook":
                                    if p.number_of_moves == 0:
                                        moves.append((7, 6))
                if (7, 3) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                  self.white_pieces + self.black_pieces]:
                    if (7, 2) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p
                                      in self.white_pieces + self.black_pieces]:
                        if (7, 1) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for
                                          p in self.white_pieces + self.black_pieces]:
                            for p in self.white_pieces:
                                if (7, 0) in [
                                    (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                                    if p.__class__.__name__ == "Rook":
                                        if p.number_of_moves == 0:
                                            moves.append((7, 2))
            else:
                # check if 0,5 and 0,6 are empty
                if (0, 5) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                  self.white_pieces + self.black_pieces]:
                    if (0, 6) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p
                                      in self.white_pieces + self.black_pieces]:
                        # check if 0,7 is rook
                        for p in self.black_pieces:
                            if (0, 7) in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                                if p.__class__.__name__ == "Rook":
                                    if p.number_of_moves == 0:
                                        moves.append((0, 6))
                if (0, 3) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                                  self.white_pieces + self.black_pieces]:
                    if (0, 2) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p
                                      in self.white_pieces + self.black_pieces]:
                        if (0, 1) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for
                                          p in self.white_pieces + self.black_pieces]:
                            for p in self.black_pieces:
                                if (0, 0) in [
                                    (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                                    if p.__class__.__name__ == "Rook":
                                        if p.number_of_moves == 0:
                                            moves.append((0, 2))

        return moves

    def castling(self):
        if self.selected_piece.number_of_moves == 1:
            if self.selected_piece.color == "white":
                if (self.selected_piece.pos().x() - self.initial_position.x()) == 2 * self.square_size:
                    for p in self.white_pieces:
                        if p.__class__.__name__ == "Rook" and p.pos().x() == 7 * self.square_size:
                            p.setPos(5 * self.square_size, 7 * self.square_size)
                            p.number_of_moves += 1
                elif self.selected_piece.pos().x() - self.initial_position.x() == -2 * self.square_size:
                    for p in self.white_pieces:
                        if p.__class__.__name__ == "Rook" and p.pos().x() == 0:
                            p.setPos(3 * self.square_size, 7 * self.square_size)
                            p.number_of_moves += 1
            else:
                if (self.selected_piece.pos().x() - self.initial_position.x()) == 2 * self.square_size:
                    for p in self.black_pieces:
                        if p.__class__.__name__ == "Rook" and p.pos().x() == 7 * self.square_size:
                            p.setPos(5 * self.square_size, 0)
                            p.number_of_moves += 1
                elif self.selected_piece.pos().x() - self.initial_position.x() == -2 * self.square_size:
                    for p in self.black_pieces:
                        if p.__class__.__name__ == "Rook" and p.pos().x() == 0:
                            p.setPos(3 * self.square_size, 0)
                            p.number_of_moves += 1

    def reset_color(self):
        for square in self.squares:
            if square.old_color is not None:
                square.color = square.old_color
                square.old_color = None
                square.is_legal = False
                square.update()

    def update_logger(self):
        inix = self.initial_position.x() / self.square_size
        iniy = self.initial_position.y() / self.square_size
        x = self.selected_piece.pos().x() / self.square_size
        y = self.selected_piece.pos().y() / self.square_size
        text = f'{self.to_chess_notation(iniy,inix)}{self.to_chess_notation(y, x)}'
        self.log_queue.put(f"Ruch: {text}")

    def process_log_updates(self):
        while True:
            text = self.log_queue.get()
            self.logger.update_text(text)
            self.log_queue.task_done()

    def pawn_promotion(self):
        if self.selected_piece.color == "white":
            if self.selected_piece.pos().y() == 0:
                new = Queen(self.selected_piece.pos().x(), self.selected_piece.pos().y(), self.square_size,
                            self.selected_piece.color)
                self.removeItem(self.selected_piece)
                self.white_pieces.remove(self.selected_piece)
                self.white_pieces.append(new)
                self.selected_piece = new
                self.addItem(new)
        else:
            if self.selected_piece.pos().y() == 7 * self.square_size:
                new = Queen(self.selected_piece.pos().x(), self.selected_piece.pos().y(), self.square_size,
                            self.selected_piece.color)
                self.removeItem(self.selected_piece)
                self.black_pieces.remove(self.selected_piece)
                self.black_pieces.append(new)
                self.selected_piece = new
                self.addItem(new)

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
