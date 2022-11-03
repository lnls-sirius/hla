""" Basic functions """
import math as _math
import qtawesome as _qta
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, QGroupBox
from pydm.widgets.display_format import DisplayFormat as _DisplayFormat
from ..si_di_bbb.custom_widgets import MyScaleIndicator
from ..li_rf_llrf.chart import ChartWindow
from .. import util as _util
from ..widgets import SiriusLabel, PyDMLed, PyDMLedMultiChannel, \
    SiriusLineEdit, SiriusEnumComboBox, PyDMStateButton, SiriusLedAlert
from .util import COLORS, IPS_DETAILS, LEGEND
from .widgets import LedLegend, QGroupBoxButton, PyDMLedMultiIncosistencyDetector


class BaseFunctionsInterface():
    """ Export basic functions to the Vacuum windows """
    def getLayoutWidget(self, orient="G"):
        """ Get Widget with a layout inside """
        wid = QWidget()
        if orient == "G":
            lay = QGridLayout()
        elif orient == "H":
            lay = QHBoxLayout()
        else:
            lay = QVBoxLayout()
        wid.setLayout(lay)
        return wid, lay

    def getWidget(self, name, wid_type='button',
                  keep_unit=False, precision=True):
        """ Build and configure widgets used """
        pv_name = self.devpref + name
        if wid_type == 'led':
            if "ReadS.B4" in pv_name:
                led_type = 'alert'
            else:
                led_type = 'normal'
            widget = self.buildLed(pv_name, '', led_type)
        elif wid_type == 'enum':
            widget = SiriusEnumComboBox(
                self, init_channel=pv_name)
            widget.setStyleSheet("min-width:4em;max-height:1em;")
        elif wid_type == 'state':
            widget = PyDMStateButton(
                self, init_channel=pv_name)
            widget.setStyleSheet("min-height: 0.6em; min-width: 1.5em;")
        else:
            if wid_type == 'edit':
                widget = SiriusLineEdit(
                    init_channel=pv_name)
                widget.precisionFromPV = False
                widget.precision = 2
                widget.setSizePolicy(
                    QSizePolicy.Maximum, QSizePolicy.Minimum)
            else:
                widget = SiriusLabel(
                    init_channel=pv_name,
                    keep_unit=keep_unit)
            if precision and 's' != pv_name[-1]:
                widget.displayFormat = _DisplayFormat.Exponential
            widget.setAlignment(Qt.AlignCenter)
            widget.setStyleSheet(
                "min-width:4em;max-width:5em;max-height:1em;")
        return widget

    def getGroupTitle(self, cat, id_num):
        """ Get element simple name """
        dev_id = id_num
        if cat == "Pump":
            name = "IPS"
        else:
            dev_number, dev_gen = self.buildIdsVac(id_num)
            if dev_gen == 3:
                dev_id = dev_number
                name = "PRG"
            else:
                dev_id = dev_number * 2
                if dev_gen == 1:
                    dev_id -= 1
                name = "CCG"
        return name + self.buildIdName(dev_id, False)

    def getSufixes(self, data):
        """ Format sufixes based on info type """
        pv_suf = ["", ""]
        if isinstance(data, str):
            pv_suf[0] = data
        elif isinstance(data, list):
            pv_suf = data
        elif isinstance(data, dict) and 'title' in data:
            pv_suf = {
                'status': data['status'],
                'control': data['control']
            }
        return pv_suf

    def setupUnitView(self, pv_name, color="#00000000", min_width=3):
        """Create and format SiriusLabel"""
        widget = SiriusLabel(
            init_channel=pv_name, keep_unit=True)
        styled = """
            min-height:0.75em;min-width: """+str(min_width)+"""em;
            max-height:0.75em;max-width: """+str(min_width*5)+"""em;
            background-color:"""+color+";"
        widget.setStyleSheet(styled)
        widget.showUnits = True
        widget.setAlignment(Qt.AlignCenter)
        if any(x in pv_name for x in ["RdPrs", "ReadP"]) and 's' != pv_name[-1]:
                widget.precisionFromPV = False
                widget.precision = 2
                widget.displayFormat = _DisplayFormat.Exponential
        return widget

    def setWindowBtn(self, cat, id_num):
        """ Create and configure button to open detail windows """
        button = QPushButton(_qta.icon('fa5s.ellipsis-h'), '', self)
        if cat == 'Vacuum':
            id_num, lx = self.buildIdsVac(id_num)
        _util.connect_window(
            button, self.selWindow(cat),
            parent=self, id_num=id_num)
        button.setStyleSheet("margin: 0.1em;")
        return button

    def buildLed(self, pv_name, sufix_list, comp):
        """ Build and configure different types of Led """
        if comp == 'normal':
            if "Gauge" in pv_name:
                comp = 'diff'
            led = PyDMLed(
                init_channel=pv_name + sufix_list)
        elif comp == 'alert':
            led = SiriusLedAlert(
                self, init_channel=pv_name)
        elif comp == 'on/off':
            chan2vals = {
                pv_name + sufix_list[0]: 1,
                pv_name + sufix_list[1]: 0
            }
            led = PyDMLedMultiChannel(
                self, chan2vals)
        else:
            chan2vals = {
                pv_name + sufix_list[0]: 1,
                pv_name + sufix_list[1]: 1
            }
            led = PyDMLedMultiIncosistencyDetector(
                self, chan2vals)
        shape = getShape(comp)
        led.shape = shape
        if shape not in [1, 2]:
            shape -= 2
        led.setStyleSheet(
            "min-width:"+str(shape)+"em; max-width:"+str(shape)+"em;")
        return led

    def SPRBWidget(self, title, control, readback, wid_type,
                   kp_unit=False, precision=True, sec_wid="label"):
        """
            Build a setpoint and readback widget:
            title + setpoint + readback
        """
        wid, lay = self.getLayoutWidget("H")
        lay.setContentsMargins(0, 1, 0, 1)
        if title != "":
            label = QLabel(title, alignment=Qt.AlignCenter)
            label.setStyleSheet("min-width:5em;")
            lay.addWidget(label)
        lay.addWidget(
            self.getWidget(control, wid_type, kp_unit, precision),
            alignment=Qt.AlignRight)
        widget = self.getWidget(readback, sec_wid, kp_unit, precision)
        lay.addWidget(
            widget,
            alignment=Qt.AlignLeft)
        return wid

    def getProgressBar(self, pv_name, limit, color=COLORS['purple']):
        """ Create and configure Progress Bar """
        prog_bar = MyScaleIndicator(
            init_channel=pv_name)
        prog_bar.limitsFromChannel = False
        prog_bar.showLimits = False
        prog_bar.showValue = False
        prog_bar.barIndicator = True
        prog_bar.userLowerLimit = limit[0]
        prog_bar.userUpperLimit = limit[1]
        prog_bar.indicatorColor = color
        width = 6
        if limit[1] == 200:
            width = 8
        prog_bar.setStyleSheet('min-height:1em; min-width:'+str(width)+'em;')
        return prog_bar


    def buildBasicGroup(self, cat, id_num, orient="V"):
        """ Build anc configure group template """
        group = QGroupBoxButton(
            title=self.getGroupTitle(cat, id_num))
        wid, lay = self.getLayoutWidget(orient)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 2, 0, 0)
        group.setLayout(lay)
        if orient == "H":
            lay.addWidget(
                self.setWindowBtn(cat, id_num),
                alignment=Qt.AlignLeft)
        else:
            group.setObjectName("group")
            group.setStyleSheet(
                "QGroupBox#group{background-color:"+COLORS['btn_bg']+"};")
            window = self.selWindow(cat)
            if cat == 'Vacuum':
                id_num, lx  = self.buildIdsVac(id_num)
            windowConfig = window(self, id_num=id_num)
            group.clicked.connect(lambda: windowConfig.show())
        return lay, group

    def buildAllLegends(self, listleg=LEGEND):
        """ Display all the legends """
        group = QGroupBox()
        lay = QHBoxLayout()
        group.setLayout(lay)
        group.setContentsMargins(0, 0, 0, 0)
        col = 0
        group.setTitle("LEGEND")
        for leg in listleg:
            if leg != 'size':
                lay.addWidget(
                    self.setupLegend(leg),
                    alignment=Qt.AlignTop)
                col += 1
        return group

    def setupLegend(self, legend):
        """ Show one of the legends present in the LEGEND variable in util"""
        wid, lay = self.getLayoutWidget()
        lay.addWidget(
            QLabel('<b>'+legend+'</b>'),
            0, 0, 1, 2, alignment=Qt.AlignCenter)
        row = 1
        for item in LEGEND[legend]:
            column = 0
            if 'color' in item:
                shape = getShape(legend)
                lay.addWidget(
                    LedLegend(
                        self, shape,
                        item['color'].name()),
                    row, column, 1, 1,
                    alignment=Qt.AlignRight | Qt.AlignVCenter)
                column = 1

            lay.addWidget(
                QLabel(item['text']),
                row, column, 1, 1,
                alignment=Qt.AlignLeft)
            row += 1
        return wid

    def buildIdName(self, id_num, is_valve=False):
        """Format number in the PV name"""
        pv_id = ""
        if not is_valve:
            if id_num < 10:
                pv_id = "0"
        pv_id += str(id_num)
        return pv_id

    def buildVacPv(self, id_num):
        """Generate VGC PV name with VGC id"""
        dev_number, dev_gen = self.buildIdsVac(id_num)
        pv_number = self.buildIdName(dev_number, False)
        return pv_number, dev_gen

    def buildIdsVac(self, id_num):
        """Get VGC group and individual identity and with VGC id"""
        dev_number = _math.ceil(id_num / 3)
        dev_gen = id_num % 3
        if not dev_gen:
            dev_gen = 3
        return dev_number, dev_gen

    def getVgcSPRB(self, data, pv_list, num, gen, sec_wid='led'):
        """ Use dict info to create a self.SPRBWidget """
        pv_name = {}
        for data_type, name in pv_list.items():
            pv_name[data_type] = num + name + str(gen)
        return self.SPRBWidget(
            data['title'], pv_name['control'],
            pv_name['status'], data['widget'],
            precision=(data['widget'] != 'enum'), sec_wid=sec_wid)

    def getVgcLed(self, name, gen, suf_list):
        """ Select led type based on VGC identity """
        if gen % 3 != 0:
            comp = 'equal'
        else:
            comp = 'normal'
        return self.buildLed(name, suf_list[gen % 3], comp)

    def getSPTable(self, num, gen, data, show_title=False, alternative=False):
        """ Build and configure VGC SP table"""
        pos = [0, 0]
        wid, lay = self.getLayoutWidget()
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        for title, obj_data in data.items():
            if show_title:
                lay.addWidget(
                    headerWidget(title, alternative),
                    pos[0], pos[1], 1, 3, alignment=Qt.AlignCenter)
            pos[0] += 1
            for sp_gen in data["No."][gen % 3]:
                if title == "No.":
                    text = ''
                    if not alternative:
                        text = str(sp_gen)
                    widget = QLabel('<strong>'+text+'</strong>')
                    widget.setStyleSheet("min-width: 2em;")
                    widget.setAlignment(Qt.AlignCenter)
                else:
                    pv_suf = self.getSufixes(obj_data)
                    if alternative:
                        if title == "SP" and sp_gen in [2, 6, 10]:
                            pv_suf = {'status': ':RdSH-', 'control': ':SetSH-'}
                            sp_gen -= 1
                        if title == "SP-H" and sp_gen in [1, 5, 9]:
                            pv_suf = {'status': ':RdSP-', 'control': ':SetSP-'}
                            sp_gen += 1
                    widget = self.getVgcSPRB(
                        obj_data, pv_suf, num, sp_gen, sec_wid='label')
                lay.addWidget(
                    widget, pos[0], pos[1],
                    1, 1, alignment=Qt.AlignCenter)
                pos[0] += 1
            pos[1] += 3
            pos[0] = 0
        return wid

    def getSimplePvWidget(self, title, suf, num, gen):
        """ Get simple VGC widget """
        pv_name = num + suf[0]
        if title in ["Pressure<br/>Readback", "Gauge<br/>Message"]:
            pv_name += str(gen) + suf[1]
            wid_type = "label"
        elif title == "Unit":
            wid_type = "enum"
        else:
            wid_type = "label"
        wid = self.getWidget(pv_name, wid_type)
        return wid

    def getVacPosition(self, id_vgc, divide=True):
        """ Get VGC widget position on the VGC Lists """
        pos = [0, 0]
        pos[0], pos[1] = self.buildIdsVac(id_vgc)
        if pos[1] == 3:
            if divide:
                pos[1] = 0
            else:
                pos[0] += 10
        else:
            pos[0] *= 2
            if pos[1] == 1:
                pos[0] -= 1
            if divide:
                pos[1] = 1
        return pos

    def buildIPSInfo(self, pv_name, lay, orient):
        """ Display IPS measurement information """
        for info_type in ['voltage', 'current']:
            info = IPS_DETAILS["General"][info_type]
            name = pv_name + info["text"]
            if info_type == 'current' and orient == 'H':
                lay.addWidget(
                    self.getProgressBar(name, [0, 200]),
                    alignment=Qt.AlignCenter)
            wid = self.setupUnitView(
                name, info['color'])
            lay.addWidget(
                wid, alignment=Qt.AlignCenter)
        return lay


def getShape(name):
    """ Get led shape number """
    if any(x in name for x in ["PRG", "normal"]):
        shape = PyDMLed.ShapeMap.Circle
    elif any(x in name for x in ["CCG", "equal"]):
        shape = PyDMLed.ShapeMap.Square
    elif "on/off" in name:
        shape = PyDMLed.ShapeMap.Triangle
    else:
        shape = PyDMLed.ShapeMap.Round
    return shape


def headerWidget(title, alternative):
    """ Get SP Table Header Widget """
    text = title
    if alternative:
        if title == "SP":
            text = "Warning"
        elif title == "SP-H":
            text = "Alarm"
        elif title == "No.":
            text = ""
    return QLabel('<strong>'+text+'</strong>')
