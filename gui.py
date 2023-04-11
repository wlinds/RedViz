from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QTextEdit

from subprocess import Popen, PIPE
import sys

version_no = '0.0.1'

class RedViz(QWidget):
    def __init__(self):
        super().__init__()

        # Create a button
        self.button = QPushButton('Run my_function', self)
        self.button.move(50, 50)
        self.button.clicked.connect(self.run_function)

        # Create a text box to display output
        self.text_box = QTextEdit(self)
        self.text_box.setGeometry(50, 100, 300, 200)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'ReDviz {version_no}')
        self.setGeometry(100, 100, 500, 500)
        label = QLabel('RedViz alpha 0.0.1', self)
        label.move(50, 50)
        self.show()

        process = Popen([sys.executable, 'main.py'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RedViz()
    sys.exit(app.exec_())
