from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea, QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
import sys
from PyQt6.QtWidgets import QApplication

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("Chat Window")
        self.setGeometry(50, 400, 200, 300)

        # Create the central widget and a vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Create a scroll area for displaying messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Create a label that will hold the chat history
        self.chat_label = QLabel()
        self.chat_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_label.setStyleSheet("QLabel { background-color : white; }")

        # Set the chat label as the scroll area's widget
        self.scroll_area.setWidget(self.chat_label)

        # Create a QLineEdit for text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        layout.addWidget(self.text_input)

        # Create a QPushButton for sending messages
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # Set the layout to the central widget
        central_widget.setLayout(layout)

        self.text = ""

    def send_message(self):
        # Retrieve the message from the QLineEdit
        message = self.text_input.text().strip()
        if message:
            # Update the chat history
            self.text +="Chat:" + message + "\n"
            self.chat_label.setText(self.text)
            # Scroll to the bottom each time a message is sent
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
            # Clear the input field
            self.text_input.clear()

    def clear_chat(self):
        self.text = ""
        self.chat_label.setText(self.text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
