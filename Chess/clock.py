import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, QTimer


class Clock(QWidget):
    def __init__(self, x, y, w, h, min, sec):
        super().__init__()

        self.setWindowTitle("Odliczanie")
        self.setGeometry(x, y, w, h)

        # Ustawienie początkowego czasu
        self.minutes = min
        self.seconds = sec

        # Tworzenie textEdit do wyświetlania czasu
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("color: rgb(51, 102, 33); background-color: rgb(255, 255, 204); font-size: 24px; font-weight: bold; border: 2px solid black;")

        # Ustawienie timera
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Odświeżanie co sekundę
        self.timer.timeout.connect(self.update_time)

        formatted_time = f"{self.minutes:02d}:{self.seconds:02d}"
        self.text_edit.setText(formatted_time)

        # Uruchamianie timera
        #self.timer.start()

    def set_time(self):
        formatted_time = f"{self.minutes:02d}:{self.seconds:02d}"
        self.text_edit.setText(formatted_time)


    def update_time(self):
        """Aktualizuje wyświetlany czas."""
        if self.seconds == 0:
            self.minutes -= 1
            self.seconds = 59
        else:
            self.seconds -= 1

        formatted_time = f"{self.minutes:02d}:{self.seconds:02d}"
        self.text_edit.setText(formatted_time)

        # Zatrzymanie timera po osiągnięciu zera
        if self.minutes == 0 and self.seconds == 0:
            self.timer.stop()


