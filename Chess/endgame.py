from sqlite_db import save_to_database
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

def gameisover(moves):
    moves = [move for move in moves.split() if len(move) == 4]
    db_file = "db/history.db"
    xml_file = "db/history.xml"
    save_moves_to_xml(moves, xml_file)
    save_to_database(moves, db_file)
    if exit_message_box():
        return True



