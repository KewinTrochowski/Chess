import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, QTimer


class Clock(QWidget):
    def __init__(self, x, y, w, h):
        super().__init__()

        self.setWindowTitle("Odliczanie")
        self.setGeometry(x, y, w, h)

        # Ustawienie początkowego czasu
        self.minutes = 60
        self.seconds = 0

        # Tworzenie textEdit do wyświetlania czasu
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Ustawienie timera
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Odświeżanie co sekundę
        self.timer.timeout.connect(self.update_time)

        # Uruchamianie timera
        #self.timer.start()

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

    def reset_timer(self):
        """Resetowanie timera do 60 minut."""
        self.minutes = 60
        self.seconds = 0
        self.update_time()

