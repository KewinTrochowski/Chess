from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt6.QtCore import Qt


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

    def clear_text(self):
        self.text = ""
        self.label.setText(self.text)