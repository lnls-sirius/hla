#!/usr/bin/env python-sirius

"""Mock application launcher."""

import time as _time
from functools import partial as _part
from qtpy.QtWidgets import QPushButton, QDialog, QMessageBox, QMenuBar, \
    QMenu, QLabel, QHBoxLayout
from qtpy.QtCore import Signal, QThread
from siriuspy.clientconfigdb import ConfigDBClient
from siriushla import util
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


class MainMenuBar(QMenuBar):
    """Main launcher."""

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self):
        self.message = MyDialog(self, 'Wait', '<h3>Loading Window</h3>')
        as_apps = self._create_as_menu()
        li_apps = self._create_li_menu()
        tb_apps = self._create_section_menu('TB', 'TB')
        bo_apps = self._create_section_menu('BO', 'BO')
        ts_apps = self._create_section_menu('TS', 'TS')
        si_apps = self._create_section_menu('SI', 'SI')
        serv_apps = self._create_serv_menu()

        self.addMenu(serv_apps)
        self.addMenu(as_apps)
        self.addMenu(li_apps)
        self.addMenu(tb_apps)
        self.addMenu(bo_apps)
        self.addMenu(ts_apps)
        self.addMenu(si_apps)

    def _create_serv_menu(self):
        menu = QMenu('Services', self)
        menu.setObjectName('ServMenu')
        servconf = menu.addAction('ConfigDB Manager')
        self.connect_newprocess(servconf, 'sirius-hla-as-ap-configdb.py')

        pvsconfig = menu.addMenu('PVs configs')
        pvsconfig.setObjectName('ServMenu')
        pvssave = pvsconfig.addAction('Save Config')
        self.connect_newprocess(
            pvssave, 'sirius-hla-as-ap-pvsconfigs-save.py')
        pvsload = pvsconfig.addAction('Load Config')
        self.connect_newprocess(
            pvsload, 'sirius-hla-as-ap-pvsconfigs-load.py')

        pvsconfig.addSeparator()
        act = pvsconfig.addAction('Load Standby')
        act.triggered.connect(self._applyconfig)
        act = pvsconfig.addAction('Load TurnOff')
        act.triggered.connect(self._applyconfig)
        return menu

    def _create_as_menu(self):
        menu = QMenu('AS', self)
        menu.setObjectName('ASApp')

        injection = menu.addAction('Injection')
        self.connect_newprocess(injection, 'sirius-hla-as-ap-injection.py')
        timing = menu.addAction('Timing')
        self.connect_newprocess(timing, 'sirius-hla-as-ti-control.py')

        pwrsupply = menu.addMenu('Power Supplies')
        pwrsupply.setObjectName('ASApp')
        pscycle = pwrsupply.addAction('PS Cycle')
        self.connect_newprocess(pscycle, 'sirius-hla-as-ps-cycle.py')
        psdiag = pwrsupply.addAction('PS Diag')
        self.connect_newprocess(psdiag, 'sirius-hla-as-ps-diag.py')
        pstest = pwrsupply.addAction('PS Test')
        self.connect_newprocess(pstest, 'sirius-hla-as-ps-test.py')
        psmonitor = pwrsupply.addAction('PS Monitor')
        self.connect_newprocess(psmonitor, 'sirius-hla-as-ps-monitor.py')

        optics = menu.addMenu('Optics')
        optics.setObjectName('ASApp')
        energy_button = optics.addAction('Energy Button')
        self.connect_newprocess(
            energy_button, 'sirius-hla-as-ap-energybutton.py')
        offconv = optics.addAction('Offline Converter')
        self.connect_newprocess(offconv, 'sirius-hla-as-ap-magoffconv.py')
        return menu

    def _create_li_menu(self):
        menu = QMenu('LI', self)
        menu.setObjectName('LIApp')
        LI_launcher = menu.addAction('Linac launcher')
        util.connect_newprocess(LI_launcher, 'sirius-hla-li-launcher.sh')

        optics = menu.addMenu('Optics')
        optics.setObjectName('LIApp')
        energy = optics.addAction('Energy Meas')
        self.connect_newprocess(energy, 'sirius-hla-li-ap-energy.py')
        emit = optics.addAction('Emittance Meas')
        self.connect_newprocess(emit, 'sirius-hla-li-ap-emittance.py')
        return menu

    def _create_section_menu(self, name, sec):
        sec = sec.lower()
        menu = QMenu(name, self)
        menu.setObjectName(sec.upper()+'App')

        PS = self._set_psma_menu(sec, dis='ps')
        MA = self._set_psma_menu(sec, dis='ma')
        OPT = self._set_optics_menu(sec)
        DIG = self._set_diagnostic_menu(sec)
        menu.addMenu(PS)
        menu.addMenu(MA)
        menu.addMenu(DIG)
        menu.addMenu(OPT)
        return menu

    def _set_optics_menu(self, sec):
        optics = QMenu('Optics', self)
        optics.setObjectName(sec.upper()+'App')

        if sec in {'tb', 'ts'}:
            launcher = optics.addAction('Main')
            self.connect_newprocess(
                launcher, 'sirius-hla-'+sec+'-ap-control.py')

        sofb = optics.addAction('SOFB')
        self.connect_newprocess(sofb, 'sirius-hla-'+sec+'-ap-sofb.py')

        if sec in {'tb', 'ts'}:
            PosAng = optics.addAction('PosAng')
            self.connect_newprocess(PosAng, 'sirius-hla-'+sec+'-ap-posang.py')
        if 'tb' in sec:
            Emittance = optics.addAction('Emittance Meas')
            self.connect_newprocess(Emittance, 'sirius-hla-tb-ap-emittance.py')
        if sec in {'bo', 'si'}:
            CurrLT = optics.addAction('Current and Lifetime')
            self.connect_newprocess(CurrLT, 'sirius-hla-'+sec+'-ap-currlt.py')

            TuneCorr = optics.addAction('Tune Correction')
            self.connect_newprocess(TuneCorr,
                                    'sirius-hla-'+sec+'-ap-tunecorr.py')

            ChromCorr = optics.addAction('Chromaticity Correction')
            self.connect_newprocess(ChromCorr,
                                    'sirius-hla-'+sec+'-ap-chromcorr.py')
        if 'bo' in sec:
            Ramp = optics.addAction('Ramp')
            self.connect_newprocess(Ramp, 'sirius-hla-bo-ap-ramp.py')
        return optics

    def _set_diagnostic_menu(self, sec):
        diag = QMenu('Diagnostic', self)
        diag.setObjectName(sec.upper()+'App')

        BPMs = self._set_bpm_menu(sec)
        diag.addMenu(BPMs)
        if sec in {'tb', 'ts'}:
            ICTs = diag.addAction('ICTs')
            self.connect_newprocess(ICTs, 'sirius-hla-'+sec+'-di-icts.py')
        if 'tb' in sec:
            Slits = diag.addAction('Slits')
            self.connect_newprocess(Slits, 'sirius-hla-tb-di-slits.py')
        if 'si' not in sec:
            Scrns = diag.addAction('Screens')
            self.connect_newprocess(Scrns,
                                    ['sirius-hla-as-di-scrn.py', sec.upper()])
        return diag

    def _set_bpm_menu(self, sec):
        cmd = ['sirius-hla-as-di-bpm.py', sec, '-w']
        menu = QMenu('BPMs', self)
        menu.setObjectName(sec.upper()+'App')
        action = menu.addAction('Summary')
        self.connect_newprocess(action, cmd + ['Summary', ])
        typs = ('Single Pass', 'Multi Turn')
        acts = ('SPass', 'MTurn')
        for typ, act in zip(typs, acts):
            if sec == 'bo':
                menu2 = menu.addMenu(typ)
                menu2.setObjectName(sec.upper()+'App')
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
            else:
                action = menu.addAction(typ)
                self.connect_newprocess(action, cmd + [act, ])
        return menu

    def _set_psma_menu(self, sec, dis='ps'):
        scr = 'sirius-hla-' + sec + '-' + dis + '-control.py'
        psma = QMenu('Magnets' if dis == 'ma' else 'Power Supplies', self)
        psma.setObjectName(sec.upper()+'App')

        all_dev = psma.addAction('All')
        self.connect_newprocess(all_dev, scr)

        dip = psma.addAction('Dipoles')
        self.connect_newprocess(dip, [scr, '--device', 'dipole'])

        quad = psma.addAction('Quadrupoles')
        self.connect_newprocess(quad, [scr, '--device', 'quadrupole'])

        if sec in {'bo', 'si'}:
            sext = psma.addAction('Sextupoles')
            self.connect_newprocess(sext, [scr, '--device', 'sextupole'])

            skew = psma.addAction('Skew Quadrupoles')
            self.connect_newprocess(skew, [scr, '--device', 'quadrupole-skew'])
        corrs = psma.addAction('Correctors')
        self.connect_newprocess(corrs, [scr, '--device', 'corrector-slow'])
        if sec in 'si':
            fcorr = psma.addAction('Fast Correctors')
            self.connect_newprocess(fcorr, [scr, '--device', 'corrector-fast'])
        if dis in 'ma':
            pmag = psma.addAction('Pulsed Magnets')
            self.connect_newprocess(pmag, 'sirius-hla-'+sec+'-pm-control.py')
        return psma

    def connect_newprocess(self, button, cmd):
        signal = util.get_appropriate_signal(button)
        signal.connect(_part(self._prepare, cmd))
        util.connect_newprocess(button, cmd)

    def _prepare(self, cmd):
        th = MyThread(self, cmd=cmd)
        th.openmessage.connect(self.message.show)
        th.closemessage.connect(self.message.close)
        th.start()

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
