#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys
import time as _time
from functools import partial as _part
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QMenu, \
    QGroupBox, QPushButton, QWidget, QLabel, QInputDialog, QLineEdit, \
    QDialog, QMessageBox
from qtpy.QtCore import Qt, Signal, QThread
from siriuspy.clientconfigdb import ConfigDBClient
from siriushla.sirius_application import SiriusApplication
from siriushla import util
from siriushla.widgets import SiriusMainWindow
from siriushla.widgets.dialog import ReportDialog, ProgressDialog
from siriushla.misc.epics.wrapper import PyEpicsWrapper
from siriushla.misc.epics.task import EpicsChecker, EpicsSetter


class MyDialog(QDialog):

    def __init__(self, parent, title, message):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        lay = QHBoxLayout(self)
        lay.addWidget(QLabel(message))


class MyThread(QThread):

    openmessage = Signal()
    closemessage = Signal()

    def __init__(self, parent=None, cmd=''):
        super().__init__(parent=parent)
        self.cmd = cmd or ''

    def run(self):
        self.openmessage.emit()
        wind = ''
        while not wind:
            _, wind = util.check_process(self.cmd)
            _time.sleep(0.01)
        self.closemessage.emit()


class ControlApplication(SiriusMainWindow):
    """Main launcher."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent=parent)
        self.setWindowTitle("AS Launcher")
        self._setup_ui()

    def _setup_ui(self):
        self.message = MyDialog(self, 'Wait', '<h3>Loading Window</h3>')

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)

        self.AS_apps = QGroupBox('Accelerator System (AS)')
        self.AS_apps.setLayout(self._create_as_layout())

        self.LI_apps = QGroupBox('Linac (LI)')
        self.LI_apps.setLayout(self._create_li_layout())

        self.TB_apps = QGroupBox('Booster Transport Line (TB)')
        self.TB_apps.setLayout(self._create_section_layout('TB'))

        self.BO_apps = QGroupBox('Booster (BO)')
        self.BO_apps.setLayout(self._create_section_layout('BO'))

        self.TS_apps = QGroupBox('Sirius Transport Line (TS)')
        self.TS_apps.setLayout(self._create_section_layout('TS'))

        self.SI_apps = QGroupBox('Sirius (SI)')
        self.SI_apps.setLayout(self._create_section_layout('SI'))

        self.serv_apps = QGroupBox('Services')
        self.serv_apps.setLayout(self._create_serv_layout())

        self.layout.addWidget(
            QLabel('<h2>Sirius Launcher</h2>', self, alignment=Qt.AlignCenter))
        self.layout.addWidget(self.serv_apps)
        self.layout.addWidget(self.AS_apps)
        self.layout.addWidget(self.LI_apps)
        self.layout.addWidget(self.TB_apps)
        self.layout.addWidget(self.BO_apps)
        self.layout.addWidget(self.TS_apps)
        self.layout.addWidget(self.SI_apps)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.layout)

        self.main_widget.setStyleSheet("""
            QPushButton{
                min-width:9.5em; max-width:9.5em;
                min-height:1.5em; max-height:1.5em;
            }""")

        self.setCentralWidget(self.main_widget)

    def _create_as_layout(self):
        operation = QPushButton('Operation', self)
        self.connect_newprocess(operation, 'sirius-hla-as-ap-operation.py')

        injection = QPushButton('Injection', self)
        self.connect_newprocess(injection, 'sirius-hla-as-ap-injection.py')

        timing = QPushButton('Timing', self)
        self.connect_newprocess(timing, 'sirius-hla-as-ti-control.py')

        pwrsupply = QPushButton('Power Supplies')
        menu = QMenu(pwrsupply)
        pwrsupply.setMenu(menu)

        pscycle = menu.addAction('PS Cycle')
        self.connect_newprocess(pscycle, 'sirius-hla-as-ps-cycle.py')
        psdiag = menu.addAction('PS Diag')
        self.connect_newprocess(psdiag, 'sirius-hla-as-ps-diag.py')
        pstest = menu.addAction('PS Test')
        self.connect_newprocess(pstest, 'sirius-hla-as-ps-test.py')
        psmonitor = menu.addAction('PS Monitor')
        self.connect_newprocess(psmonitor, 'sirius-hla-as-ps-monitor.py')

        optics = QPushButton('Optics')
        menu = QMenu(optics)
        optics.setMenu(menu)

        energy_button = menu.addAction('Energy Button')
        self.connect_newprocess(
            energy_button, 'sirius-hla-as-ap-energybutton.py')

        offconv = menu.addAction('Offline Converter')
        self.connect_newprocess(offconv, 'sirius-hla-as-ap-magoffconv.py')

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(operation, 0, 0)
        lay.addWidget(injection, 0, 1)
        lay.addWidget(timing, 0, 2)
        lay.addWidget(pwrsupply, 0, 3)
        lay.addWidget(optics, 0, 4)
        return lay

    def connect_newprocess(self, button, cmd):
        signal = util.get_appropriate_signal(button)
        signal.connect(_part(self._prepare, cmd))
        util.connect_newprocess(button, cmd)

    def _prepare(self, cmd):
        th = MyThread(self, cmd=cmd)
        th.openmessage.connect(self.message.show)
        th.closemessage.connect(self.message.close)
        th.start()

    def _create_serv_layout(self):
        servconf = QPushButton('ConfigDB Manager')
        self.connect_newprocess(servconf, 'sirius-hla-as-ap-configdb.py')

        pvsconfig = QPushButton('PVs configs')
        menu = QMenu(pvsconfig)
        pvsconfig.setMenu(menu)

        pvssave = menu.addAction('Save Config')
        self.connect_newprocess(
            pvssave, 'sirius-hla-as-ap-pvsconfigs-save.py')
        pvsload = menu.addAction('Load Config')
        self.connect_newprocess(
            pvsload, 'sirius-hla-as-ap-pvsconfigs-load.py')

        menu.addSeparator()
        act = menu.addAction('Load Standby')
        act.triggered.connect(self._applyconfig)
        act = menu.addAction('Load TurnOff')
        act.triggered.connect(self._applyconfig)

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(servconf)
        lay.addWidget(pvsconfig)
        return lay

    def _applyconfig(self):
        sender_text = self.sender().text()
        if 'Standby' in sender_text:
            config_name = 'standby'
        elif 'TurnOff' in sender_text:
            config_name = 'turnoff'

        ans = QMessageBox.question(
            self, 'Are you Sure?',
            "Do you really want to apply the Configuration'" + config_name +
            "' to the machine?",
            QMessageBox.Yes, QMessageBox.Cancel)
        if ans != QMessageBox.Yes:
            return

        server_global = ConfigDBClient(config_type='global_config')
        try:
            config = server_global.get_config_value(config_name)['pvs']
        except Exception:
            QMessageBox.critical(
                self, 'Problem Loading',
                'Configuration \''+config_name+'\' not found in Server!')
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
        set_task = EpicsSetter(pvs, values, delays, PyEpicsWrapper, self)
        pvs, values, delays = zip(*check_pvs_tuple)
        check_task = EpicsChecker(pvs, values, delays, PyEpicsWrapper, self)
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

    def _create_li_layout(self):
        LI_launcher = QPushButton('Linac launcher', self)
        util.connect_newprocess(LI_launcher, 'sirius-hla-li-launcher.sh')

        optics = QPushButton('Optics', self)
        menu = QMenu(self)
        optics.setMenu(menu)

        energy = menu.addAction('Energy Meas')
        self.connect_newprocess(energy, 'sirius-hla-li-ap-energy.py')

        emit = menu.addAction('Emittance Meas')
        self.connect_newprocess(emit, 'sirius-hla-li-ap-emittance.py')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(LI_launcher)
        lay.addWidget(optics)
        return lay

    def _create_section_layout(self, sec):
        sec = sec.lower()

        PS = self._set_psma_button(sec, dis='ps')
        MA = self._set_psma_button(sec, dis='ma')
        OPT = self._set_optics_button(sec)
        DIG = self._set_diagnostic_button(sec)

        glay = QGridLayout()
        glay.setVerticalSpacing(15)
        glay.setAlignment(Qt.AlignLeft)
        glay.addWidget(PS, 0, 0)
        glay.addWidget(MA, 0, 1)
        glay.addWidget(OPT, 0, 2)
        glay.addWidget(DIG, 0, 3)
        return glay

    def _set_optics_button(self, sec):
        pbt = QPushButton('Optics', self)
        menu = QMenu(pbt)
        menu.setStyleSheet('background-color: blue;')
        pbt.setMenu(menu)

        if sec in {'tb', 'ts'}:
            launcher = menu.addAction('Main')
            self.connect_newprocess(
                launcher, 'sirius-hla-'+sec+'-ap-control.py')

        sofb = menu.addAction('SOFB')
        self.connect_newprocess(sofb, 'sirius-hla-'+sec+'-ap-sofb.py')

        if sec in {'tb', 'ts'}:
            PosAng = menu.addAction('PosAng')
            self.connect_newprocess(PosAng, 'sirius-hla-'+sec+'-ap-posang.py')
        if 'tb' in sec:
            Emittance = menu.addAction('Emittance Meas')
            self.connect_newprocess(Emittance, 'sirius-hla-tb-ap-emittance.py')
        if sec in {'bo', 'si'}:
            CurrLT = menu.addAction('Current and Lifetime')
            self.connect_newprocess(CurrLT, 'sirius-hla-'+sec+'-ap-currlt.py')

            TuneCorr = menu.addAction('Tune Correction')
            self.connect_newprocess(TuneCorr,
                                    'sirius-hla-'+sec+'-ap-tunecorr.py')

            ChromCorr = menu.addAction('Chromaticity Correction')
            self.connect_newprocess(ChromCorr,
                                    'sirius-hla-'+sec+'-ap-chromcorr.py')
        if 'bo' in sec:
            Ramp = menu.addAction('Ramp')
            self.connect_newprocess(Ramp, 'sirius-hla-bo-ap-ramp.py')
        return pbt

    def _set_diagnostic_button(self, sec):
        pbt = QPushButton('Diagnostic', self)
        menu = QMenu(pbt)
        menu.setStyleSheet('QMenu {background-color: green;}')
        pbt.setMenu(menu)

        BPMs = self._set_bpm_menu(sec)
        menu.addMenu(BPMs)
        if sec in {'tb', 'ts'}:
            ICTs = menu.addAction('ICTs')
            self.connect_newprocess(ICTs, 'sirius-hla-'+sec+'-di-icts.py')
        if 'tb' in sec:
            Slits = menu.addAction('Slits')
            self.connect_newprocess(Slits, 'sirius-hla-tb-di-slits.py')
        if 'si' not in sec:
            Scrns = menu.addAction('Screens')
            self.connect_newprocess(Scrns,
                                    ['sirius-hla-as-di-scrn.py', sec.upper()])
        return pbt

    def _set_bpm_menu(self, sec):
        cmd = ['sirius-hla-as-di-bpm.py', sec, '-w']
        menu = QMenu('BPMs', self)
        action = menu.addAction('Summary')
        self.connect_newprocess(action, cmd + ['Summary', ])
        typs = ('Single Pass', 'Multi Turn')
        acts = ('SPass', 'MTurn')
        for typ, act in zip(typs, acts):
            if sec == 'bo':
                menu2 = menu.addMenu(typ)
                action2 = menu2.addAction('All')
                self.connect_newprocess(action2, cmd + [act, ])
                action2 = menu2.addAction('subsec 02-11')
                self.connect_newprocess(action2, cmd + [act, '-s', '1'])
                action2 = menu2.addAction('subsec 12-21')
                self.connect_newprocess(action2, cmd + [act, '-s', '2'])
                action2 = menu2.addAction('subsec 22-31')
                self.connect_newprocess(action2, cmd + [act, '-s', '3'])
                action2 = menu2.addAction('subsec 32-41')
                self.connect_newprocess(action2, cmd + [act, '-s', '4'])
                action2 = menu2.addAction('subsec 42-01')
                self.connect_newprocess(action2, cmd + [act, '-s', '5'])
                action.setMenu(menu2)
            else:
                action = menu.addAction(typ)
                self.connect_newprocess(action, cmd + [act, ])
        return menu

    def _set_psma_button(self, sec, dis='ps'):
        scr = 'sirius-hla-' + sec + '-' + dis + '-control.py'
        but = QPushButton('Magnets' if dis == 'ma' else 'Power Supplies', self)
        menu = QMenu(self)
        but.setMenu(menu)

        all_dev = menu.addAction('All')
        self.connect_newprocess(all_dev, scr)

        dip = menu.addAction('Dipoles')
        self.connect_newprocess(dip, [scr, '--device', 'dipole'])

        quad = menu.addAction('Quadrupoles')
        self.connect_newprocess(quad, [scr, '--device', 'quadrupole'])

        if sec in {'bo', 'si'}:
            sext = menu.addAction('Sextupoles')
            self.connect_newprocess(sext, [scr, '--device', 'sextupole'])

            skew = menu.addAction('Skew Quadrupoles')
            self.connect_newprocess(skew, [scr, '--device', 'quadrupole-skew'])
        corrs = menu.addAction('Correctors')
        self.connect_newprocess(corrs, [scr, '--device', 'corrector-slow'])
        if sec in 'si':
            fcorr = menu.addAction('Fast Correctors')
            self.connect_newprocess(fcorr, [scr, '--device', 'corrector-fast'])
        if dis in 'ma':
            pmag = menu.addAction('Pulsed Magnets')
            self.connect_newprocess(pmag, 'sirius-hla-'+sec+'-pm-control.py')
        return but


if __name__ == "__main__":

    app = SiriusApplication()
    app.open_window(ControlApplication)
    sys.exit(app.exec_())
