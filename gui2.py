import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a button
        self.button = QPushButton('Authenticate', self)
        self.button.move(50, 50)
        self.button.clicked.connect(self.run_function)

        # Create a text box to display output
        self.text_box = QTextEdit(self)
        self.text_box.setGeometry(50, 100, 300, 200)

    def run_function(self):
        # Import the script containing my_function
        import main

        # Call my_function and store the output
        output = main.auth()

        # Display the output in the text box
        self.text_box.setText(str(output))


if __name__ == '__main__':
    # Create the application
    app = QApplication(sys.argv)

    # Create the main window
    main_window = MainWindow()
    main_window.setGeometry(100, 100, 400, 400)
    main_window.show()

    # Run the event loop
    sys.exit(app.exec_())
