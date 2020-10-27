"""Interface to handle power supply diagnostic."""

import re as _re
import logging as _log
from datetime import datetime as _datetime
from functools import partial as _partial

from pcaspy import Severity as _Sev

import numpy as _np

from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtCore import Qt, Slot, Signal
from qtpy.QtWidgets import QWidget, QLabel, QPushButton, \
    QGridLayout, QSpacerItem, QSizePolicy as QSzPlcy, QLineEdit, \
    QTreeView, QItemDelegate, QHeaderView, QAbstractItemView, \
    QStackedLayout, QRadioButton
import qtawesome as qta

from pydm.widgets.base import PyDMWidget

from siriuspy.envars import VACA_PREFIX
from siriuspy.pwrsupply.csdev import Const as _PSConst, \
    ETypes as _PSEnums, PS_LI_INTLK_THRS as _PS_LI_INTLK
from siriuspy.search import PSSearch
from siriuspy.namesys import SiriusPVName

from siriushla.util import run_newprocess as _run_newprocess, \
    get_appropriate_color as _get_appropriate_color
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow, SiriusConnectionSignal, \
    PyDMLedMultiChannel, PyDMLed, PyDMLedMultiConnection, QLed

from siriushla.as_ps_diag.util import asps2filters, lips2filters, sips2filters


class PSDiag(SiriusMainWindow):
    """Power Supply Diagnostic."""

    def __init__(self, parent=None, prefix=VACA_PREFIX):
        """Init."""
        super().__init__(parent)
        self._prefix = prefix
        self.setWindowTitle('PS Diagnostics')
        self.setObjectName('ASApp')
        cor = _get_appropriate_color(section='AS')
        self.setWindowIcon(qta.icon('mdi.stethoscope', color=cor))
        self._setupUi()
        self._initialized = False

    def _setupUi(self):
        # Leds Panel
        cw = QWidget(self)
        panel = QWidget(cw)
        panel_lay = QGridLayout()
        panel_lay.setVerticalSpacing(0)
        panel_lay.setHorizontalSpacing(5)
        panel.setLayout(panel_lay)

        # # Leds Header
        for i, lab in enumerate([
                '', 'PS\nConn?', 'Power\nState', 'Interlock',
                'OpMode\nSlowRef?', 'Current\nDiff']):
            label = QLabel(lab, panel, alignment=Qt.AlignCenter)
            label.setStyleSheet('min-width:3.4em; max-width:3.4em;')
            panel_lay.addWidget(label, 0, i)

        # # Leds panel
        _on = _PSConst.PwrStateSts.On
        _slowref = _PSConst.States.SlowRef
        _rmpwfm = _PSConst.States.RmpWfm
        i = 2
        for sec in ['LI', 'TB', 'BO', 'TS', 'SI']:
            seclabel = QLabel('<h3>'+sec+'</h3>', panel)
            panel_lay.addWidget(seclabel, i, 0)
            i += 1
            if sec == 'LI':
                for label, filt in lips2filters.items():
                    ps_label = QLabel(
                        label, panel,
                        alignment=Qt.AlignRight | Qt.AlignVCenter)
                    psnames = PSSearch.get_psnames(filters=filt)
                    ps_ch2vals = dict()
                    intlk_ch2vals = dict()
                    conn_chs = list()
                    for name in psnames:
                        pname = self._prefix + name
                        conn_chs.append(pname+':PwrState-Sts')
                        ps_ch2vals[pname + ':PwrState-Sts'] = 1
                        intlk_ch2vals[pname + ':StatusIntlk-Mon'] = \
                            {'value': _PS_LI_INTLK, 'comp': 'lt'}

                    f = 'LI-.*:PS-'+filt['dev']
                    conn_led = MyLedMultiConnection(
                        filters=f, parent=panel, channels=conn_chs)
                    ps_led = MyLedMultiChannel(
                        filters=f, parent=panel, channels2values=ps_ch2vals)
                    intlk_led = MyLedMultiChannel(
                        filters=f, parent=panel, channels2values=intlk_ch2vals)

                    suf = sec+filt['dev'].strip('.*')+'_led'
                    conn_led.setObjectName('conn' + suf)
                    ps_led.setObjectName('ps' + suf)
                    intlk_led.setObjectName('intlk' + suf)

                    panel_lay.addWidget(ps_label, i, 0)
                    panel_lay.addWidget(conn_led, i, 1)
                    panel_lay.addWidget(ps_led, i, 2)
                    panel_lay.addWidget(intlk_led, i, 3)
                    i += 1
            else:
                l2f = sips2filters if sec == 'SI' else asps2filters
                for label, filt in l2f.items():
                    filt['sec'] = sec
                    psnames = PSSearch.get_psnames(filters=filt)
                    if not psnames:
                        continue
                    psconn_chs = list()
                    ps_ch2vals = dict()
                    intlk_ch2vals = dict()
                    opm_ch2vals = dict()
                    diff_ch2vlas = dict()
                    for name in psnames:
                        pname = self._prefix + name
                        ps_ch2vals[pname+':PwrState-Sts'] = _on
                        if name.dis == 'PS':
                            psconn_chs.append(pname+':Version-Cte')
                            intlk_ch2vals[pname+':IntlkSoft-Mon'] = 0
                            intlk_ch2vals[pname+':IntlkHard-Mon'] = 0
                            if sec == 'BO':
                                opm_ch2vals[pname+':OpMode-Sts'] = {
                                    'value': [_slowref, _rmpwfm], 'comp': 'in'}
                            else:
                                opm_ch2vals[pname+':OpMode-Sts'] = _slowref
                            diff_ch2vlas[pname+':DiagStatus-Mon'] = \
                                {'value': 0, 'bit': 5}
                        elif name.dis == 'PU':
                            psconn_chs.append(pname+':PwrState-Sts')
                            intlkcount = 7 if 'Sept' in name.dev else 8
                            for idx in range(1, intlkcount+1):
                                sidx = str(idx)
                                intlk_ch2vals[pname+':Intlk'+sidx+'-Mon'] = 1

                    f = sec+'-'+filt['sub']+':'+psnames[0].dis+'-'+filt['dev']
                    ps_label = QLabel(
                        label, panel,
                        alignment=Qt.AlignRight | Qt.AlignVCenter)
                    psconn_led = MyLedMultiConnection(
                        filters=f, parent=panel, channels=psconn_chs)
                    ps_led = MyLedMultiChannel(
                        filters=f, parent=panel, channels2values=ps_ch2vals)
                    intlk_led = MyLedMultiChannel(
                        filters=f, parent=panel, channels2values=intlk_ch2vals)

                    suf = sec+filt['dev'].strip('.*')+'_led'
                    psconn_led.setObjectName('psconn' + suf)
                    ps_led.setObjectName('ps' + suf)
                    intlk_led.setObjectName('intlk' + suf)

                    panel_lay.addWidget(ps_label, i, 0)
                    panel_lay.addWidget(psconn_led, i, 1)
                    panel_lay.addWidget(ps_led, i, 2)
                    panel_lay.addWidget(intlk_led, i, 3)

                    if psnames[0].dis == 'PS':
                        opm_led = MyLedMultiChannel(
                            filters=f, parent=panel,
                            channels2values=opm_ch2vals)
                        opm_led.setOnColor(PyDMLed.LightGreen)
                        opm_led.setOffColor(PyDMLed.Yellow)
                        diff_led = MyLedMultiChannel(
                            filters=f, parent=panel,
                            channels2values=diff_ch2vlas)

                        opm_led.setObjectName('opm' + suf)
                        diff_led.setObjectName('diff' + suf)

                        panel_lay.addWidget(opm_led, i, 4)
                        panel_lay.addWidget(diff_led, i, 5)

                    i += 1
            panel_lay.addItem(QSpacerItem(1, 10, QSzPlcy.Ignored,
                              QSzPlcy.MinimumExpanding), i, 0)
            i += 1

        # Current State and Log Tables
        table_label2px = {
            'Date': 110,
            'Time': 85,
            'Type': 70,
            'PS Name': 145,
            'Property': 85,
            'Value': 120}

        channels = list()
        for ps in PSSearch.get_psnames(filters={'dis': 'PS'}):
            channels.append(self._prefix+ps+':DiagCurrentDiff-Mon')
            channels.append(self._prefix+ps+':OpMode-Sts')
        self._status = LogTable(cw, channels, table_label2px, is_status=True)
        self._status.setObjectName('status_table')
        self._status.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._status.updated.connect(self._filter_table)
        self._log = LogTable(cw, channels, table_label2px)
        self._log.setObjectName('log_table')
        self._log.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._tables_stack = QStackedLayout()
        self._tables_stack.addWidget(self._status)
        self._tables_stack.addWidget(self._log)

        self._rb_status = QRadioButton('Status', self)
        self._rb_status.setObjectName('rb_status')
        self._rb_status.setChecked(True)
        self._visible_table = self._status
        self._rb_status.toggled.connect(_partial(self._toggle_table, 0))
        self._rb_log = QRadioButton('Log', self)
        self._rb_log.setObjectName('rb_log')
        self._rb_log.toggled.connect(_partial(self._toggle_table, 1))

        for name, width in table_label2px.items():
            attr = '_search_'+name.replace(' ', '').lower()
            setattr(self, attr, QLineEdit())
            le = getattr(self, attr)
            le.setObjectName(name)
            le.setPlaceholderText(name + '...')
            le.editingFinished.connect(self._filter_table)
            width = str(width-1)
            if name == 'Value':
                le.setStyleSheet(
                    '#'+name+'{min-width:'+width+'px;}')
                le.setSizePolicy(QSzPlcy.Expanding, QSzPlcy.Maximum)
            else:
                le.setStyleSheet(
                    '#'+name+'{min-width:'+width+'px; max-width:'+width+'px;}')
                le.setSizePolicy(QSzPlcy.Maximum, QSzPlcy.Maximum)

        self._scrollup_pb = QPushButton('↟', cw)
        self._scrollup_pb.setObjectName('scrollup_pb')
        self._scrollup_pb.clicked.connect(self._arrange_table)

        self._scrolldown_pb = QPushButton('↡', cw)
        self._scrolldown_pb.setObjectName('scrolldown_pb')
        self._scrolldown_pb.clicked.connect(self._arrange_table)

        tables_lay = QGridLayout()
        tables_lay.setVerticalSpacing(2)
        tables_lay.setHorizontalSpacing(0)
        tables_lay.addWidget(self._search_date, 0, 0)
        tables_lay.addWidget(self._search_time, 0, 1)
        tables_lay.addWidget(self._search_type, 0, 2)
        tables_lay.addWidget(self._search_psname, 0, 3)
        tables_lay.addWidget(self._search_property, 0, 4)
        tables_lay.addWidget(self._search_value, 0, 5)
        tables_lay.addWidget(self._scrollup_pb, 0, 6, alignment=Qt.AlignRight)
        tables_lay.addLayout(self._tables_stack, 1, 0, 1, 7)
        tables_lay.addWidget(self._rb_status, 2, 0, alignment=Qt.AlignLeft)
        tables_lay.addWidget(self._rb_log, 2, 1, alignment=Qt.AlignLeft)
        tables_lay.addWidget(self._scrolldown_pb, 2, 6,
                             alignment=Qt.AlignRight)
        tables = QWidget(cw)
        tables.setObjectName('tables')
        tables.setLayout(tables_lay)

        # Connect signals
        for led in self.findChildren(QLed):
            led.shape = PyDMLed.ShapeMap.Round
            led.filterlog.connect(self._filter_table)
            led.warning.connect(self._log.add_log_slot)
            led.warning.connect(self._status.add_log_slot)
            led.normal.connect(self._status.remove_log_slot)

        # Layout
        window_title = QLabel('<h2>Power Supplies Diagnostics</h2>', cw,
                              alignment=Qt.AlignCenter)
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(5)
        layout.addWidget(window_title, 0, 0, 1, 2)
        layout.addWidget(panel, 1, 0)
        layout.addWidget(tables, 1, 1)

        cw.setStyleSheet("""
            #scrollup_pb, #scrolldown_pb{
                max-height: 1em;
                max-width: 0.7em;
                color: #464646;
            }
            QLineEdit{
                max-height: 1em;
            }
            #status_table, #log_table{
                border: 1px solid #bebebe;
            }
            #tables{
                min-width: 700px;
            }
            #rb_status, #rb_log{
                min-width: 5em;
                max-width: 5em;
                max-height: 1em;
            }""")
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def _arrange_table(self):
        text = self.sender().text()
        if '↟' in text:
            self._visible_table.scrollToTop()
        elif '↡' in text:
            self._visible_table.scrollToBottom()

    def _filter_table(self, text=''):
        # identify first user interaction
        if isinstance(self.sender(), (QLineEdit, QLed)):
            self._initialized = True
        # ignore initializing
        if not self._initialized:
            return
        # set led's filter
        if isinstance(self.sender(), QLed):
            self.blockSignals(True)
            self._search_psname.setText(text)
            self.blockSignals(False)

        # get search filters
        pats = list()
        date_txt = self._search_date.text()
        time_txt = self._search_time.text()
        logtype_txt = self._search_type.text()
        psname_txt = self._search_psname.text()
        property_txt = self._search_property.text()
        value_txt = self._search_value.text()
        try:
            if date_txt:
                pats.append([_re.compile(date_txt, _re.I), 0])
            if time_txt:
                pats.append([_re.compile(time_txt, _re.I), 1])
            if logtype_txt:
                pats.append([_re.compile(logtype_txt, _re.I), 2])
            if psname_txt:
                pats.append([_re.compile(psname_txt, _re.I), 3])
            if property_txt:
                pats.append([_re.compile(property_txt, _re.I), 4])
            if value_txt:
                pats.append([_re.compile(value_txt, _re.I), 5])
        except Exception:
            return

        m = self._visible_table.model()
        for row in range(m.rowCount()):
            for pat, col in pats:
                if not pat.search(m.data(m.index(row, col))):
                    self._visible_table.setRowHidden(
                        row, self._visible_table.rootIndex(), True)
                    break
            else:
                self._visible_table.setRowHidden(
                    row, self._visible_table.rootIndex(), False)

    def _toggle_table(self, i, toggle):
        if not toggle:
            return

        self._tables_stack.setCurrentIndex(i)
        if i == 0:
            self._log.updated.disconnect(self._filter_table)
            self._status.updated.connect(self._filter_table)
            self._visible_table = self._status
        else:
            self._status.updated.disconnect(self._filter_table)
            self._log.updated.connect(self._filter_table)
            self._visible_table = self._log
        self._filter_table()


class LogTable(QTreeView, PyDMWidget):
    """Log Table."""

    updated = Signal()

    def __init__(self, parent=None, channels=list(), label2width=dict(),
                 is_status=False):
        # QTableView.__init__(self, parent)
        QTreeView.__init__(self, parent)
        PyDMWidget.__init__(self)

        # setup table
        self._is_status = is_status
        self._date_fmt = ' %Y/%m/%d '
        self._time_fmt = ' %H:%M:%S '
        self.headerLabels = label2width.keys()
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(self.headerLabels)
        self.setModel(self._model)
        self.setUniformRowHeights(True)
        self.setHeader(QHeaderView(Qt.Horizontal))
        for idx, width in enumerate(label2width.values()):
            self.header().resizeSection(idx, width)
        self.header().resizeSections(QHeaderView.Fixed)
        self.header().setStretchLastSection(True)
        self.setSortingEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setItemDelegateForColumn(2, LogItemDelegate(self))
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setStyleSheet("gridline-color: #ffffff;")

        # set channels
        self.address2conn = dict()
        self.address2channels = dict()
        for address in channels:
            self.address2conn[address] = False
            channel = SiriusConnectionSignal(
                address=address,
                connection_slot=self.connection_changed,
                value_slot=self.value_changed,
                severity_slot=self.alarm_severity_changed)
            channel.connect()
            self.address2channels[address] = channel
            self._channels.append(channel)

    @Slot(bool)
    def connection_changed(self, conn):
        """Reimplement connection_changed to handle all channels."""
        address = self.sender().address
        self.address2conn[address] = conn
        allconn = True
        for conn in self.address2conn.values():
            allconn &= conn
        self.setState(allconn)
        self._connected = allconn

    def add_log_slot(self, updated):
        new_value = self._get_newitem_data(updated)
        if not new_value:
            return
        self.add_log(new_value)

    def add_log(self, new_value):
        if self._is_status:
            self.remove_log(new_value)

        datetime_now = _datetime.now()
        item_data = [QStandardItem(text) for text in (
            datetime_now.date().strftime(self._date_fmt),
            datetime_now.time().strftime(self._time_fmt),
            new_value['logtype'], new_value['psname'],
            new_value['propty'], new_value['value'])]
        for item in item_data:
            item.setTextAlignment(Qt.AlignCenter)

        self._model.insertRow(0, item_data)
        if self._model.rowCount() > 10000:
            self._model.removeRow(self._model.rowCount()-1)
        self.updated.emit()

    def remove_log_slot(self, updated):
        new_value = self._get_newitem_data(updated)
        if not new_value:
            return
        self.remove_log(new_value)

    def remove_log(self, new_value):
        for row in range(self._model.rowCount()):
            logtype = self._model.data(self._model.index(row, 2))
            if logtype != new_value['logtype']:
                continue
            psname = self._model.data(self._model.index(row, 3))
            if psname != new_value['psname']:
                continue
            propty = self._model.data(self._model.index(row, 4))
            if propty != new_value['propty']:
                continue
            self._model.removeRow(row)
        self.updated.emit()

    def alarm_severity_changed(self, new_alarm_severity):
        """Reimplement alarm_severity_changed."""
        if self.sender():
            pv_diff = SiriusPVName(self.sender().address)
            val_diff = self.address2channels[pv_diff].value

            pv_opmd = pv_diff.substitute(
                propty_name='OpMode', propty_suffix='Sts')
            val_opmd = self.address2channels[pv_opmd].value
            is_slowref = val_opmd == _PSConst.States.SlowRef

            new_value = {'logtype': 'WARN', 'psname': pv_diff.device_name,
                         'propty': pv_diff.propty_name, 'value': str(val_diff)}
            if new_alarm_severity in [_Sev.MINOR_ALARM, _Sev.MAJOR_ALARM] and \
                    is_slowref:
                self.add_log(new_value)
            elif self._is_status:
                self.remove_log(new_value)

            super().alarm_severity_changed(new_alarm_severity)

    def _get_newitem_data(self, updated):
        pv, value = updated
        pv = SiriusPVName(pv)
        if isinstance(value, _np.ndarray):
            _log.warning('PSDiag window received a numpy array to ' +
                         pv+' ('+str(value)+')!')
            return

        if value is None:
            return
        if 'conn' in self.sender().objectName():
            str_value = 'disconnected'
            logtype = 'DISCONN'
        elif pv.propty_name == 'PwrState':
            str_value = _PSEnums.PWRSTATE_STS[value]
            logtype = 'ERR'
        elif pv.propty_name == 'OpMode':
            str_value = _PSEnums.STATES[value]
            logtype = 'WARN'
        else:
            str_value = str(value)
            logtype = 'ERR'

        return {'logtype': logtype,
                'psname': pv.device_name,
                'propty': '' if logtype == 'DISCONN' else pv.propty_name,
                'value': str_value}

    def mouseDoubleClickEvent(self, ev):
        """Trigger open PS detail window."""
        idx = self.selectedIndexes()
        text = self._model.data(self._model.index(idx[0].row(), 3))
        text = SiriusPVName(text)
        if text.dis == 'PS':
            _run_newprocess(['sirius-hla-as-ps-detail.py', text])
        elif text.dis == 'PU':
            _run_newprocess(['sirius-hla-as-pu-detail.py', text])
        super().mouseDoubleClickEvent(ev)


class LogItemDelegate(QItemDelegate):
    """Log Item Delegate."""

    def paint(self, painter, option, index):
        """Paint."""
        logtype = self.parent().model().data(
            index.sibling(index.row(), 2))
        if logtype.upper() == 'WARN':
            painter.fillRect(option.rect, PyDMLed.Yellow)
        elif logtype.upper() == 'ERR':
            painter.fillRect(option.rect, PyDMLed.Red)
        elif logtype.upper() == 'DISCONN':
            painter.fillRect(option.rect, PyDMLed.Gray)

        QItemDelegate.paint(self, painter, option, index)


def create_led_class(type='multichannel'):
    if type == 'multichannel':
        led_class = PyDMLedMultiChannel
    else:
        led_class = PyDMLedMultiConnection

    class MyLed(led_class):

        filterlog = Signal(str)

        def __init__(self, filters, **kwargs):
            super().__init__(**kwargs)
            self.filter = filters

        def mouseDoubleClickEvent(self, ev):
            self.filterlog.emit(self.filter)

    return MyLed


MyLedMultiChannel = create_led_class('multichannel')
MyLedMultiConnection = create_led_class('multiconn')


if __name__ == '__main__':
    import sys

    app = SiriusApplication()
    window = PSDiag()
    window.show()
    sys.exit(app.exec_())
