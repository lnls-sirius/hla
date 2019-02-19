"""GUI for injection."""
from pydm import PyDMApplication
from qtpy.QtCore import Slot, QTimer, Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QRadioButton, QPushButton, QSpinBox, QGridLayout, QMessageBox, QDialog, \
    QLabel, QDockWidget
from pydm.widgets.label import PyDMLabel
from pydm.widgets.checkbox import PyDMCheckbox

from siriushla.widgets.led import SiriusLedState
from siriushla.widgets import SiriusMainWindow
from siriushla.as_ap_injection.CustomExceptions import PVConnectionError
from siriushla.as_ap_injection.InjectionController import InjectionController
from siriushla.as_ap_injection.BarGraphWidget \
    import BarGraphWidget, PyDMBarGraph
from siriuspy.envars import vaca_prefix as _VACA_PREFIX


class WaitingDlg(QDialog):
    """Window that shows message to user."""

    StyleSheet = """
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

    @Slot(int)
    def done(self, r):
        """Override done method."""
        self.may_close = True
        super(WaitingDlg, self).done(r)

    def closeEvent(self, event):
        """Override closeEvent."""
        if self.may_close:
            super(WaitingDlg, self).closeEvent(event)
        else:
            event.ignore()


class InjectionWindow(SiriusMainWindow):
    """Window to set injection parameters and control the injection."""

    StyleSheet = """
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

    def __init__(self, controller=None, parent=None):
        """Init window."""
        super(InjectionWindow, self).__init__(parent)

        self.app = PyDMApplication.instance()
        InjectionWindow.Instance = self

        if controller is None:
            self.controller = InjectionController()
        else:
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

        # self.cycleSpinBox.valueChanged.connect(self.setCycle)
        # self.cycleSpinBox.setEnabled(False)

        self.initialBucketSpinBox.valueChanged.connect(self.setInitialBucket)
        self.finalBucketSpinBox.valueChanged.connect(self.setFinalBucket)
        self.stepSpinBox.valueChanged.connect(self.setStep)

        self.startInjectionBtn.clicked.connect(self.startInjection)
        self.stopInjectionBtn.clicked.connect(self.stopInjection)
        self._enableButtons(False)

        # self.injectingLed.connected_signal.connect(
        #     lambda: self._enableButtons(True))
        # self.injectingLed.disconnected_signal.connect(
        #     lambda: self._enableButtons(False))

        # bl = self.controller.bucket_list

        self.multiBunchRadio.setChecked(True)
        self.setInjectionMode(self.controller.MultiBunch)

        self.initialBucketSpinBox.setRange(1, InjectionController.Harmonic)
        self.initialBucketSpinBox.setValue(1)
        self.finalBucketSpinBox.setRange(1, InjectionController.Harmonic)
        self.finalBucketSpinBox.setValue(InjectionController.Harmonic)
        self.stepSpinBox.setRange(1, 200)
        self.stepSpinBox.setValue(75)

        self.beamCurrentLabel.precFromPV = True
        # self.cycleSpinBox.setRange(1, 20)
        # self.cycleSpinBox.setValue(1)

        # self.app.establish_widget_connections(self)
        # self.show()

    # Public
    @Slot()
    def startInjection(self):
        """Start injection."""
        if self.controller.injecting:
            self._showMsgBox(
                "[InjectionControlWindow]", "Injection is already running")
            return

        if self.cycleCheckBox.isChecked():
            msg = ("Injection will run in cyclic mode.")
        else:
            msg = "Injection will be executed once."

        res = self._showQuestionBox("Start Injection?", msg + "\nProceed?")
        if res in (QMessageBox.Yes, QMessageBox.Accepted):
            # self._startInjection()
            QTimer.singleShot(100, self._startInjection)
            self._showWaitingDlg(
                "[InjectionControlWindow]", "Setting bucket list...")

        # self._dialog = None

    @Slot()
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

    @Slot(int)
    def setInitialBucket(self, value):
        """Set controller initial bucket and update bucket profile."""
        self.controller.initial_bucket = value
        self._setBucketProfile()

    @Slot(int)
    def setFinalBucket(self, value):
        """Set controller final graph and update bucket profile."""
        self.controller.final_bucket = value
        self._setBucketProfile()

    @Slot(int)
    def setStep(self, value):
        """Set controller step and update bucket profile."""
        self.controller.step = value
        self._setBucketProfile()

    @Slot(int)
    def setCycle(self, value):
        """Set controller cycles."""
        self.controller.cycles = value

    def setInjectionMode(self, value):
        """Set controller injection mode."""
        self.controller.mode = value

    # Private
    def _startInjection(self):
        try:
            self.controller.put_bucket_list()

            self._dialog.main_label.setText("Starting injection")
            PyDMApplication.processEvents()

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

    @Slot(str)
    def _showErrorMsg(self, msg):
        self._showMsgBox("Error", msg, QMessageBox.Warning)

    @Slot()
    def _showStartedMsg(self):
        self._showMsgBox("[InjectionControlWindow]",
                         "Injection started", QMessageBox.Information)

    @Slot()
    def _showStoppedMsg(self):
        self._showMsgBox("[InjectionControlWindow]",
                         "Injection stopped", QMessageBox.Information)

    def _setBucketProfile(self):
        self.bucket_graph.clear()
        profile = [0 for _ in range(864)]
        for b in self.controller.bucket_list:
            for i in range(75):
                profile[(b - 1 + i) % 864] += 1

        self.bucket_graph.set_waveform(profile)

    def _setupUi(self):
        self._dialog = None

        self.central_widget = QWidget()
        # self.central_widget.setSizePolicy(
        #      QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.central_widget.layout = QGridLayout()

        radio_layout = QVBoxLayout()
        self.multiBunchRadio = QRadioButton("Multi Bunch", self.central_widget)
        self.multiBunchRadio.setObjectName("multiBunchRadio")
        self.singleBunchRadio = QRadioButton(
            "Single Bunch", self.central_widget)
        self.singleBunchRadio.setObjectName("singleBunchRadio")
        radio_layout.addWidget(self.multiBunchRadio)
        radio_layout.addWidget(self.singleBunchRadio)

        cycle_layout = QHBoxLayout()
        # self.cycleSpinBox = QSpinBox(self.central_widget)
        # self.cycleSpinBox.setObjectName("cycleSpinBox")
        pv = _VACA_PREFIX + "AS-Glob:TI-EVG:InjectionCyc-Sel"
        self.cycleCheckBox = PyDMCheckbox(parent=self, init_channel=pv)
        self.cycleCheckBox.setObjectName("cycleCheckBox")
        self.cycleCheckBox.setText("Cyclic mode")
        pv = _VACA_PREFIX + "AS-Glob:TI-EVG:InjectionCyc-Sts"
        self.cycleLed = SiriusLedState(parent=self, init_channel=pv)
        self.cycleLed.setObjectName("cycleLed")
        cycle_layout.addWidget(self.cycleCheckBox)
        cycle_layout.addWidget(self.cycleLed)

        button_layout = QHBoxLayout()
        self.startInjectionBtn = \
            QPushButton("Start Injection", self.central_widget)
        self.startInjectionBtn.setObjectName("startInjectionBtn")
        self.stopInjectionBtn = \
            QPushButton("Stop Injection", self.central_widget)
        self.stopInjectionBtn.setObjectName("stopInjectionBtn")
        button_layout.addWidget(self.startInjectionBtn)
        button_layout.addWidget(self.stopInjectionBtn)

        bucket_list_layout = QVBoxLayout()
        self.initialBucketLabel = QLabel("&Initial bucket")
        self.initialBucketLabel.setObjectName("initialBucketLabel")
        self.initialBucketSpinBox = QSpinBox(self.central_widget)
        self.initialBucketSpinBox.setObjectName("initialBucketSpinBox")
        self.initialBucketLabel.setBuddy(self.initialBucketSpinBox)
        self.finalBucketLabel = QLabel("&Final bucket")
        self.finalBucketLabel.setObjectName("finalBucketLabel")
        self.finalBucketSpinBox = QSpinBox(self.central_widget)
        self.finalBucketSpinBox.setObjectName("finalBucketSpinBox")
        self.finalBucketLabel.setBuddy(self.finalBucketSpinBox)
        self.stepLabel = QLabel("&Step")
        self.stepLabel.setObjectName("stepLabel")
        self.stepSpinBox = QSpinBox(self.central_widget)
        self.stepSpinBox.setObjectName("stepSpinBox")
        self.stepLabel.setBuddy(self.stepSpinBox)
        bucket_list_layout.addWidget(self.initialBucketLabel)
        bucket_list_layout.addWidget(self.initialBucketSpinBox)
        bucket_list_layout.addWidget(self.finalBucketLabel)
        bucket_list_layout.addWidget(self.finalBucketSpinBox)
        bucket_list_layout.addWidget(self.stepLabel)
        bucket_list_layout.addWidget(self.stepSpinBox)
        bucket_list_layout.addStretch()

        self.bucket_graph = BarGraphWidget()
        self.bucket_graph.setTitle("Bucket List")
        self.bucket_graph.setYRange(min=0, max=2)

        led_layout = QHBoxLayout()
        self.ledLabel = QLabel("Injecting")
        self.ledLabel.setObjectName("ledLabel")
        pv = InjectionController.TimingPrefix + ':' + \
            InjectionController.InjectionToggle
        self.injectingLed = SiriusLedState(self, init_channel=pv)
        self.injectingLed.setObjectName("injectingLed")
        pv = _VACA_PREFIX + "SI-Glob:AP-CurrInfo:Current-Mon"
        self.beamCurrentLabel = PyDMLabel(parent=self, init_channel=pv)
        led_layout.addStretch()
        led_layout.addWidget(self.ledLabel)
        led_layout.addWidget(self.injectingLed)
        led_layout.addWidget(self.beamCurrentLabel)

        self.profile_bar_graph = PyDMBarGraph()
        self.profile_bar_graph.setTitle("Bunch by bunch charge")
        pv = _VACA_PREFIX + "SI-13C4:DI-DCCT:BbBCurrent-Mon"
        self.profile_bar_graph.model.channel = pv
        # self.profile_bar_graph.set_scale (100)
        self.profile_bar_graph.set_brush("b")

        self.central_widget.layout.addLayout(radio_layout, 0, 0)
        self.central_widget.layout.addLayout(cycle_layout, 0, 2)
        self.central_widget.layout.addLayout(bucket_list_layout, 1, 0, 1, 3)
        # self.central_widget.layout.addWidget(self.bucket_graph, 2, 0, 1, 3)
        self.central_widget.layout.addLayout(button_layout, 3, 0)
        self.central_widget.layout.addLayout(led_layout, 3, 2)
        # self.central_widget.layout.addWidget(
        #     self.profile_bar_graph, 0, 3, 4, 1)

        self.central_widget.setLayout(self.central_widget.layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Injection Control Window")

        # Create dock windows
        dock_widget = QDockWidget(self)
        dock_widget.setWidget(self.profile_bar_graph)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock_widget)

        dock_widget = QDockWidget(self)
        dock_widget.setWidget(self.bucket_graph)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    def showEvent(self, event):
        self.profile_bar_graph.start()

    def closeEvent(self, event):
        """Clear open instance."""
        self.profile_bar_graph.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    app = PyDMApplication(None, sys.argv)
    controller = InjectionController()
    window = InjectionWindow(controller)
    sys.exit(app.exec_())
