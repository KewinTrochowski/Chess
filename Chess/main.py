from Chess import Chess
from PyQt6.QtWidgets import QApplication, QGraphicsView
from PyQt6.QtGui import QColor
import sys

def main():
    app = QApplication(sys.argv)
    scene = Chess()
    scene.setBackgroundBrush(QColor(64, 64, 64))
    view = QGraphicsView(scene)
    view.setGeometry(250, 30, 1000, 710)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
