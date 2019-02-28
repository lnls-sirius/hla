#!/usr/bin/env python-sirius

"""Mock application launcher."""

import sys

from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, \
                           QGroupBox, QPushButton, QWidget, QLabel
from qtpy.QtCore import Qt
from siriushla.sirius_application import SiriusApplication
from siriushla import util
from siriushla.widgets import SiriusMainWindow


class ControlApplication(SiriusMainWindow):
    """Main launcher."""

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.setWindowTitle("AS Launcher")
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)

        self.AS_apps = QGroupBox('General')
        self.AS_apps.setLayout(self._create_as_layout())

        self.LI_apps = QGroupBox('Linac')
        self.LI_apps.setLayout(self._create_LI_layout())

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
                min-width:12em; max-width:12em;
                min-height:2em; max-height:2em;
            }""")

        self.setCentralWidget(self.main_widget)

    def _create_as_layout(self):
        injection = QPushButton('Injection', self)
        util.connect_newprocess(injection, 'sirius-hla-as-ap-injection.py')

        timing = QPushButton('Timing', self)
        util.connect_newprocess(timing, 'sirius-hla-as-ti-control.py')

        pscycle = QPushButton('PS Cycle', self)
        util.connect_newprocess(pscycle, 'sirius-hla-as-ps-cycle.py')

        pstest = QPushButton('PS Test', self)
        util.connect_newprocess(pstest, 'sirius-hla-as-ps-test.py')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(injection)
        lay.addWidget(timing)
        lay.addWidget(pscycle)
        lay.addWidget(pstest)
        return lay

    def _create_serv_layout(self):
        servconf = QPushButton('Configurations Server')
        util.connect_newprocess(servconf, 'sirius-hla-as-ap-servconf.py')

        pvsconfmgr = QPushButton('PVs Configuration Manager')
        util.connect_newprocess(pvsconfmgr, 'sirius-hla-as-ap-pvsconfmgr.py')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(servconf)
        lay.addWidget(pvsconfmgr)
        return lay

    def _create_LI_layout(self):
        LI_launcher = QPushButton('Linac launcher', self)
        util.connect_newprocess(LI_launcher, 'sirius-hla-li-launcher.sh')

        energy = QPushButton('Energy Meas', self)
        util.connect_newprocess(energy, 'sirius-hla-li-ap-energy.py')

        emit = QPushButton('Emittance Meas', self)
        util.connect_newprocess(emit, 'sirius-hla-li-ap-emittance.py')

        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignLeft)
        lay.addWidget(LI_launcher)
        lay.addWidget(energy)
        lay.addWidget(emit)
        return lay

    def _create_section_layout(self, sec):
        sec = sec.lower()

        if 'tb' in sec or 'ts' in sec:
            launcher = QPushButton('Main', self)
            util.connect_newprocess(launcher,
                                    'sirius-hla-'+sec+'-ap-control.py')

        PS = QPushButton('Power Supplies', self)
        util.connect_newprocess(PS, 'sirius-hla-'+sec+'-ps-control.py')

        MA = QPushButton('Magnets', self)
        util.connect_newprocess(MA, 'sirius-hla-'+sec+'-ma-control.py')

        PM = QPushButton('Pulsed Magnets', self)
        util.connect_newprocess(PM, 'sirius-hla-'+sec+'-pm-control.py')

        SOFB = QPushButton('SOFB', self)
        util.connect_newprocess(SOFB, 'sirius-hla-'+sec+'-ap-sofb.py')

        if 'tb' in sec or 'ts' in sec:
            PosAng = QPushButton('PosAng', self)
            util.connect_newprocess(PosAng, 'sirius-hla-'+sec+'-ap-posang.py')

            ICTs = QPushButton('ICTs', self)
            util.connect_newprocess(ICTs, 'sirius-hla-'+sec+'-di-icts.py')

        if 'tb' in sec:
            Slits = QPushButton('Slits', self)
            util.connect_newprocess(Slits, 'sirius-hla-tb-di-slits.py')

            Emittance = QPushButton('Emittance Meas', self)
            util.connect_newprocess(Emittance, 'sirius-hla-tb-ap-emittance.py')

        BPMs = QPushButton('BPMs', self)
        util.connect_newprocess(BPMs, ['sirius-hla-as-di-bpm.py', sec.upper()])

        if 'si' not in sec:
            Scrns = QPushButton('Screens', self)
            util.connect_newprocess(Scrns,
                                    ['sirius-hla-as-di-scrn.py', sec.upper()])

        if 'bo' in sec or 'si' in sec:
            CurrLT = QPushButton('Current and Lifetime', self)
            util.connect_newprocess(CurrLT, 'sirius-hla-'+sec+'-ap-currlt.py')

            TuneCorr = QPushButton('Tune Correction', self)
            util.connect_newprocess(TuneCorr,
                                    'sirius-hla-'+sec+'-ap-tunecorr.py')

            ChromCorr = QPushButton('Chromaticity Correction', self)
            util.connect_newprocess(ChromCorr,
                                    'sirius-hla-'+sec+'-ap-chromcorr.py')

        if 'bo' in sec:
            Ramp = QPushButton('Ramp', self)
            util.connect_newprocess(Ramp, 'sirius-hla-bo-ap-ramp.py')

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
        if 'tb' in sec or 'ts' in sec:
            glay.addWidget(launcher, 0, 0)
            glay.addWidget(PosAng, 2, 1)
            glay.addWidget(ICTs, 3, 2)
        if 'tb' in sec:
            glay.addWidget(Emittance, 2, 2)
            glay.addWidget(Slits, 3, 3)
        if 'bo' in sec or 'si' in sec:
            glay.addWidget(CurrLT, 2, 1)
            glay.addWidget(TuneCorr, 2, 2)
            glay.addWidget(ChromCorr, 2, 3)
        if 'bo' in sec:
            glay.addWidget(Ramp, 2, 4)

        return glay


if __name__ == "__main__":

    app = SiriusApplication()

    window = ControlApplication()
    window.show()
    sys.exit(app.exec_())
