from PyQt6.QtWidgets import QApplication, QInputDialog, QDialog, QRadioButton, QVBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt6.QtGui import QDoubleValidator, QIntValidator
import sys

class GameDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ustawienia")
        layout = QVBoxLayout()

        # Dodaj przyciski typu radio
        self.radio_buttons = []
        self.radio_button_labels = ["1 gracz", "2 graczy", "Gracz vs AI"]
        for label in self.radio_button_labels:
            radio_button = QRadioButton(label)
            self.radio_buttons.append(radio_button)
            layout.addWidget(radio_button)

        self.radio_buttons[0].setChecked(True)

        # Dodaj pole tekstowe do wprowadzania czasu
        self.time_input = QLineEdit()
        self.time_label = QLabel("Czas gry (w minutach):")
        start_time = 5
        self.time_input.setText(str(start_time))
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_input)

        # Ustaw validator dla pola tekstowego, aby akceptował tylko liczby float
        validator = QDoubleValidator()
        validator.setDecimals(2)  # Ustaw ilość miejsc po przecinku na 2
        self.time_input.setValidator(validator)

        # Dodaj pole tekstowe dla adresu IP
        self.ip_input = QLineEdit()
        self.ip_label = QLabel("Adres IP:")
        self.ip_input.setText("127.0.0.1")
        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)

        # Dodaj pole tekstowe dla portu
        self.port_input = QLineEdit()
        self.port_label = QLabel("Port:")
        self.port_input.setText("55555")
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)

        # Ustaw validator dla pola tekstowego portu, aby akceptował tylko liczby całkowite z zakresu 1-65535
        port_validator = QIntValidator(1, 65535)
        self.port_input.setValidator(port_validator)

        # Dodaj przyciski OK i Anuluj
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(sys.exit)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def getButton(self):
        for index, radio_button in enumerate(self.radio_buttons):
            if radio_button.isChecked():
                return index
        return None

    def getTime(self):
        time_text = self.time_input.text()
        time_text = time_text.replace(",", ".")
        if time_text:
            return float(time_text)
        return None

    def getIP(self):
        ip_text = self.ip_input.text()
        if ip_text:
            return ip_text
        return None

    def getPort(self):
        port_text = self.port_input.text()
        if port_text:
            return int(port_text)
        return None

'''app = QApplication([])
dialog = GameDialog()
dialog.exec()
selected_button = dialog.getButton()
selected_time = dialog.getTime()

if selected_button is not None:
    print("Wybrana liczba graczy:", selected_button + 1)
if selected_time is not None:
    print("Wybrany czas gry:", selected_time)'''
