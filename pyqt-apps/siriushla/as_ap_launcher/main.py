"""Interface to handle main operation commands."""

import qtawesome as qta

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout

from siriuspy.envars import vaca_prefix
from siriuspy.search import LLTimeSearch as _LLTimeSearch

from siriushla.util import get_appropriate_color
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    SiriusLedState, SiriusLedAlert
from siriushla.misc.epics.wrapper import PyEpicsWrapper
from .menu import get_object


class MainOperation(SiriusMainWindow):
    """Main Operation."""

    def __init__(self, parent=None, wrapper=PyEpicsWrapper,
                 prefix=vaca_prefix):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._wrapper = wrapper
        menubar = get_object(ismenubar=True)
        menubar.setNativeMenuBar(False)
        self.setMenuBar(menubar)
        self._setupUi()
        self.setWindowTitle('Main Controls')
        self.setWindowIcon(
            qta.icon('mdi.rocket', color=get_appropriate_color('AS')))
        self.move(0, 20)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def _setupUi(self):
        # Egun triggers
        egun = QGroupBox('Egun Trigger')
        egun.setStyleSheet('min-width: 8em;')

        egun_trigger_enable = PyDMStateButton(
            parent=self, init_channel=self._prefix+'LI-01:EG-TriggerPS:enable')
        egun_trigger_status = SiriusLedAlert(
            parent=self, init_channel=self._prefix+'LI-01:EG-TriggerPS:status')
        egun_trigger_status.setOnColor(SiriusLedAlert.LightGreen)
        egun_trigger_status.setOffColor(SiriusLedAlert.DarkGreen)

        egun_lay = QGridLayout()
        egun_lay.setVerticalSpacing(5)
        egun_lay.setHorizontalSpacing(15)
        egun_lay.addWidget(QLabel(''))
        egun_lay.addWidget(egun_trigger_enable, 1, 0)
        egun_lay.addWidget(egun_trigger_status, 2, 0)
        egun.setLayout(egun_lay)

        # EVG control
        timing = QGroupBox('EVG Control')

        evg_name = _LLTimeSearch.get_evg_name()
        evg_continuous_label = QLabel(
            '<h4>Continuous</h4>', self, alignment=Qt.AlignCenter)
        evg_continuous_sel = PyDMStateButton(
            parent=self,
            init_channel=self._prefix+evg_name+':ContinuousEvt-Sel')
        evg_continuous_sts = SiriusLedState(
            parent=self,
            init_channel=self._prefix+evg_name+':ContinuousEvt-Sts')

        evg_injection_label = QLabel(
            '<h4>Injection</h4>', self, alignment=Qt.AlignCenter)
        evg_injection_sel = PyDMStateButton(
            parent=self,
            init_channel=self._prefix+evg_name+':InjectionEvt-Sel')
        evg_injection_sts = SiriusLedState(
            parent=self,
            init_channel=self._prefix+evg_name+':InjectionEvt-Sts')

        timing_lay = QGridLayout()
        timing_lay.setVerticalSpacing(5)
        timing_lay.setHorizontalSpacing(15)
        timing_lay.addWidget(evg_continuous_label, 0, 0)
        timing_lay.addWidget(evg_continuous_sel, 1, 0)
        timing_lay.addWidget(evg_continuous_sts, 2, 0)
        timing_lay.addWidget(evg_injection_label, 0, 1)
        timing_lay.addWidget(evg_injection_sel, 1, 1)
        timing_lay.addWidget(evg_injection_sts, 2, 1)
        timing.setLayout(timing_lay)

        pbt = QPushButton('v', self)
        pbt.clicked.connect(self._toggle_expand)
        pbt.setStyleSheet('max-width: 0.8em;')

        self.expandwid = get_object(ismenubar=False, parent=self)
        self.expandwid.setVisible(False)

        layout = QGridLayout()
        layout.addWidget(egun, 0, 0)
        layout.addWidget(timing, 0, 1)
        layout.addWidget(pbt, 0, 2, alignment=Qt.AlignLeft | Qt.AlignBottom)
        layout.addWidget(self.expandwid, 2, 0, 1, 3)

        cw = QWidget(self)
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _toggle_expand(self):
        self.expandwid.setVisible(self.expandwid.isHidden())
        text = 'v' if self.expandwid.isHidden() else '^'
        self.sender().setText(text)
        self.centralWidget().adjustSize()
        self.adjustSize()


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = MainOperation()
    window.show()
    sys.exit(app.exec_())
