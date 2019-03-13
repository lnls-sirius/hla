"""Interface to handle main operation commands."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QPushButton, QLabel, \
    QGridLayout, QHBoxLayout

from siriuspy.envars import vaca_prefix
from siriuspy.timesys.ll_classes import get_evg_name
from siriuspy.servconf.srvconfig import ConnConfigService

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    SiriusLedState, SiriusLedAlert
from siriushla.misc.epics.wrapper import PyEpicsWrapper
from siriushla.misc.epics.task import EpicsChecker, EpicsSetter
from siriushla.widgets.dialog import ReportDialog, ProgressDialog


class MainOperation(SiriusMainWindow):
    """Main Operation."""

    def __init__(self, parent=None, wrapper=PyEpicsWrapper,
                 prefix=vaca_prefix):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._wrapper = wrapper
        self._setupUi()
        self.setWindowTitle('Main Controls')
        self.move(0, 0)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def _setupUi(self):
        # Egun triggers
        egun = QGroupBox('Egun Trigger')

        egun_trigger_enable = PyDMStateButton(
            parent=self, init_channel=self._prefix+'egun:triggerps:enable')
        egun_trigger_status = SiriusLedAlert(
            parent=self, init_channel=self._prefix+'egun:triggerps:status')
        egun_trigger_status.setOnColor(SiriusLedAlert.LightGreen)
        egun_trigger_status.setOffColor(SiriusLedAlert.DarkGreen)

        egun_lay = QGridLayout()
        egun_lay.setVerticalSpacing(5)
        egun_lay.setHorizontalSpacing(15)
        egun_lay.addWidget(egun_trigger_enable, 1, 0)
        egun_lay.addWidget(egun_trigger_status, 2, 0)
        egun.setLayout(egun_lay)

        # EVG control
        timing = QGroupBox('EVG Control')

        evg_continuous_label = QLabel('<h4>Continuous</h4>', self,
                                      alignment=Qt.AlignCenter)
        evg_continuous_sel = PyDMStateButton(
            parent=self,
            init_channel=self._prefix+get_evg_name()+':ContinuousEvt-Sel')
        evg_continuous_sts = SiriusLedState(
            parent=self,
            init_channel=self._prefix+get_evg_name()+':ContinuousEvt-Sts')

        evg_injection_label = QLabel('<h4>Injection</h4>', self,
                                     alignment=Qt.AlignCenter)
        evg_injection_sel = PyDMStateButton(
            parent=self,
            init_channel=self._prefix+get_evg_name()+':InjectionEvt-Sel')
        evg_injection_sts = SiriusLedState(
            parent=self,
            init_channel=self._prefix+get_evg_name()+':InjectionEvt-Sts')

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

        # Load standby and turnoff configurations
        standby_pb = QPushButton('Set \'Standby\' Configuration')
        standby_pb.setAutoDefault(False)
        standby_pb.setDefault(False)
        standby_pb.clicked.connect(self._applyconfig)
        turnoff_pb = QPushButton('Set \'TurnOff\' Configuration')
        turnoff_pb.setAutoDefault(False)
        turnoff_pb.setDefault(False)
        turnoff_pb.clicked.connect(self._applyconfig)

        setconfigs_lay = QGridLayout()
        setconfigs_lay.setVerticalSpacing(5)
        setconfigs_lay.setHorizontalSpacing(15)
        setconfigs_lay.addWidget(standby_pb, 0, 0)
        setconfigs_lay.addWidget(turnoff_pb, 1, 0)

        layout = QHBoxLayout()
        layout.addWidget(egun)
        layout.addWidget(timing)
        layout.addLayout(setconfigs_lay)

        cw = QWidget(self)
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _applyconfig(self):
        sender_text = self.sender().text()
        if 'Standby' in sender_text:
            config_name = 'standby'
        elif 'TurnOff' in sender_text:
            config_name = 'turnoff'

        server_global = ConnConfigService('global_config')
        try:
            config = server_global.config_get(config_name)[0]['pvs']
        except Exception:
            print('Configuration \''+config_name+'\' not found in Server!')
            return

        set_pvs_tuple = list()
        check_pvs_tuple = list()
        for t in config:
            try:
                pv, value, delay = t
            except ValueError:
                pv, value = t
                delay = 1e-2
            set_pvs_tuple.append((pv, value, delay))
            check_pvs_tuple.append((pv, value, delay))

        # Create thread
        failed_items = []
        pvs, values, delays = zip(*set_pvs_tuple)
        set_task = EpicsSetter(pvs, values, delays, self._wrapper, self)
        pvs, values, delays = zip(*check_pvs_tuple)
        check_task = EpicsChecker(pvs, values, delays, self._wrapper, self)
        check_task.itemChecked.connect(
           lambda pv, status: failed_items.append(pv) if not status else None)

        # Set/Check PVs values and show wait dialog informing user
        labels = ['Setting PV values', 'Checking PV values']
        tasks = [set_task, check_task]
        dlg = ProgressDialog(labels, tasks, self)
        dlg.rejected.connect(set_task.exit_task)
        dlg.rejected.connect(check_task.exit_task)
        ret = dlg.exec_()
        if ret == dlg.Rejected:
            return
        # Show report dialog informing user results
        self._report = ReportDialog(failed_items, self)
        self._report.show()


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = MainOperation()
    window.show()
    sys.exit(app.exec_())
