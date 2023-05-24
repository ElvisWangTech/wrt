import sys

from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QDialogButtonBox, QVBoxLayout, QLabel, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self, s):
        print("click", s)

        # dlg = CustomDialog()
        # button = dlg.exec()
        # if (button):
        #     print("OK!")

        # 内置的QMessageBox组件
        button = QMessageBox.question(self, "Question dialog", "The longer message")
        if button == QMessageBox.StandardButton.Yes:
            print("Yes!")
        else:
            print("No!")

        # Build in QMessageBox dialogs
        '''
        QMessageBox.about(parent, title, message)
        QMessageBox.critical(parent, title, message)
        QMessageBox.information(parent, title, message)
        QMessageBox.question(parent, title, message)
        QMessageBox.warning(parent, title, message)
        '''

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("HELLO!")

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()