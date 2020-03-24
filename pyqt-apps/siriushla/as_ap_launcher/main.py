"""Interface to handle main operation commands."""

import qtawesome as qta

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QApplication, QMessageBox, QMenu, QAction
from pydm.widgets import PyDMPushButton

from siriuspy.envars import VACA_PREFIX
from siriuspy.search import LLTimeSearch as _LLTimeSearch

from siriushla.util import get_appropriate_color
from siriushla.sirius_application import SiriusApplication
from siriushla.as_ti_control import BucketList
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    SiriusLedAlert, PyDMLed
from siriushla.common.epics.wrapper import PyEpicsWrapper
from .menu import get_object
from .standby_widgets import InjSysStandbyEnblDsbl, InjSysStandbyStatusLed


class MainOperation(SiriusMainWindow):
    """Main Operation."""

    def __init__(self, parent=None, wrapper=PyEpicsWrapper,
                 prefix=VACA_PREFIX):
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
        screens = QApplication.screens()
        screen_idx = 3 if len(screens) == 8 else 0
        topleft = screens[screen_idx].geometry().topLeft()
        self.move(topleft.x(), topleft.y()+20)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setObjectName('ASApp')

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

        # Injection System
        injsys = QGroupBox('Injection System')
        injsys.setObjectName('InjSys')
        injsys_state_sel = InjSysStandbyEnblDsbl(self)
        injsys_state_sts = InjSysStandbyStatusLed(self)

        injsys_lay = QGridLayout()
        injsys_lay.setVerticalSpacing(5)
        injsys_lay.setHorizontalSpacing(15)
        injsys_lay.addWidget(QLabel(''))
        injsys_lay.addWidget(injsys_state_sel, 1, 0)
        injsys_lay.addWidget(injsys_state_sts, 2, 0)
        injsys.setLayout(injsys_lay)

        # EVG control
        timing = QGroupBox('EVG Control')

        evg_name = _LLTimeSearch.get_evg_name()
        evg_continuous_label = QLabel(
            '<h4>Continuous</h4>', self, alignment=Qt.AlignCenter)
        evg_continuous_sel = PyDMStateButton(
            parent=self,
            init_channel=self._prefix+evg_name+':ContinuousEvt-Sel')
        color_list = 7*[PyDMLed.LightGreen, ]
        color_list[0] = PyDMLed.DarkGreen  # Initializing
        color_list[1] = PyDMLed.DarkGreen  # Stopped
        color_list[4] = PyDMLed.Yellow  # Preparing Continuous
        color_list[6] = PyDMLed.Yellow  # Restarting Continuous
        evg_continuous_sts = PyDMLed(
            parent=self,
            init_channel=self._prefix+evg_name+':STATEMACHINE',
            color_list=color_list)

        evg_injection_label = QLabel(
            '<h4>Injection</h4>', self, alignment=Qt.AlignCenter)
        evg_injection_sel = PyDMStateButton(
            parent=self,
            init_channel=self._prefix+evg_name+':InjectionEvt-Sel')
        color_list = 7*[PyDMLed.DarkGreen, ]
        color_list[3] = PyDMLed.LightGreen  # Injection
        color_list[5] = PyDMLed.Yellow  # Preparing Injection
        evg_injection_sts = PyDMLed(
            parent=self,
            init_channel=self._prefix+evg_name+':STATEMACHINE',
            color_list=color_list)

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
        timing_lay.addWidget(pbt, 2, 3)
        timing_lay.addWidget(evg_bucket_list, 0, 4, 3, 1)
        timing.setLayout(timing_lay)

        pbt = QPushButton('v', self)
        pbt.clicked.connect(self._toggle_expand)
        pbt.setStyleSheet('max-width: 0.8em;')

        self.expandwid = get_object(ismenubar=False, parent=self)
        self.expandwid.setVisible(False)

        layout = QGridLayout()
        layout.addWidget(egun, 0, 0)
        layout.addWidget(injsys, 0, 1)
        layout.addWidget(timing, 0, 2)
        layout.addWidget(pbt, 0, 3, alignment=Qt.AlignLeft | Qt.AlignBottom)
        layout.addWidget(self.expandwid, 2, 0, 1, 4)

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

    def _show_help_message(self):
        QMessageBox.information(
            self, 'What does this box control?',
            'This box controls: \n\n'
            '- The Pulse-Sel/Sts and PwrState-Sel/Sts PVs of Pulsed Magnets\n'
            ' (TB-04:PU-InjSept,  BO-01D:PU-InjKckr,\n'
            '  BO-48D:PU-EjeKckr, TS-01:PU-EjeSeptF, TS-01:PU-EjeSeptG,\n'
            '  TS-04:PU-InjSeptF, TS-04:PU-InjSeptG-1, TS-04:PU-InjSeptG-2,\n'
            '  SI-01SA:PU-InjNLKckr);\n\n'
            '- The RF Ramp (RmpEnbl-Sel/Sts).\n')

    def contextMenuEvent(self, event):
        """Show a custom context menu."""
        point = event.pos()
        widget = self.childAt(event.pos())
        parent = widget.parent()
        grand_parent = parent.parent()
        if widget.objectName() == 'InjSys' or \
                parent.objectName() == 'InjSys' or \
                grand_parent.objectName() == 'InjSys':
            menu = QMenu(self)
            act = QAction('What does this box control?', self)
            act.triggered.connect(self._show_help_message)
            menu.addAction(act)
            menu.popup(self.mapToGlobal(point))


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = MainOperation()
    window.show()
    sys.exit(app.exec_())
