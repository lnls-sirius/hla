"""GUI for injection."""
from CustomExceptions import PVConnectionError
from InjectionController import InjectionController
from pydm.PyQt.QtCore import pyqtSlot, QTimer
from pydm.PyQt.QtGui import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QRadioButton, QPushButton, QSpinBox, QGridLayout, QMessageBox, QDialog, \
    QLabel, qApp
from pydm.widgets.led import PyDMLed
import pyqtgraph as pg


# class StartInjectionWorker(QObject):
#     """Start injection. Run in QThread."""
#
#     finished = pyqtSignal()
#     error = pyqtSignal(str)
#
#     def __init__(self, controller):
#         """Call super and set controller member."""
#         super(StartInjectionWorker, self).__init__()
#         self.controller = controller
#
#     @pyqtSlot()
#     def run(self):
#         """Set configurations and start injection."""
#         time.sleep(0.1)
#         try:
#             self.controller.put_bucket_list()
#             self.controller.put_injection_mode()
#             self.controller.put_cycles()
#             self.controller.start_injection()
#         except PVConnectionError as e:
#             self.error.emit("{}".format(e))
#             # print("error: leaving")
#         else:
#             self.finished.emit()
#             # print("finished: leaving")
#
#
# class StopInjectionWorker(QObject):
#     """Stop injection. Run in QThread."""
#
#     finished = pyqtSignal()
#     error = pyqtSignal(str)
#
#     def __init__(self, controller):
#         """Call super and set controller member."""
#         super(StopInjectionWorker, self).__init__()
#         self.controller = controller
#
#     @pyqtSlot()
#     def run(self):
#         """Set configurations and start injection."""
#         time.sleep(0.1)
#         try:
#             self.controller.stop_injection()
#         except PVConnectionError as e:
#             self.error.emit("{}".format(e))
#         else:
#             self.finished.emit()


class WaitingDlg(QDialog):
    """Window that shows message to user."""

    StyleSheet = """
        * {
            font: 23px;
        }
    """

    def __init__(self, title, message, parent=None):
        """Class constructor."""
        super(WaitingDlg, self).__init__(parent)
        self.title = title
        self.message = message
        self.may_close = True
        self._setupUi()
        self.setStyleSheet(self.StyleSheet)

    def _setupUi(self):
        self.layout = QVBoxLayout()

        self.main_label = QLabel(self.message, self)

        # self.cancel = QPushButton("Cancel")
        # self.cancel.clicked.connect(self.reject)

        self.layout.addWidget(self.main_label)
        # self.layout.addWidget(self.cancel)

        self.setLayout(self.layout)
        self.setWindowTitle(self.title)

    @pyqtSlot(int)
    def done(self, r):
        """Override done method."""
        self.may_close = True
        super(WaitingDlg, self).done(r)

    # @pyqtSlot()
    # def finished(self):
    #     """Slot that closes window."""
    #     self.may_close = True
    #     self.close()

    def closeEvent(self, event):
        """Override closeEvent."""
        if self.may_close:
            super(WaitingDlg, self).closeEvent(event)
        else:
            event.ignore()


class InjectionWindow(QMainWindow):
    """Window to set injection parameters and control the injection."""

    StyleSheet = """
        * {
            font-size: 23px;
        }
        #startInjectionBtn {
            background-color: #478547;
        }
        #stopInjectionBtn {
            background-color: #a88a8a;
        }
        #ledLabel {
            padding: 0;
        }
        """

    def __init__(self, controller, parent=None):
        """Init window."""
        super(InjectionWindow, self).__init__(parent)
        self.controller = controller

        # self._dialog = None
        # self._worker = None
        # self._thread = QThread()

        self._setupUi()
        self.setStyleSheet(self.StyleSheet)

        self.multiBunchRadio.clicked.connect(
            lambda: self.setInjectionMode(self.controller.MultiBunch))
        self.singleBunchRadio.clicked.connect(
            lambda: self.setInjectionMode(self.controller.SingleBunch))
        self.singleBunchRadio.setEnabled(False)
        self.startInjectionBtn.clicked.connect(self.startInjection)
        self.stopInjectionBtn.clicked.connect(self.stopInjection)
        self.initialBucketSpinBox.valueChanged.connect(self.setInitialBucket)
        self.finalBucketSpinBox.valueChanged.connect(self.setFinalBucket)
        self.stepSpinBox.valueChanged.connect(self.setStep)
        self.cycleSpinBox.valueChanged.connect(self.setCycle)
        self.cycleSpinBox.setEnabled(False)
        self._enableButtons(False)
        self.injectingLed.connected_signal.connect(
            lambda: self._enableButtons(True))
        self.injectingLed.disconnected_signal.connect(
            lambda: self._enableButtons(False))

        # bl = self.controller.bucket_list

        self.multiBunchRadio.setChecked(True)
        self.setInjectionMode(self.controller.MultiBunch)

        self.initialBucketSpinBox.setRange(1, InjectionController.Harmonic)
        self.initialBucketSpinBox.setValue(1)
        self.finalBucketSpinBox.setRange(1, InjectionController.Harmonic)
        self.finalBucketSpinBox.setValue(InjectionController.Harmonic)
        self.stepSpinBox.setRange(1, 200)
        self.stepSpinBox.setValue(75)
        self.cycleSpinBox.setRange(1, 20)
        self.cycleSpinBox.setValue(1)

        self.show()

    # Public
    @pyqtSlot()
    def startInjection(self):
        """Start injection."""
        if self.controller.injecting:
            self._showMsgBox(
                "[InjectionControlWindow]", "Injection is already running")
            return

        msg = ("Injection will run "
               "for {} cycles.").format(self.cycleSpinBox.value())

        res = self._showQuestionBox("Start Injection?", msg + "\nProceed?")
        if res in (QMessageBox.Yes, QMessageBox.Accepted):
            # self._startInjection()
            QTimer.singleShot(100, self._startInjection)
            self._showWaitingDlg(
                "[InjectionControlWindow]", "Setting bucket list...")

        # self._dialog = None

    @pyqtSlot()
    def stopInjection(self):
        """Stop injection."""
        if not self.controller.injecting:
            self._showMsgBox(
                "[InjectionControlWindow]", "Injection isn't running")
            return

        res = self._showQuestionBox(
            "[InjectionControlWindow]", "Stop injection?")
        if res in (QMessageBox.Yes, QMessageBox.Accepted):
            QTimer.singleShot(100, self._stopInjection)
            self._showWaitingDlg(
                "[InjectionControlWindow]", "Stopping injection...")

        # self._dialog = None

    @pyqtSlot(int)
    def setInitialBucket(self, value):
        """Set controller initial bucket and update bucket profile."""
        self.controller.initial_bucket = value
        self._setBucketProfile()

    @pyqtSlot(int)
    def setFinalBucket(self, value):
        """Set controller final graph and update bucket profile."""
        self.controller.final_bucket = value
        self._setBucketProfile()

    @pyqtSlot(int)
    def setStep(self, value):
        """Set controller step and update bucket profile."""
        self.controller.step = value
        self._setBucketProfile()

    @pyqtSlot(int)
    def setCycle(self, value):
        """Set controller cycles."""
        self.controller.cycles = value

    def setInjectionMode(self, value):
        """Set controller injection mode."""
        self.controller.mode = value

    # Private
    def _startInjection(self):
        # # Set worker to start injection
        # self._worker = StartInjectionWorker(self.controller)
        # self._worker.moveToThread(self._thread)
        # # Connect signal to handle error and close thread and waiting dlg
        # self._worker.error.connect(self._showErrorMsg)
        # self._worker.error.connect(self._thread.quit)
        # self._worker.finished.connect(self._showStartedMsg)
        # self._worker.finished.connect(self._thread.quit)
        # # Start thread
        # self._thread.started.connect(lambda: self._enableButtons(False))
        # self._thread.finished.connect(lambda: self._enableButtons(True))
        # self._thread.started.connect(self._worker.run)
        # self._thread.setTerminationEnabled(True)
        # self._thread.start()
        # # Show message

        try:
            self.controller.put_bucket_list()

            # self._dialog.main_label.setText("Setting injection mode")
            # qApp.processEvents()
            #
            # self.controller.put_injection_mode()

            # self._dialog.main_label.setText("Setting number of cycles")
            # qApp.processEvents()
            #
            # self.controller.put_cycles()

            self._dialog.main_label.setText("Starting injection")
            qApp.processEvents()

            self.controller.start_injection()
        except PVConnectionError as e:
            self._dialog.reject()
            self._showErrorMsg("{}".format(e))
        else:
            self._dialog.accept()

    def _stopInjection(self):
        # # Set worker to start injection
        # self._worker = StopInjectionWorker(self.controller)
        # self._worker.moveToThread(self._thread)
        # # Connect signal to handle error and close thread and waiting dlg
        # self._worker.error.connect(self._showErrorMsg)
        # self._worker.finished.connect(self._thread.quit)
        # self._worker.finished.connect(self._showStoppedMsg)
        # # Start thread
        # self._thread.started.connect(self._worker.run)
        # self._thread.start()
        # Show message
        # self._showWaitingDlg(
        #     "[InjectionControlWindow]", "Stopping injection...")

        try:
            self.controller.stop_injection()
        except PVConnectionError as e:
            self._dialog.reject()
            self._showErrorMsg("{}".format(e))
        else:
            self._dialog.accept()

    def _showMsgBox(self, title, msg, level=QMessageBox.Information):
        if self._dialog is not None:
            self._dialog.reject()

        self._dialog = QMessageBox(level, title, msg, QMessageBox.Ok)
        self._dialog.setStyleSheet(WaitingDlg.StyleSheet)

        return self._dialog.exec_()

    def _showQuestionBox(self, title, msg):
        if self._dialog is not None:
            self._dialog.reject()

        self._dialog = QMessageBox(QMessageBox.Question,
                                   title,
                                   msg,
                                   QMessageBox.Yes | QMessageBox.No)
        self._dialog.setStyleSheet(WaitingDlg.StyleSheet)

        return self._dialog.exec_()

    def _showWaitingDlg(self, title, msg):
        if self._dialog is not None:
            self._dialog.reject()
        self._dialog = WaitingDlg(title, msg)
        return self._dialog.exec_()

    def _enableButtons(self, value):
        self.startInjectionBtn.setEnabled(value)
        self.stopInjectionBtn.setEnabled(value)

    @pyqtSlot(str)
    def _showErrorMsg(self, msg):
        self._showMsgBox("Error", msg, QMessageBox.Warning)

    @pyqtSlot()
    def _showStartedMsg(self):
        self._showMsgBox("[InjectionControlWindow]",
                         "Injection started", QMessageBox.Information)

    @pyqtSlot()
    def _showStoppedMsg(self):
        self._showMsgBox("[InjectionControlWindow]",
                         "Injection stopped", QMessageBox.Information)

    def _setBucketProfile(self):
        self.bucket_graph.clear()
        profile = [0 for _ in range(864)]
        x = list(range(864))
        for b in self.controller.bucket_list:
            for i in range(75):
                profile[(b - 1 + i) % 864] += 1

        self.bucket_graph.plot(x, profile)

    def _setupUi(self):
        self._dialog = None

        self.central_widget = QWidget()
        self.central_widget.layout = QGridLayout()

        radio_layout = QVBoxLayout()
        self.multiBunchRadio = QRadioButton("Multi Bunch", self.central_widget)
        self.multiBunchRadio.setObjectName("multiBunchRadio")
        self.singleBunchRadio = QRadioButton("Single Bunch", self.central_widget)
        self.singleBunchRadio.setObjectName("singleBunchRadio")
        radio_layout.addWidget(self.multiBunchRadio)
        radio_layout.addWidget(self.singleBunchRadio)

        cycle_layout = QHBoxLayout()
        self.cycleSpinBox = QSpinBox(self.central_widget)
        self.cycleSpinBox.setObjectName("cycleSpinBox")
        cycle_layout.addWidget(self.cycleSpinBox)

        button_layout = QHBoxLayout()
        self.startInjectionBtn = \
            QPushButton("Start Injection", self.central_widget)
        self.startInjectionBtn.setObjectName("startInjectionBtn")
        self.stopInjectionBtn = \
            QPushButton("Stop Injection", self.central_widget)
        self.stopInjectionBtn.setObjectName("stopInjectionBtn")
        button_layout.addWidget(self.startInjectionBtn)
        button_layout.addWidget(self.stopInjectionBtn)

        bucket_list_layout = QHBoxLayout()
        self.initialBucketSpinBox = QSpinBox(self.central_widget)
        self.initialBucketSpinBox.setObjectName("initialBucketSpinBox")
        self.finalBucketSpinBox = QSpinBox(self.central_widget)
        self.finalBucketSpinBox.setObjectName("finalBucketSpinBox")
        self.stepSpinBox = QSpinBox(self.central_widget)
        self.stepSpinBox.setObjectName("stepSpinBox")
        bucket_list_layout.addWidget(self.initialBucketSpinBox)
        bucket_list_layout.addWidget(self.finalBucketSpinBox)
        bucket_list_layout.addWidget(self.stepSpinBox)

        self.bucket_graph = pg.PlotWidget()
        self.bucket_graph.setYRange(min=0, max=2)
        # self.bucket_graph.mouseEnabled = False
        # self.bucket_graph.setAspectLocked(1)
        # self.bucket_graph.showAxis("left", show=False)
        # self.bucket_graph.showAxis("bottom", show=False)

        led_layout = QHBoxLayout()
        self.ledLabel = QLabel("Injecting")
        self.ledLabel.setObjectName("ledLabel")
        pv = InjectionController.TimingPrefix + ':' + \
            InjectionController.InjectionToggle
        self.injectingLed = PyDMLed(self, init_channel="ca://" + pv)
        self.injectingLed.setObjectName("injectingLed")
        led_layout.addWidget(self.ledLabel)
        led_layout.addWidget(self.injectingLed)

        self.central_widget.layout.addLayout(radio_layout, 0, 0)
        self.central_widget.layout.addLayout(cycle_layout, 0, 2)
        self.central_widget.layout.addLayout(bucket_list_layout, 1, 0, 1, 3)
        self.central_widget.layout.addWidget(self.bucket_graph, 2, 0, 1, 3)
        self.central_widget.layout.addLayout(button_layout, 3, 0)
        self.central_widget.layout.addLayout(led_layout, 3, 2)

        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Injection Control Window")


if __name__ == "__main__":
    import sys
    from pydm import PyDMApplication

    app = PyDMApplication(None, sys.argv)
    controller = InjectionController()
    window = InjectionWindow(controller)
    sys.exit(app.exec_())
