from sqlite_db import save_to_database, delete_all_moves
from xml_db import save_moves_to_xml
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox


def exit_message_box():
    msg_box = QMessageBox()
    msg_box.setText("Wciśnij ok jeśli chcesz odtworzyć historię gry.")
    msg_box.setWindowTitle("Koniec gry")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)

    # Poniżej znajduje się obsługa wyboru użytkownika
    button_clicked = msg_box.exec()

    if button_clicked == QMessageBox.StandardButton.Ok:
        return True
    elif button_clicked == QMessageBox.StandardButton.Cancel:
        return False

def gameisover(history, session, flag):
    if not flag:
        history = [move for move in history.split()]
        for move in history:
            if move == "Ruch:" or move == "Szach!":
                history.remove(move)
        moves = []
        timing = []
        for i in range(len(history)):
            if i % 2 == 0:
                moves.append(history[i])
            else:
                timing.append(history[i])

        dir = f"db/{session}"

        db_file = f"{dir}/history.db"
        db_file_timing = f"{dir}/timing.db"
        xml_file = f"{dir}/history.xml"
        delete_all_moves(db_file)
        delete_all_moves(db_file_timing)
        save_moves_to_xml(moves, xml_file)
        save_to_database(moves, db_file)
        save_to_database(timing, db_file_timing)
    if exit_message_box():
        return True
    else:
        sys.exit(0)



