import traceback
import sys
from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from message import SN, SN_TYPE


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    '''
    finished = pyqtSignal(SN)
    error = pyqtSignal(SN)
    result = pyqtSignal(SN)
    progress = pyqtSignal(float)


class TranslateWorker(QRunnable):
    '''
    Translate worker thread
    '''

    def __init__(self, fn, *args, **kwargs):
        super(TranslateWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress.emit
        self.kwargs['handle_message'] = self.signals.result.emit

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(SN(text=(exctype, value, traceback.format_exc()), type=SN_TYPE.error))
        finally:
            self.signals.finished.emit(SN(text="finished", type=SN_TYPE.finished))  # Done
