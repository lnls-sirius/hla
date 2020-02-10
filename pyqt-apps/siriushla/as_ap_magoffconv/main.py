"""Normalizer interface module."""

import re

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QComboBox, QLabel, \
    QDoubleSpinBox, QVBoxLayout, QHBoxLayout, QGridLayout, QSpacerItem, \
    QSizePolicy as QSzPlcy, QApplication, QMessageBox

from siriuspy.envars import VACA_PREFIX
from siriuspy.search import MASearch
from siriuspy.factory import NormalizerFactory
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow


Dipole = re.compile("^.*:MA-(B|Spect).*$")
Quadrupole = re.compile("^.*Fam:MA-Q.*$")
Sextupole = re.compile("^.*:MA-S.*$")
Corrector = re.compile("^.*:MA-(CH|CV|FCH|FCV).*$")
PulsedMagnet = re.compile("^.*:PM-.*$")
Multipole = re.compile("^.*:(MA)-(Q|S|QS|CH|CV|FCH|FCV).*$")
Trim = re.compile("^SI-.*[0-2][0-9].*:MA-Q(D|F|[1-4]).*$")


class MagOffConvApp(SiriusMainWindow):
    """Offline converter interface."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self._normalizer = None
        self._last_edited = None
        self._setupUi()
        self.setWindowTitle('Offline Strength/Current Converter')

    def _setupUi(self):
        # Layout to enter
        matype_label = QLabel('Choose a magnet: ', self)
        self._matype_cb = QComboBox(self)
        self._matype_items = MASearch.get_pwrsupply_manames()
        self._matype_cb.addItem('Select...')
        self._matype_cb.addItems(self._matype_items)
        self._matype_cb.setEditable(True)
        self._matype_cb.setMaxVisibleItems(10)
        self._matype_cb.currentIndexChanged.connect(
            self._fill_normalizer_layout)
        hlmatype = QHBoxLayout()
        hlmatype.setAlignment(Qt.AlignLeft)
        hlmatype.addWidget(matype_label)
        hlmatype.addWidget(self._matype_cb)

        # Layout to enter normalizer data
        self._lb_current = QLabel('Current [A]: ')
        lb_arrow = QLabel('↔', self, alignment=Qt.AlignCenter)
        lb_arrow.setStyleSheet('min-width:1.2em; max-width:1.2em;')
        self._lb_strength = QLabel('Strength: ')
        self._lb_energy = QLabel('Dipole Energy [GeV]: ')
        self._lb_energy.setVisible(False)
        self._lb_quadfam_kl = QLabel('Family KL [1/m]: ')
        self._lb_quadfam_kl.setVisible(False)

        for name in ['_sb_current', '_sb_strength',
                     '_sb_energy', '_sb_quadfam_kl']:
            setattr(self, name, MyDoubleSpinBox())
            sb = getattr(self, name)
            sb.setObjectName(name)
            sb.setValue(0)
            sb.setMinimum(-100000)
            sb.setMaximum(100000)
            sb.setDecimals(4)
            sb.setStyleSheet("min-width:8em; max-width:8em;")
            sb.editingFinished.connect(self._update_inputs)
            if name in ['_sb_current', '_sb_strength']:
                sb.setEnabled(False)
            else:
                sb.setVisible(False)

        norm_lay = QGridLayout()
        norm_lay.setAlignment(Qt.AlignLeft)
        norm_lay.setHorizontalSpacing(5)
        norm_lay.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 0)
        norm_lay.addWidget(self._lb_current, 0, 1)
        norm_lay.addWidget(self._sb_current, 1, 1)
        norm_lay.addWidget(lb_arrow, 0, 2, 2, 1)
        norm_lay.addWidget(self._lb_strength, 0, 3)
        norm_lay.addWidget(self._sb_strength, 1, 3)
        norm_lay.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 4)
        norm_lay.addWidget(self._lb_energy, 0, 5)
        norm_lay.addWidget(self._sb_energy, 1, 5)
        norm_lay.addItem(
            QSpacerItem(15, 1, QSzPlcy.Fixed, QSzPlcy.Ignored), 1, 6)
        norm_lay.addWidget(self._lb_quadfam_kl, 0, 7)
        norm_lay.addWidget(self._sb_quadfam_kl, 1, 7)
        self.norm_gb = QGroupBox('', self)
        self.norm_gb.setLayout(norm_lay)

        # General layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(
            QLabel('<h2>Offline Strength/Current Converter</h2>',
                   self, alignment=Qt.AlignCenter))
        layout.addLayout(hlmatype)
        layout.addWidget(self.norm_gb)
        cw = QWidget(self)
        cw.setObjectName('central_widget')
        cw.setStyleSheet("""#central_widget{min-width:42em;}""")
        cw.setLayout(layout)
        self.setCentralWidget(cw)
        self.setFocusPolicy(Qt.StrongFocus)

    def _fill_normalizer_layout(self, index):
        text = self.sender().currentText()
        if text not in self._matype_items:
            QMessageBox.critical(self, 'Error', 'Enter a valid magnet name!')
            self._sb_current.setEnabled(False)
            self._sb_strength.setEnabled(False)
            self._lb_energy.setVisible(False)
            self._sb_energy.setVisible(False)
            self._lb_quadfam_kl.setVisible(False)
            self._sb_quadfam_kl.setVisible(False)
            return

        # Reset all fields
        self._sb_current.setValue(0)
        self._sb_strength.setValue(0)
        self._sb_energy.setValue(0)
        self._sb_quadfam_kl.setValue(0)

        # Create normalizer and update limits if text is a valid magnet
        if index != 0:
            self._create_normalizer(text)

        # Update interface
        enbl_current = False
        enbl_strength = False
        show_energy = False
        show_quadfam_kl = False
        if Dipole.match(text):
            enbl_current = True
            enbl_strength = True
        elif Trim.match(text):
            enbl_current = True
            enbl_strength = True
            show_energy = True
            show_quadfam_kl = True
        elif Multipole.match(text) or PulsedMagnet.match(text):
            enbl_current = True
            enbl_strength = True
            show_energy = True
        self._sb_current.setEnabled(enbl_current)
        self._sb_strength.setEnabled(enbl_strength)
        self._lb_energy.setVisible(show_energy)
        self._sb_energy.setVisible(show_energy)
        self._lb_quadfam_kl.setVisible(show_quadfam_kl)
        self._sb_quadfam_kl.setVisible(show_quadfam_kl)

        # Update Strength label
        if Dipole.match(text):
            text_strength = 'Energy [GeV]: '
        elif Quadrupole.match(text):
            text_strength = 'KL [1/m]: '
        elif Trim.match(text):
            text_strength = 'KL (Fam + Trim) [1/m]: '
        elif Sextupole.match(text):
            text_strength = 'SL [1/m²]: '
        elif Corrector.match(text):
            text_strength = 'Kick [urad]: '
        elif PulsedMagnet.match(text):
            text_strength = 'Kick [mrad]: '
        else:
            text_strength = 'Strength: '
        self._lb_strength.setText(text_strength)

        # update limits, if necessary
        self._update_inputs()

    def _create_normalizer(self, maname):
        self._normalizer = NormalizerFactory.create(maname)

    def _update_inputs(self):
        sender = self.sender().objectName()
        if 'strength' in sender:
            self._last_edited = 's'
        elif 'current' in sender:
            self._last_edited = 'c'

        strength = self._sb_strength.value()
        current = self._sb_current.value()
        quadfam_kl = None
        energy = None
        if self._sb_quadfam_kl.isVisible():
            quadfam_kl = self._sb_quadfam_kl.value()
        if self._sb_energy.isVisible():
            energy = self._sb_energy.value()

        if self._last_edited == 's':
            current = self._conv_strength2curr(strength, energy, quadfam_kl)
            self._sb_current.setValue(current)
        else:
            strength = self._conv_curr2strength(current, energy, quadfam_kl)
            self._sb_strength.setValue(strength)

    def _conv_curr2strength(self, current, energy=None, quadfam_kl=None):
        if quadfam_kl is not None:
            strength = self._normalizer.conv_current_2_strength(
                currents=current, strengths_dipole=energy,
                strengths_family=quadfam_kl)
        elif energy is not None:
            strength = self._normalizer.conv_current_2_strength(
                currents=current, strengths_dipole=energy)
        else:
            strength = self._normalizer.conv_current_2_strength(
                currents=current)
        return strength

    def _conv_strength2curr(self, strength, energy=None, quadfam_kl=None):
        if quadfam_kl is not None:
            current = self._normalizer.conv_strength_2_current(
                strengths=strength, strengths_dipole=energy,
                strengths_family=quadfam_kl)
        elif energy is not None:
            current = self._normalizer.conv_strength_2_current(
                strengths=strength, strengths_dipole=energy)
        else:
            current = self._normalizer.conv_strength_2_current(
                strengths=strength)
        return current


class MyDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.step_exponent = 0

    def keyPressEvent(self, ev):
        app = QApplication.instance()
        ctrl_hold = app.queryKeyboardModifiers() == Qt.ControlModifier
        if ctrl_hold and (ev.key() in (Qt.Key_Left, Qt.Key_Right)):
            self.step_exponent += 1 if ev.key() == Qt.Key_Left else -1
            self.step_exponent = max(-self.decimals(), self.step_exponent)
            self.setSingleStep(10 ** self.step_exponent)
        else:
            super().keyPressEvent(ev)


if __name__ == '__main__':
    """Run Example."""
    import sys

    app = SiriusApplication()
    w = MagOffConvApp(prefix=VACA_PREFIX)
    w.show()
    sys.exit(app.exec_())
