"""Define Controllers for the orbits displayed in the graphic."""

from qtpy.QtWidgets import QLabel, QGroupBox, QFormLayout, QVBoxLayout, \
    QHBoxLayout, QGridLayout

from ...widgets import SiriusLabel
from . import BaseWidget


class DriveControl(BaseWidget):
    """."""

    def __init__(self, parent, device, prefix='', acc='SI'):
        """."""
        super().__init__(parent, device, prefix=prefix, acc=acc)
        self.setupui()

    def setupui(self):
        """."""
        self.setLayout(QGridLayout())
        ctrls = self._get_controls_widget(self)
        self.layout().addWidget(ctrls, 0, 0)

    def _get_controls_widget(self, parent):
        gpbx = QGroupBox('Drive Controls', parent)
        gpbx_lay = QVBoxLayout(gpbx)

        fbl = QFormLayout()
        fbl.setHorizontalSpacing(9)
        gpbx_lay.addLayout(fbl)

        lbl = QLabel('State', gpbx)
        wid = self.create_pair_butled(gpbx, 'DriveState')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Type', gpbx)
        wid = self.create_pair_sel(gpbx, 'DriveType')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Freq. Divisor', gpbx)
        wid = self.create_pair(gpbx, 'DriveFreqDivisor')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Number of Cycles', gpbx)
        wid = self.create_pair(gpbx, 'DriveNrCycles')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Amplitude [urad]', gpbx)
        wid = self.create_pair(gpbx, 'DriveAmplitude')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Phase [°]', gpbx)
        wid = self.create_pair(gpbx, 'DrivePhase')
        fbl.addRow(lbl, wid)
        lbl = QLabel('Corrector Index', gpbx)
        wid = self.create_pair(gpbx, 'DriveCorrIndex')
        fbl.addRow(lbl, wid)
        lbl = QLabel('BPM Index', gpbx)
        wid = self.create_pair(gpbx, 'DriveBPMIndex')
        fbl.addRow(lbl, wid)

        hlay = QHBoxLayout()
        hlay.addWidget(QLabel('Frequency [Hz]: '))
        hlay.addWidget(SiriusLabel(
            self, self.devpref.substitute(propty='DriveFrequency-Mon')))
        hlay.addStretch()
        hlay.addWidget(QLabel('Duration [s]: '))
        hlay.addWidget(SiriusLabel(
            self, self.devpref.substitute(propty='DriveDuration-Mon')))
        gpbx_lay.addLayout(hlay)
        return gpbx
