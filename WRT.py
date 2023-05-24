import sys
import os
from threading import Thread
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QPlainTextEdit, QMenu, QFileDialog, QLabel, QPushButton, QMessageBox, QStatusBar
from PyQt6.QtCore import QDir
from PyQt6.QtGui import QAction, QIcon

from util import getFileSizeDesc
from translator import translate
from message import SN, SN_TYPE

class WRT():

    '''
    WRT is a realtime translator using whisper.
    '''
    def __init__(self):
        
        self.app = QApplication(sys.argv)
        self.window = uic.loadUi("WRT.ui")
        
        self.initWidges()
        self.bindWidgetSignals()

        self.window.show()
        self.app.exec()

    def initWidges(self):
        self.filePathLabel: QLabel = self.window.findChild(QtWidgets.QLabel, "filePath")
        self.plainTextEdit: QPlainTextEdit = self.window.findChild(QtWidgets.QPlainTextEdit, 'plainTextEdit')
        self.startButton: QPushButton = self.window.findChild(QtWidgets.QPushButton, 'startButton')
        self.statusBar: QStatusBar = self.window.findChild(QtWidgets.QStatusBar, 'statusbar')

    def bindWidgetSignals(self):
        # 选择文件按钮
        chooseMenu: QMenu = self.window.findChild(QtWidgets.QMenu, "chooseMenu")
        chooseAction = QAction(QIcon("icons/disc--plus.png"), "打开", self.window)
        chooseAction.setStatusTip("打开视频/音频文件")
        chooseAction.triggered.connect(self.getFile)
        chooseMenu.addAction(chooseAction)

        exportAction = QAction(QIcon("icons/disk.png"), "保存", self.window)
        exportAction.setStatusTip("导出到txt文本")
        exportAction.triggered.connect(self.exportTxt)
        chooseMenu.addAction(exportAction)

        # 帮助按钮
        helpMenu: QMenu = self.window.findChild(QtWidgets.QMenu, "helpMenu")
        aboutAction = QAction(QIcon("icons/info.png"), "关于", self.window)
        aboutAction.triggered.connect(self.showAboutDialg)
        helpMenu.addAction(aboutAction)

        # 开始按钮
        self.startButton.clicked.connect(self.startTranslateThread)

    def getFile(self):
        print("get file...")

        fileName = QFileDialog.getOpenFileName(self.window, "选择文件", os.path.expanduser('~'), "*.mp4 *.mp3 *.aac *.wav *.flv")

        if (fileName[0]):
            print("select file", fileName[0])
            self.filePathLabel.setText('当前文件：' + fileName[0] + '' * 20 + '大小：' + getFileSizeDesc(fileName[0]))
            self.filePath = fileName[0]

    def exportTxt(self):
        print("export txt file...")


    def showAboutDialg(self):
        print("show about...")

    def startTranslateThread(self):
        self.translateThread = Thread(target=translate, args=(self.filePath, self.handleMessage))
        self.translateThread.start()

    def handleMessage(self, message: SN):
        print(message)
        match message.type:
            case SN_TYPE.dataGenerated:
                self.plainTextEdit.appendPlainText(message.text)
            case SN_TYPE.error:
                QMessageBox.warning(self.window, "出现错误", message.text)
            case SN_TYPE.keyInfo:
                self.statusBar.showMessage(message.text)
            case SN_TYPE.processing:
                # TODO processBar
                pass
            case SN_TYPE.finished:
                self.statusBar.showMessage(message.text)

if __name__ == '__main__':
    WRT()