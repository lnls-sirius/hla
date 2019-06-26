#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys
import time as _time
from functools import partial as _part
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QMenu, \
    QGroupBox, QPushButton, QWidget, QLabel, QInputDialog, QLineEdit, QDialog
from qtpy.QtCore import Qt, Signal, QThread
from siriushla.sirius_application import SiriusApplication
from siriushla import util
from siriushla.widgets import SiriusMainWindow


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

        self.AS_apps = QGroupBox('General')
        self.AS_apps.setLayout(self._create_as_layout())

        self.LI_apps = QGroupBox('Linac')
        self.LI_apps.setLayout(self._create_li_layout())

        self.TB_apps = QGroupBox('LTB')
        self.TB_apps.setLayout(self._create_section_layout('TB'))

        self.BO_apps = QGroupBox('Booster')
        self.BO_apps.setLayout(self._create_section_layout('BO'))

        self.TS_apps = QGroupBox('BTS')
        self.TS_apps.setLayout(self._create_section_layout('TS'))

        self.SI_apps = QGroupBox('Storage Ring')
        self.SI_apps.setLayout(self._create_section_layout('SI'))

        self.serv_apps = QGroupBox('Services')
        self.serv_apps.setLayout(self._create_serv_layout())

        self.layout.addWidget(
            QLabel('<h2>Sirius Launcher</h2>', self, alignment=Qt.AlignCenter))
        self.layout.addWidget(self.AS_apps)
        self.layout.addWidget(self.LI_apps)
        self.layout.addWidget(self.TB_apps)
        self.layout.addWidget(self.BO_apps)
        self.layout.addWidget(self.TS_apps)
        self.layout.addWidget(self.SI_apps)
        self.layout.addWidget(self.serv_apps)

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

        pscycle = QPushButton('PS Cycle', self)
        self.connect_newprocess(pscycle, 'sirius-hla-as-ps-cycle.py')

        psdiag = QPushButton('PS Diag', self)
        self.connect_newprocess(psdiag, 'sirius-hla-as-ps-diag.py')

        pstest = QPushButton('PS Test', self)
        self.connect_newprocess(pstest, 'sirius-hla-as-ps-test.py')

        psmonitor = QPushButton('PS Monitor', self)
        self.connect_newprocess(psmonitor, 'sirius-hla-as-ps-monitor.py')

        energy_button = QPushButton('Energy Button', self)
        self.connect_newprocess(
            energy_button, 'sirius-hla-as-ap-energybutton.py')

        offconv = QPushButton('Offline Converter', self)
        self.connect_newprocess(offconv, 'sirius-hla-as-ap-magoffconv.py')

        lay = QGridLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(operation, 0, 0)
        lay.addWidget(injection, 0, 1)
        lay.addWidget(timing, 0, 2)
        lay.addWidget(pscycle, 1, 0)
        lay.addWidget(pstest, 1, 1)
        lay.addWidget(psdiag, 1, 2)
        lay.addWidget(psmonitor, 1, 3)
        lay.addWidget(energy_button, 1, 4)
        lay.addWidget(offconv, 1, 5)
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

        # pvsconfmgr = QPushButton('PVs Configs')
        # self.connect_newprocess(pvsconfmgr, 'sirius-hla-as-ap-pvsconfigs.py')
        pvssave = QPushButton('Save Config')
        self.connect_newprocess(
            pvssave, 'sirius-hla-as-ap-pvsconfigs-save.py')
        pvsload = QPushButton('Load Config')
        self.connect_newprocess(
            pvsload, 'sirius-hla-as-ap-pvsconfigs-load.py')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(servconf)
        # lay.addWidget(pvsconfmgr)
        lay.addWidget(pvssave)
        lay.addWidget(pvsload)
        return lay

    def _create_li_layout(self):
        LI_launcher = QPushButton('Linac launcher', self)
        util.connect_newprocess(LI_launcher, 'sirius-hla-li-launcher.sh')

        energy = QPushButton('Energy Meas', self)
        self.connect_newprocess(energy, 'sirius-hla-li-ap-energy.py')

        emit = QPushButton('Emittance Meas', self)
        self.connect_newprocess(emit, 'sirius-hla-li-ap-emittance.py')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(LI_launcher)
        lay.addWidget(energy)
        lay.addWidget(emit)
        return lay

    def _create_section_layout(self, sec):
        sec = sec.lower()

        if sec in {'tb', 'ts'}:
            launcher = QPushButton('Main', self)
            self.connect_newprocess(launcher,
                                    'sirius-hla-'+sec+'-ap-control.py')

        PS = self._set_psma_menu(sec, dis='ps')
        MA = self._set_psma_menu(sec, dis='ma')

        PM = QPushButton('Pulsed Magnets', self)
        self.connect_newprocess(PM, 'sirius-hla-'+sec+'-pm-control.py')

        SOFB = QPushButton('SOFB', self)
        self.connect_newprocess(SOFB, 'sirius-hla-'+sec+'-ap-sofb.py')

        if sec in {'tb', 'ts'}:
            PosAng = QPushButton('PosAng', self)
            self.connect_newprocess(PosAng, 'sirius-hla-'+sec+'-ap-posang.py')

            ICTs = QPushButton('ICTs', self)
            self.connect_newprocess(ICTs, 'sirius-hla-'+sec+'-di-icts.py')

        if 'tb' in sec:
            Slits = QPushButton('Slits', self)
            self.connect_newprocess(Slits, 'sirius-hla-tb-di-slits.py')

            Emittance = QPushButton('Emittance Meas', self)
            self.connect_newprocess(Emittance, 'sirius-hla-tb-ap-emittance.py')

        BPMs = self._set_bpm_menu(sec)

        if 'si' not in sec:
            Scrns = QPushButton('Screens', self)
            self.connect_newprocess(Scrns,
                                    ['sirius-hla-as-di-scrn.py', sec.upper()])

        if sec in {'bo', 'si'}:
            CurrLT = QPushButton('Current and Lifetime', self)
            self.connect_newprocess(CurrLT, 'sirius-hla-'+sec+'-ap-currlt.py')

            TuneCorr = QPushButton('Tune Correction', self)
            self.connect_newprocess(TuneCorr,
                                    'sirius-hla-'+sec+'-ap-tunecorr.py')

            ChromCorr = QPushButton('Chromaticity Correction', self)
            self.connect_newprocess(ChromCorr,
                                    'sirius-hla-'+sec+'-ap-chromcorr.py')

        if 'bo' in sec:
            Ramp = QPushButton('Ramp', self)
            self.connect_newprocess(Ramp, 'sirius-hla-bo-ap-ramp.py')

        glay = QGridLayout()
        glay.setVerticalSpacing(15)
        glay.setAlignment(Qt.AlignLeft)
        glay.addWidget(PS, 1, 0)
        glay.addWidget(MA, 1, 1)
        glay.addWidget(PM, 1, 2)
        glay.addWidget(SOFB, 2, 0)
        glay.addWidget(BPMs, 3, 0)
        if 'si' not in sec:
            glay.addWidget(Scrns, 3, 1)
        if sec in {'tb', 'ts'}:
            glay.addWidget(launcher, 0, 0)
            glay.addWidget(PosAng, 2, 1)
            glay.addWidget(ICTs, 3, 2)
        if 'tb' in sec:
            glay.addWidget(Emittance, 2, 2)
            glay.addWidget(Slits, 3, 3)
        if sec in {'bo', 'si'}:
            glay.addWidget(CurrLT, 2, 1)
            glay.addWidget(TuneCorr, 2, 2)
            glay.addWidget(ChromCorr, 2, 3)
        if 'bo' in sec:
            glay.addWidget(Ramp, 2, 4)

        return glay

    def _set_bpm_menu(self, sec):
        cmd = ['sirius-hla-as-di-bpm.py', sec, '-w']
        menu = QMenu(self)
        action = menu.addAction('Summary')
        self.connect_newprocess(action, cmd + ['Summary', ])
        typs = ('Single Pass', 'Multi Turn')
        acts = ('SPass', 'MTurn')
        for typ, act in zip(typs, acts):
            action = menu.addAction(typ)
            if sec == 'bo':
                menu2 = QMenu(self)
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
                self.connect_newprocess(action, cmd + [act, ])
        bpm = QPushButton('BPMs', self)
        bpm.setMenu(menu)
        return bpm

    def _set_psma_menu(self, sec, dis='ps'):
        scr = 'sirius-hla-' + sec + '-' + dis + '-control.py'
        menu = QMenu(self)

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

        but = QPushButton('Magnets' if dis == 'ma' else 'Power Supplies', self)
        but.setMenu(menu)
        return but


if __name__ == "__main__":

    app = SiriusApplication()
    app.open_window(ControlApplication)
    sys.exit(app.exec_())
