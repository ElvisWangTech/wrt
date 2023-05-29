import sys
import os
from queue import Queue
from warnings import warn
from threading import Thread
from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QMenu, \
    QFileDialog, QLabel, QPushButton, QMessageBox, QStatusBar, QProgressBar
from PyQt6.QtCore import QThreadPool, QTimer
from PyQt6.QtGui import QAction, QIcon

from util import getFileSizeDesc, getFileName
from translator import preloadAudio, translate
from message import SN, SN_TYPE
from workers import TranslateWorker


class WRT():

    '''
    WRT is a realtime translator using whisper.
    '''
    def __init__(self):
        self.app: QApplication = QApplication(sys.argv)
        self.window: QMainWindow = uic.loadUi("WRT.ui")
        self.initWidges()
        self.bindWidgetSignals()
        self.working = False

        self.threadpool = QThreadPool()
        self.messageQue = Queue()
        self.initTimer()
        # preloadModel()
        self.window.show()
        self.app.exec()

    def initTimer(self):
        self.timer = QTimer(self.window)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.pollMessage)
        self.timer.start()

    def initWidges(self):
        self.filePathLabel: QLabel = self.window.findChild(QtWidgets.QLabel, "filePath")
        self.fileSizeLabel: QLabel = self.window.findChild(QtWidgets.QLabel, "fileSize")
        self.plainTextEdit: QPlainTextEdit = self.window.findChild(QtWidgets.QPlainTextEdit, 'plainTextEdit')
        self.startButton: QPushButton = self.window.findChild(QtWidgets.QPushButton, 'startButton')
        self.statusBar: QStatusBar = self.window.findChild(QtWidgets.QStatusBar, 'statusbar')
        self.progressBar: QProgressBar = self.window.findChild(QtWidgets.QProgressBar, 'progressBar')

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
        # self.startButton.clicked.connect(self.startTranslateThread)
        self.startButton.pressed.connect(self.startTranslateWorker)
        self.startButton.setDisabled(True)

        # 进度条默认隐藏
        self.progressBar.setVisible(False)

    def getFile(self):
        print("get file...")
        fileName = QFileDialog.getOpenFileName(
            self.window, "选择文件", os.path.expanduser('~'),
            "*.mp4 *.mp3 *.aac *.wav *.flv")

        if (fileName[0]):
            print("select file", fileName[0])
            self.filePathLabel.setText(fileName[0])
            self.fileSizeLabel.setText(getFileSizeDesc(fileName[0]))
            self.filePath = fileName[0]
            self.startButton.setDisabled(False)
            self.progressBar.setVisible(True)
            self.statusBar.showMessage("开始预加载资源")
            preloadAudio(self.filePath)
            self.statusBar.showMessage("资源准备完毕")

    def exportTxt(self):
        print("export txt file...")
        if self.working:
            QMessageBox.information(self.window, "提示", "还在转录呢~")
            return
        if self.filePath is None:
            QMessageBox.information(self.window, "提示", "没有任何文件要导出！")
            return
        saveFilePath = os.path.dirname(self.filePath) + '/' + getFileName(self.filePath) + '.txt'
        file = open(saveFilePath, 'w')
        text = self.plainTextEdit.toPlainText()
        file.write(text)
        file.close()
        QMessageBox.information(self.window, "提升", "保存成功！\n {}".format(saveFilePath))

    def showAboutDialg(self):
        print("show about...")

    def startTranslateWorker(self):
        worker = TranslateWorker(translate, self.filePath)
        worker.signals.result.connect(self.putMessage)
        worker.signals.finished.connect(self.putMessage)
        # worker.signals.progress.connect(self.handleProgress) # progress直接存在消息里

        # 禁用开始按钮，防止重复触发
        self.startButton.setText("转录中..")
        self.startButton.setDisabled(True)
        self.progressBar.setValue(0)
        self.plainTextEdit.setPlainText("")
        # Execute
        self.threadpool.start(worker)
        self.working = True
        # 启动定时器处理消息
        self.messageQue.empty()

    def startTranslateThread(self):
        warn("This is deprecated; version=1.0.0", DeprecationWarning)
        self.translateThread = Thread(target=translate, args=(self.filePath, self.putMessage, self.handleProgress,))
        self.translateThread.start()

    def pollMessage(self):
        # print("get message in queue")
        if self.messageQue.empty():
            return
        msg: SN = self.messageQue.get(block=False)
        if (msg is not None):
            self.handleMessage(msg)

    def putMessage(self, message: SN):
        print("put message in queue", message)
        self.messageQue.put(message)

    def handleMessage(self, message: SN):
        print("handle message", message)
        match message.type:
            case SN_TYPE.dataGenerated:
                self.plainTextEdit.appendPlainText(message.text)
                if (message.progress):
                    self.handleProgress(message.progress)
            case SN_TYPE.error:
                QMessageBox.warning(self.window, "出现错误", message.text)
            case SN_TYPE.keyInfo:
                self.statusBar.showMessage(message.text)
            case SN_TYPE.processing:
                # TODO processBar
                pass
            case SN_TYPE.finished:
                self.statusBar.showMessage(message.text)
                self.progressBar.setValue(100)
                self.startButton.setDisabled(False)
                self.startButton.setText("开始")
                self.working = False

    def handleProgress(self, progress):
        print("progress: ", progress)
        self.progressBar.setValue(int(progress * 100))


if __name__ == '__main__':
    WRT()
