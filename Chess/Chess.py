import sys
import time, os
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QInputDialog
from PyQt6.QtCore import QTimer, QPointF
from PyQt6.QtGui import QFont
import threading
import queue
from pieces import *
from logger import *
from intro import GameDialog
from endgame import gameisover
from move_from_keyboard import MoveKeyboard
from clock import Clock
from json_settings import save_to_json
from sqlite_db import read_from_database
from datetime import datetime
from tcp_client import create_tcp_client, send_message_to_tcp_server
from tcp_server import Server
import subprocess
from chat import ChatWindow

class Chess(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.square_size = 80
        self.w_square = 8
        self.h_square = 8
        self.minutes = 60
        self.squares = []
        self.white_pieces = []
        self.black_pieces = []
        self.highlight_color = (255, 30, 0, 255)
        self.which_turn = "white"
        self.selected_piece = None
        self.seconds = 0
        self.session = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

        os.mkdir(f"db/{self.session}")


        intro = GameDialog()
        intro.exec()
        time = intro.getTime()
        self.game_mode = intro.getButton()
        self.ip = intro.getIP()
        self.port = intro.getPort()
        time = str(time).split(".")
        self.minutes = int(time[0])
        self.seconds = int(int(time[1]) / 10 * 60)

        self.settings = {"minutes": self.minutes, "seconds": self.seconds, "game_mode": self.game_mode
                         , "ip": self.ip, "port": self.port, "session": self.session}
        save_to_json(self.settings, self.session)

        if self.game_mode == 1:
            self.tcp_client = create_tcp_client(self.ip, self.port)
            if self.tcp_client is None:
                self.tcp_server = Server(self.ip, self.port)
                #self.tcp_server_thread = threading.Thread(target=self.tcp_server.start_server)
                #self.tcp_server_thread.start()
                command = f'start cmd.exe /k python tcp_server.py {self.ip} {self.port}'
                subprocess.Popen(command, shell=True)

                self.tcp_client = create_tcp_client(self.ip, self.port)
            self.tcp_client_thread = threading.Thread(target=self.receive_tcp_messages, args=(self.tcp_client,))
            self.tcp_client_thread.start()
        self.tcp_ip_move = None
        self.tcpTimer = QTimer()
        self.tcpTimer.timeout.connect(self.tcp_update)
        self.tcpTimer.start(100)

        self.clock_black = Clock(720, 100, 80, 50,self.minutes, self.seconds)
        self.clock_white = Clock(720, 500, 80, 50,self.minutes, self.seconds)
        self.initial_position = QPointF()
        self.logger = Logger()
        self.move_from_keyboard = MoveKeyboard(self.square_size * 9,300,100,50)

        self.chat_magazine = ""
        self.chat = ChatWindow()
        self.chat_thread = threading.Thread(target=self.process_chat_updates)
        self.chat_thread.start()

        self.initialize_map()
        self.updating = True
        self.history = []
        self.record_board_state()
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self.update_blink)
        self.clockTimer = QTimer()
        self.clockTime_thread = threading.Thread(target=self.monitor_time)
        self.clockTimer.timeout.connect(self.monitor_time)
        self.clockTimer.start(1000)

        self.log_queue = queue.Queue()
        self.log_worker = threading.Thread(target=self.process_log_updates)
        self.log_worker.daemon = True
        self.log_worker.start()

        self.history_moves = []
        self.history_timing = []
        self.auto_play_time = 0
        self.auto_play_wait = 1000000
        self.history_is_playing = False




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
        self.chat.show()
        self.addWidget(self.move_from_keyboard)
        self.addWidget(self.clock_black)
        self.addWidget(self.clock_white)


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

            self.move(new_position)



        if self.check_check(self.which_turn):
            self.undo_move()

        if self.selected_piece is not None and self.selected_piece.pos() != self.initial_position:
            self.update_logger()
        if self.check_check(self.opposite_color(self.which_turn)):
            self.log_queue.put("Szach!")
            if self.check_mate(self.which_turn):
                self.log_queue.put("Szach mat!")
                self.clock_white.timer.stop()
                self.clock_black.timer.stop()
                if gameisover(self.logger.text, self.session, self.history_is_playing):
                    self.reset_game()

        if not self.history_is_playing:
            if self.which_turn == "white":
                self.clock_white.timer.start()
                self.clock_black.timer.stop()
            else:
                self.clock_black.timer.start()
                self.clock_white.timer.stop()

        self.updating = True
        self.selected_piece = None
        self.initial_position = QPointF()
        super().mouseReleaseEvent(event)



    def final_move(self, new_position, piece=None):

        if piece is None or piece.color != self.which_turn:
            return
        self.initial_position = piece.pos()
        self.move(new_position, piece)


        if self.check_check(self.which_turn):
            self.undo_move()

        if self.selected_piece is not None and self.selected_piece.pos() != self.initial_position:
            self.update_logger()
        if self.check_check(self.opposite_color(self.which_turn)):
            self.log_queue.put("Szach!")
            if self.check_mate(self.which_turn):
                self.log_queue.put("Szach mat!")
                if gameisover(self.logger.text, self.session, self.history_is_playing):
                    self.reset_game()

        if not self.history_is_playing:
            if self.which_turn == "white":
                self.clock_white.timer.start()
                self.clock_black.timer.stop()
            else:
                self.clock_black.timer.start()
                self.clock_white.timer.stop()
        self.updating = True
        self.selected_piece = None
        self.initial_position = QPointF()

    def reset_game(self):
        self.clock_black.timer.stop()
        self.clock_white.timer.stop()
        for i in range(len(self.history) + 1):
            self.undo_move()
        self.clock_white.minutes = self.minutes
        self.clock_black.minutes = self.minutes
        self.clock_white.seconds = self.seconds
        self.clock_black.seconds = self.seconds
        self.clock_black.set_time()
        self.clock_white.set_time()
        self.clock_black.timer.stop()
        self.clock_white.timer.stop()
        self.logger.clear_text()
        self.history_moves = read_from_database(f"db/{self.session}/history.db")
        self.history_timing = read_from_database(f"db/{self.session}/timing.db")
        self.auto_play_time = time.time()
        self.history_is_playing = True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            p1, p2 = self.move_from_keyboard.obsluga()
            if p1 is not None and p2 is not None:
                self.move_from_notation(p1, p2)
        if event.key() == Qt.Key.Key_Right:
            if self.history_moves:
                self.play_history(self.history_moves.pop(0), self.history_timing.pop(0))
        if event.key() == Qt.Key.Key_Space:
            self.auto_play_wait = 2 if self.auto_play_wait > 2 else 1000000
        if event.text():
            self.move_from_keyboard.text_edit.insertPlainText(event.text())

    def tcp_update(self):
        if self.tcp_ip_move:
            self.move_from_notation(self.from_chess_notation(self.tcp_ip_move[0:2]), self.from_chess_notation(self.tcp_ip_move[2:4]))
            self.tcp_ip_move = None

    def monitor_time(self):
        if self.history_moves:
            if time.time() - self.auto_play_time >= self.auto_play_wait:
                self.play_history(self.history_moves.pop(0), self.history_timing.pop(0))
                self.auto_play_time = time.time()

        if self.clock_black.minutes == 0 and self.clock_black.seconds == 0:
            self.clock_black.timer.stop()
            self.log_queue.put("Czas minął, wygrywa biały!")
            self.clockTimer.stop()
            if gameisover(self.logger.text, self.session, self.history_is_playing):
                self.reset_game()
        if self.clock_white.minutes == 0 and self.clock_white.seconds == 0:
            self.clock_white.timer.stop()
            self.log_queue.put("Czas minął, wygrywa czarny!")
            self.clockTimer.stop()
            if gameisover(self.logger.text, self.session, self.history_is_playing):
                self.reset_game()

    def receive_tcp_messages(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024)  # Odbierz wiadomość (bufor 1024 bajty)
                if message:
                    move = message.decode()
                    print(f"Received message: {move}")
                    if move[:5] == "Chat:":
                        print("XXXXXXXX")
                        self.chat.text = move
                        self.chat.chat_label.setText(self.chat.text)
                    else:
                        self.tcp_ip_move = move

                else:
                    print("Connection closed by the server.")
                    break
        except ConnectionResetError:
            print("Server closed the connection")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()




    def play_history(self,move,time):
        move = move[1]
        p1 = self.from_chess_notation(move[0:2])
        p2 = self.from_chess_notation(move[2:4])
        self.move_from_notation(p1, p2)
        if self.which_turn == "black":
            self.clock_white.minutes = int(time[1][0])
            self.clock_white.seconds = int(time[1][2:])
            self.clock_white.set_time()
        else:
            self.clock_black.minutes = int(time[1][0])
            self.clock_black.seconds = int(time[1][2:])
            self.clock_black.set_time()


    def move_from_notation(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        self.selected_piece = self.find_piece(x1, y1)
        try:
            new_position = QPointF(y2 * self.square_size, x2 * self.square_size)
        except:
            new_position = None

        if new_position is not None:
            self.final_move(QPointF(y2 * self.square_size, x2 * self.square_size), self.selected_piece)
            self.update()



    def find_piece(self, x, y):
        for piece in self.white_pieces + self.black_pieces:
            if (x,y) == (piece.pos().y() / self.square_size, piece.pos().x() / self.square_size):
                return piece
        return None


    def move(self, new_position, piece=None):
        if piece is None:
            piece = self.selected_piece
            if new_position is not None:
                if self.squares[
                    int(new_position.x() / self.square_size + new_position.y() / self.square_size * 8)].is_legal:
                    piece.setPos(new_position)
                else:
                    piece.setPos(self.initial_position)
            else:
                piece.setPos(self.initial_position)
        else:
            piece.setPos(new_position)

        self.blinkTimer.stop()
        if piece is not None:
            piece.setOpacity(1.0)

        self.take()

        if piece.pos() != self.initial_position:

            piece.number_of_moves += 1
            if self.which_turn == "white":
                self.which_turn = "black"
            else:
                self.which_turn = "white"
            self.reset_color()

            if piece.__class__.__name__ == "Pawn":
                if piece.number_of_moves >= 1:
                    piece.moves = piece.after_first_move()
                self.pawn_promotion()
                self.check_en_passant()

            if piece.__class__.__name__ == "King":
                self.castling()

            self.record_board_state()

    def find_legal_moves(self, x, y):
        cord_x, cord_y = self.calculate_position(x + 1, y + 1)
        cord_x, cord_y = cord_x / self.square_size, cord_y / self.square_size
        legal_moves = self.calculate_legal_moves((cord_y, cord_x), self.selected_piece, self.which_turn)

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

    def from_chess_notation(self, notation):
        dic = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

        if len(notation) != 2:
            return None  # Błędny format notacji

        col = notation[0].lower()  # Np. litera "e"
        row = notation[1]  # Np. cyfra "4"

        if col not in dic or not row.isdigit() or int(row) < 1 or int(row) > 8:
            return None  # Błędny format notacji

        y = dic[col]
        x = 8 - int(row)
        return x, y


    def calculate_legal_moves(self, pos, piece, color):
        # print(f"Legal moves for {self.to_chess_notation(pos[0], pos[1])}")
        legal_moves, final_legal_moves = [], []
        for move in piece.moves:
            x = pos[0] + move[0]
            y = pos[1] + move[1]
            if 0 <= x <= 7 and 0 <= y <= 7:
                # print(self.to_chess_notation(x, y))
                legal_moves.append((x, y))
        if piece.color == color:
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

        # check if pawn can take

        if piece.__class__.__name__ == "Pawn":
            for move in piece.try_take():
                mx = move[0] + piece.pos().y() / self.square_size
                my = move[1] + piece.pos().x() / self.square_size

                for p in self.white_pieces + self.black_pieces:
                    if (mx, my) in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                        if piece.color != p.color:
                            moves.append((mx, my))

            # en passant
            if piece.color == "white":
                if piece.pos().y() == 3 * self.square_size:
                    for p in self.black_pieces:
                        if p.__class__.__name__ == "Pawn":
                            if p.number_of_moves == 1 and p.pos().y() == piece.pos().y():
                                if p.pos().x() - piece.pos().x() == self.square_size:
                                    moves.append((2, p.pos().x() / self.square_size))
                                elif piece.pos().x() - p.pos().x() == self.square_size:
                                    moves.append((2, p.pos().x() / self.square_size))
            else:
                if piece.pos().y() == 4 * self.square_size:
                    for p in self.white_pieces:
                        if p.__class__.__name__ == "Pawn":
                            if p.number_of_moves == 1 and p.pos().y() == piece.pos().y():
                                if p.pos().x() - piece.pos().x() == self.square_size:
                                    moves.append((5, p.pos().x() / self.square_size))
                                elif piece.pos().x() - p.pos().x() == self.square_size:
                                    moves.append((5, p.pos().x() / self.square_size))

        # check for castling
        if piece.__class__.__name__ == "King":
            moves = self.check_castling(piece, moves)

        return moves

    def check_mate(self, color):
        attacking_piece = None
        if color == "white":
            attacking_pieces = self.black_pieces
            deffending_pieces = self.white_pieces
        else:
            attacking_pieces = self.white_pieces
            deffending_pieces = self.black_pieces
        for piece in attacking_pieces:
            if self.can_capture_king(piece):
                attacking_piece = piece
                break

        for piece in deffending_pieces:
            if piece.__class__.__name__ == "King":
                king = piece
                break


        if self.try_escape(king,attacking_piece, attacking_pieces):
            return False

        if self.try_take_attacker(deffending_pieces, attacking_piece):
            return False

        if self.try_block(king, attacking_piece, deffending_pieces):
            return False



        return True

    def try_escape(self, king, attacking_piece, attacking_pieces):
        old_pos = king.pos()
        moves = self.calculate_legal_moves((king.pos().y() / self.square_size, king.pos().x() / self.square_size), king, king.color)
        for move in moves:
            buf = True
            king.setPos(move[1] * self.square_size, move[0] * self.square_size)
            if not self.check_check(self.opposite_color(king.color)):
                if king.pos() == attacking_piece.pos():
                    attacking_pieces.remove(attacking_piece)
                    for p in attacking_pieces:
                        if p != attacking_piece:
                            moves = self.calculate_legal_moves((p.pos().y() / self.square_size, p.pos().x() / self.square_size), p, p.color)
                            for m in moves:
                                if m == (king.pos().y() / self.square_size, king.pos().x() / self.square_size):
                                    buf = False
                    attacking_pieces.append(attacking_piece)

                king.setPos(old_pos)
                king.update()
                if buf:
                    return True
            king.setPos(old_pos)
            king.update()
        return False

    def try_block(self, king, attacking_piece, deffending_pieces):
        if attacking_piece.__class__.__name__ != "Knight" and attacking_piece.__class__.__name__ != "Pawn":
            squares = self.find_squares_between(king, attacking_piece)
            for p in deffending_pieces:
                if p.__class__.__name__ != "King":
                    moves = self.calculate_legal_moves((p.pos().y() / self.square_size, p.pos().x() / self.square_size), p, p.color)
                    for move in moves:
                        if move in squares:
                            if not self.binding(p, move):
                                return True


    def binding(self, piece, move, attacking_piece=None):
        buf = False
        old_pos = piece.pos()
        new_pos = QPointF(move[1] * self.square_size, move[0] * self.square_size)
        piece.setPos(new_pos)
        if attacking_piece is not None:
            attacking_pieces = self.white_pieces if attacking_piece.color == "white" else self.black_pieces
            if attacking_piece.pos() == piece.pos():
                attacking_pieces.remove(attacking_piece)
                buf = True
        if self.check_check(self.opposite_color(piece.color)):
            piece.setPos(old_pos)
            piece.update()
            if buf:
                attacking_pieces.append(attacking_piece)
            return True
        piece.setPos(old_pos)
        piece.update()
        if buf:
            attacking_pieces.append(attacking_piece)
        return False

    def find_squares_between(self, king, attacking_piece):
        x = attacking_piece.pos().x() / self.square_size - king.pos().x() / self.square_size
        y = attacking_piece.pos().y() / self.square_size - king.pos().y() / self.square_size
        if x > 0:
            dx = 1
        elif x < 0:
            dx = -1
        else:
            dx = 0
        if y > 0:
            dy = 1
        elif y < 0:
            dy = -1
        else:
            dy = 0
        squares = []
        nr = abs(x) if abs(x) > abs(y) else abs(y)
        nr = int(nr)
        for i in range(1, nr):
            squares.append((king.pos().y() / self.square_size + i * dy, king.pos().x() / self.square_size + i * dx))
        return squares


    def try_take_attacker(self, defending_pieces, attacker):
        for piece in defending_pieces:
            if piece.__class__.__name__ != "King":
                moves = self.calculate_legal_moves((piece.pos().y() / self.square_size, piece.pos().x() / self.square_size), piece, piece.color)
                for move in moves:
                    if move in [(attacker.pos().y() / self.square_size, attacker.pos().x() / self.square_size)]:
                        if not self.binding(piece, move, attacker):
                            return True

        return False


    def check_check(self, color):
        pieces = self.white_pieces if color == "white" else self.black_pieces

        for piece in pieces:
            if self.can_capture_king(piece):
                self.updating = False
                return True
        return False

    def can_capture_king(self, piece):
        moves = self.calculate_legal_moves((piece.pos().y() / self.square_size, piece.pos().x() / self.square_size),
                                                 piece, piece.color)

        for move in moves:
            for p in self.white_pieces + self.black_pieces:
                if move in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                    if p.__class__.__name__ == "King":
                        return True

    def check_white_castling(self, moves,piece):
        # check if 7,5 and 7,6 are empty
        if (7, 5) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p in
                          self.white_pieces + self.black_pieces]:
            if (7, 6) not in [(p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size) for p
                              in self.white_pieces + self.black_pieces]:
                    # check if 7,7 is rook
                    for p in self.white_pieces:
                        if (7, 7) in [
                            (p.scenePos().y() / self.square_size, p.scenePos().x() / self.square_size)]:
                            if p.__class__.__name__ == "Rook":
                                if p.number_of_moves == 0:
                                    if not self.is_blocking_castling(piece,p):
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
                                        if not self.is_blocking_castling(piece, p):
                                            moves.append((7, 2))

    def check_black_castling(self, moves,piece):
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
                                    if not self.is_blocking_castling(piece, p):
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
                                        if not self.is_blocking_castling(piece, p):
                                            moves.append((0, 2))

    def is_blocking_castling(self, king, rook):
        squares = self.find_squares_between(king, rook)
        squares.append((king.pos().y() / self.square_size, king.pos().x() / self.square_size))
        pieces = self.white_pieces if king.color == "black" else self.black_pieces
        for square in squares:
            for p in pieces:
                if p.__class__.__name__ != "King":
                    moves = self.calculate_legal_moves((p.pos().y() / self.square_size, p.pos().x() / self.square_size), p, p.color)
                    if square in moves:
                        return True
        return False

    def check_castling(self, piece, moves):
        if piece.number_of_moves == 0:
            if piece.color == "white":
                self.check_white_castling(moves,piece)
            else:
                self.check_black_castling(moves,piece)
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

    def check_en_passant(self):
        if self.selected_piece.color == "white":
            if self.selected_piece.pos().y() == 2 * self.square_size:
                if abs(self.selected_piece.pos().x() - self.initial_position.x()) == self.square_size:
                    for p in self.black_pieces:
                        if p.__class__.__name__ == "Pawn" and p.number_of_moves == 1:
                            if p.pos().x() == self.selected_piece.pos().x() and p.pos().y() == self.selected_piece.pos().y() + self.square_size:
                                self.removeItem(p)
                                self.black_pieces.remove(p)
        else:
            if self.selected_piece.pos().y() == 5 * self.square_size:
                if abs(self.selected_piece.pos().x() - self.initial_position.x()) == self.square_size:
                    for p in self.white_pieces:
                        if p.__class__.__name__ == "Pawn" and p.number_of_moves == 1:
                            if p.pos().x() == self.selected_piece.pos().x() and p.pos().y() == self.selected_piece.pos().y() - self.square_size:
                                self.removeItem(p)
                                self.white_pieces.remove(p)

    def reset_color(self):
        for square in self.squares:
            if square.old_color is not None:
                square.color = square.old_color
                square.old_color = None
                square.is_legal = False
                square.update()

    def update_logger(self, buf=True):
        if self.updating:
            inix = self.initial_position.x() / self.square_size
            iniy = self.initial_position.y() / self.square_size
            x = self.selected_piece.pos().x() / self.square_size
            y = self.selected_piece.pos().y() / self.square_size
            time = f"{self.clock_white.minutes}:{self.clock_white.seconds}" if self.which_turn == "black" else f"{self.clock_black.minutes}:{self.clock_black.seconds}"
            text = f'{self.to_chess_notation(iniy, inix)}{self.to_chess_notation(y, x)} {time}'
            self.log_queue.put(f"Ruch: {text}")
            if self.game_mode == 1 and buf:
                send_message_to_tcp_server(self.tcp_client, text[0:4])

    def process_log_updates(self):
        while True:
            text = self.log_queue.get()
            self.logger.update_text(text)
            self.log_queue.task_done()

    def process_chat_updates(self):
        while True:
            if self.chat.text != self.chat_magazine:
                self.tcp_client.send(self.chat.text.encode())
                self.chat_magazine = self.chat.text
            time.sleep(1)



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

    def record_board_state(self):
        # Record the state of the board after the move
        white_pieces_state = [(piece.__class__.__name__, piece.pos().x(), piece.pos().y(), piece.number_of_moves) for
                              piece in
                              self.white_pieces]
        black_pieces_state = [(piece.__class__.__name__, piece.pos().x(), piece.pos().y(), piece.number_of_moves) for
                              piece in
                              self.black_pieces]
        turn = self.which_turn
        # Save the state to the history list
        self.history.append((white_pieces_state, black_pieces_state, turn))

    def undo_move(self):
        if len(self.history) > 1:  # Ensure there's at least one move recorded
            # Remove the current board state
            self.history.pop()

            # Retrieve the previous board state
            prev_state = self.history[-1]
            white_pieces_state, black_pieces_state, turn = prev_state
            # Restore the board state
            self.restore_board_state(white_pieces_state, black_pieces_state, turn)

    def restore_board_state(self, white_pieces_state, black_pieces_state, turn):
        # Remove all existing pieces from the scene
        for piece in self.white_pieces + self.black_pieces:
            self.removeItem(piece)

        # Restore white pieces
        self.white_pieces = []
        for piece_info in white_pieces_state:
            piece_class_name, x, y, nr = piece_info
            piece_class = globals()[piece_class_name]
            new_piece = piece_class(x, y, self.square_size, "white", nr)
            self.white_pieces.append(new_piece)
            self.addItem(new_piece)

        # Restore black pieces
        self.black_pieces = []
        for piece_info in black_pieces_state:
            piece_class_name, x, y, nr = piece_info
            piece_class = globals()[piece_class_name]
            new_piece = piece_class(x, y, self.square_size, "black", nr)
            self.black_pieces.append(new_piece)
            self.addItem(new_piece)

        # Set the turn
        self.which_turn = turn

    def opposite_color(self, color):
        return "black" if color == "white" else "white"


