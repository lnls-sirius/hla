"""Interface to handle main operation commands."""

import qtawesome as qta

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout

from siriuspy.envars import vaca_prefix
from siriuspy.search import LLTimeSearch as _LLTimeSearch

from pydm.widgets import PyDMPushButton
from siriushla.util import get_appropriate_color
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ti_control import BucketList
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    SiriusLedState, SiriusLedAlert
from siriushla.common.epics.wrapper import PyEpicsWrapper
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
        egun.setStyleSheet('min-width: 5em;')

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

        evg_update_label = QLabel(
            '<h4>Update</h4>', self, alignment=Qt.AlignCenter)
        evg_update_sel = PyDMPushButton(
            self,
            init_channel=self._prefix+evg_name+':UpdateEvt-Cmd', pressValue=1)
        evg_update_sel.setIcon(qta.icon('fa5s.sync'))
        evg_update_sel.setToolTip('Update Events Table')
        evg_update_sel.setObjectName('but')
        evg_update_sel.setStyleSheet(
            '#but{min-width:25px; max-width:25px; icon-size:20px;}')
        evg_update_sts = SiriusLedAlert(
            parent=self,
            init_channel=self._prefix+evg_name+':EvtSyncStatus-Mon')
        evg_update_sts.setOffColor(evg_update_sts.Red)
        evg_update_sts.setOnColor(evg_update_sts.LightGreen)

        evg_bucket_list = BucketList(
            self, prefix=self._prefix+evg_name+':', min_size=15)

        pbt = QPushButton('>', self)
        pbt.clicked.connect(self._toggle_expand_horizontal)
        pbt.setStyleSheet('max-width: 0.8em;')
        self.expandwid_hor = evg_bucket_list
        self.expandwid_hor.setVisible(False)

        timing_lay = QGridLayout()
        timing_lay.setVerticalSpacing(5)
        timing_lay.setHorizontalSpacing(15)
        timing_lay.addWidget(evg_update_label, 0, 0)
        timing_lay.addWidget(evg_update_sel, 1, 0, alignment=Qt.AlignCenter)
        timing_lay.addWidget(evg_update_sts, 2, 0)
        timing_lay.addWidget(evg_continuous_label, 0, 1)
        timing_lay.addWidget(evg_continuous_sel, 1, 1)
        timing_lay.addWidget(evg_continuous_sts, 2, 1)
        timing_lay.addWidget(evg_injection_label, 0, 2)
        timing_lay.addWidget(evg_injection_sel, 1, 2)
        timing_lay.addWidget(evg_injection_sts, 2, 2)
        timing_lay.addWidget(evg_bucket_list, 0, 3, 3, 1)
        timing_lay.addWidget(pbt, 2, 4)
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

    def _toggle_expand_horizontal(self):
        self.expandwid_hor.setVisible(self.expandwid_hor.isHidden())
        text = '>' if self.expandwid_hor.isHidden() else '<'
        self.sender().setText(text)
        self.sender().parent().adjustSize()
        self.centralWidget().adjustSize()
        self.adjustSize()


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = MainOperation()
    window.show()
    sys.exit(app.exec_())
