import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
import PyQt6.QtCore as QtCore

class MoveKeyboard(QWidget):
    def __init__(self,x,y,w,h):
        super().__init__()

        self.setWindowTitle('Prosty Edytor Tekstu')
        self.setGeometry(x, y, w, h)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Wprowadź ruch")


    def obsluga(self):
        tekst = self.text_edit.toPlainText()
        print("Wprowadzony tekst:", tekst)  # Przykład przetwarzania
        p1 = self.from_chess_notation(tekst[0:2])
        p2 = self.from_chess_notation(tekst[2:4])

        self.text_edit.clear()
        return p1,p2

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
