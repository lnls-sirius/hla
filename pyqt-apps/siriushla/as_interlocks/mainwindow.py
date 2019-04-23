"""Control of EVG Timing Device."""

from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, \
    QGridLayout, QGroupBox, QLabel
from pydm.widgets import PyDMEnumComboBox, PyDMPushButton
from siriuspy.search import LLTimeSearch, HLTimeSearch
from siriushla.widgets import SiriusMainWindow, PyDMStateButton, \
    SiriusLedAlert, PyDMLedMultiChannel, PyDMLed


class Interlocks(SiriusMainWindow):

    def __init__(self, parent=None, prefix=''):
        super().__init__(parent)
        self.prefix = prefix
        self.setupui()

    def setupui(self):
        mainwid = QWidget(self)
        self.setCentralWidget(mainwid)
        self.setWindowTitle('Inter')
        gridlayout = QGridLayout(mainwid)
        gridlayout.setHorizontalSpacing(20)
        gridlayout.setVerticalSpacing(20)

        tiintlk = self.set_timing_interlocks()
        gridlayout.addWidget(tiintlk, 0, 0)

    def set_timing_interlocks(self):

        wid = QWidget(self.centralWidget())
        grid = QGridLayout(wid)
        grid.setHorizontalSpacing(50)
        lab = QLabel('<h2>Timing Interlocks<h2>', alignment=Qt.AlignCenter)
        grid.addWidget(lab, 0, 0, 1, 2)
        trigs = HLTimeSearch.get_hl_triggers()
        trigs = [tr for tr in trigs if HLTimeSearch.has_bypass_interlock(tr)]
        grid1 = self._group_timing(wid, trigs[:len(trigs)//2])
        grid2 = self._group_timing(wid, trigs[len(trigs)//2:])
        grid.addLayout(grid1, 1, 0, alignment=Qt.AlignTop)
        grid.addLayout(grid2, 1, 1, alignment=Qt.AlignTop)
        return wid

    def _group_timing(self, wid, trigs):
        colors = [PyDMLed.LightGreen, PyDMLed.Red]

        grd = QGridLayout()
        dic = {'alignment': Qt.AlignCenter}
        grd.addWidget(QLabel('<b>Trigger<b>', **dic), 0, 0)
        grd.addWidget(QLabel('<b>Status<b>', **dic), 0, 1)
        grd.addWidget(QLabel('<b>ByPass<b>', **dic), 0, 2)
        grd.addWidget(QLabel('<b>Latch<b>', **dic), 0, 3)
        for i, trig in enumerate(trigs, 1):
            ltr = HLTimeSearch.get_ll_trigger_names(trig)[0]
            ipv = ltr.substitute(propty='Intlk-Mon', prefix=self.prefix)
            spv = trig.substitute(propty='Status-Mon', prefix=self.prefix)
            bpv = trig.substitute(
                propty='ByPassIntlk-Sel', prefix=self.prefix)
            ch2v = {
                spv: {'value': 0, 'bit': 9},
                ipv: {'value': 5, 'comp': 'ne'}}

            grd.addWidget(QLabel(trig, wid), i, 0)
            grd.addWidget(PyDMLedMultiChannel(wid, channels2values=ch2v), i, 1)
            grd.addWidget(StateButton(wid, init_channel=bpv), i, 2)
            ch2v[spv]['bit'] = 10
            grd.addWidget(PyDMLedMultiChannel(wid, channels2values=ch2v), i, 3)
        return grd


class StateButton(PyDMPushButton):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._alarm_sensitive_border = True

    def value_changed(self, new_val):
        super().value_changed(new_val)
        if new_val is None:
            return
        elif new_val:
            self.setStyleSheet('color: black;')
        else:
            self.setStyleSheet('background-color: blue; color: white;')
        if self.enum_strings is not None:
            self.setText(self.enum_strings[new_val])
        self._pressValue = not new_val


if __name__ == '__main__':
    """Run Example."""
    import sys as _sys
    from siriuspy.envars import vaca_prefix as PREFIX
    from siriushla.sirius_application import SiriusApplication
    app = SiriusApplication()
    inter = Interlocks(prefix=PREFIX)
    inter.show()
    _sys.exit(app.exec_())
