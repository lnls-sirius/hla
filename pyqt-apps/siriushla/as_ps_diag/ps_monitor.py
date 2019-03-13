"""Interface to handle general status."""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QLabel, \
    QFormLayout, QHBoxLayout, QGridLayout

from siriuspy.envars import vaca_prefix
from siriuspy.csdevice.pwrsupply import Const as _PSCons
from siriuspy.search.ma_search import MASearch

from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, \
    PyDMLedMultiChannel


LINAC_PS = [
    'LA-CN:H1MLPS-1', 'LA-CN:H1MLPS-2', 'LA-CN:H1MLPS-3', 'LA-CN:H1MLPS-4',
    'LA-CN:H1SCPS-1', 'LA-CN:H1SCPS-2', 'LA-CN:H1SCPS-3', 'LA-CN:H1SCPS-4',
    'LA-CN:H1LCPS-1', 'LA-CN:H1LCPS-2', 'LA-CN:H1LCPS-3', 'LA-CN:H1LCPS-4',
    'LA-CN:H1LCPS-5', 'LA-CN:H1LCPS-6', 'LA-CN:H1LCPS-7', 'LA-CN:H1LCPS-8',
    'LA-CN:H1LCPS-9', 'LA-CN:H1LCPS-10',
    'LA-CN:H1SLPS-1', 'LA-CN:H1SLPS-2', 'LA-CN:H1SLPS-3',
    'LA-CN:H1SLPS-4', 'LA-CN:H1SLPS-5', 'LA-CN:H1SLPS-6',
    'LA-CN:H1SLPS-7', 'LA-CN:H1SLPS-8', 'LA-CN:H1SLPS-9',
    'LA-CN:H1SLPS-10', 'LA-CN:H1SLPS-11', 'LA-CN:H1SLPS-12',
    'LA-CN:H1SLPS-13', 'LA-CN:H1SLPS-14', 'LA-CN:H1SLPS-15',
    'LA-CN:H1SLPS-16', 'LA-CN:H1SLPS-17', 'LA-CN:H1SLPS-18',
    'LA-CN:H1SLPS-19', 'LA-CN:H1SLPS-20', 'LA-CN:H1SLPS-21',
    'LA-CN:H1FQPS-1', 'LA-CN:H1FQPS-2', 'LA-CN:H1FQPS-3',
    'LA-CN:H1DQPS-1', 'LA-CN:H1DQPS-2',
    'LA-CN:H1RCPS-1', 'LA-CN:H1DPPS-1']


class PSMonitor(SiriusMainWindow):
    """Power Supplies Diagnosis."""

    def __init__(self, parent=None, prefix=vaca_prefix, sections=list()):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self._sections = sections
        self.setWindowTitle('Power Supplies Diagnosis')
        self._setupUi()

    def _setupUi(self):
        cw = QWidget()
        layout = QGridLayout()
        layout.setHorizontalSpacing(15)

        self._sec2label = {'LI': 'Linac',
                           'TB': 'LTB',
                           'BO': 'Booster',
                           'TS': 'BTS',
                           'SI': 'Storage Ring'}

        for sec, label in self._sec2label.items():
            if sec not in self._sections:
                continue
            if sec == 'LI':
                status = self._make_magnets_groupbox(label, LINAC_PS)
                layout.addWidget(status, 1, 0, 2, 1)
            elif sec == 'SI':
                subsectors = ['{:02}'.format(i) for i in range(1, 21)]
                i = 3
                for sub in subsectors:
                    manames = MASearch.get_manames(
                        filters={'sec': sec, 'sub': sub+'.*'})
                    status = self._make_magnets_groupbox(
                        label + ' - Subsecton '+sub, manames)
                    layout.addWidget(status, 1, i, 2, 1)
                    i += 1
            else:
                manames = MASearch.get_manames(filters={'sec': sec})
                status = self._make_magnets_groupbox(label, manames)
                if sec == 'TB':
                    layout.addWidget(status, 1, 1)
                elif sec == 'TS':
                    layout.addWidget(status, 2, 1)
                elif sec == 'BO':
                    layout.addWidget(status, 1, 2, 2, 1)
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _make_magnets_groupbox(self, group_name, manames):
        status = QGroupBox(group_name, self)
        status_lay = QFormLayout()
        status.setLayout(status_lay)
        lb_state = QLabel('<h4>State</h4>', self, alignment=Qt.AlignCenter)
        lb_state.setStyleSheet("""min-width:2.4em;max-width:2.4em;""")
        lb_intlk = QLabel('<h4>Intlk</h4>', self, alignment=Qt.AlignCenter)
        lb_intlk.setStyleSheet("""min-width:2.4em;max-width:2.4em;""")
        hbox_label = QHBoxLayout()
        hbox_label.addWidget(lb_state)
        hbox_label.addWidget(lb_intlk)
        status_lay.addRow('', hbox_label)
        for name in manames:
            pname = self._prefix + name
            lb = QLabel(name, self, alignment=Qt.AlignRight |
                        Qt.AlignVCenter)
            led_pwrstate = PyDMLedMultiChannel(
                self, {pname + ':setpwm': 16} if 'Linac' in group_name else
                {pname+':PwrState-Sts': _PSCons.PwrStateSts.On})
            led_pwrstate.setStyleSheet("""min-width:2em;max-width:2em;""")
            led_intlk = PyDMLedMultiChannel(
                self, {pname + ':interlock': [55, 'lt']}
                if 'Linac' in group_name else
                {pname+':IntlkSoft-Mon': 0, pname+':IntlkHard-Mon': 0})
            led_intlk.setStyleSheet("""min-width:2em;max-width:2em;""")
            hbox = QHBoxLayout()
            hbox.addWidget(led_pwrstate)
            hbox.addWidget(led_intlk)
            status_lay.addRow(lb, hbox)
        return status


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSMonitor()
    window.show()
    sys.exit(app.exec_())
