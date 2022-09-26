from qtpy.QtCore import Qt
import math as _math
from pydm.widgets.display_format import DisplayFormat as _DisplayFormat
from qtpy.QtWidgets import QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout
from .util import LEGEND
from .widgets import LedLegend
from ..widgets import SiriusLabel, PyDMLed, PyDMLedMultiChannel, \
    SiriusLineEdit, SiriusEnumComboBox


def buildIdName(id_num, isValve=False):
    pv_id = ""
    if not isValve:
        if id_num < 10:
            pv_id = "0"
    pv_id += str(id_num)
    return pv_id

def buildVacPv(id_num):
    dev_number, dev_gen = buildIdsVac(id_num)
    pv_number = buildIdName(dev_number, False)
    return pv_number, dev_gen

def buildIdsVac(id_num):
    dev_number = _math.ceil(id_num / 3)
    dev_gen = id_num % 3
    if not dev_gen:
        dev_gen = 3
    return dev_number, dev_gen

def showUnitView(pv_name, color="#00000000", min_width=3):
    widget = SiriusLabel(init_channel=pv_name)
    styled = """
        min-height:0.75em;min-width: """+str(min_width)+"""em;
        max-height:0.75em;max-width: """+str(min_width*5)+"""em;
        background-color:"""+color+";"
    widget.setStyleSheet(styled)
    widget.showUnits = True
    widget._keep_unit = True
    widget.setAlignment(Qt.AlignCenter)
    if any(x in pv_name for x in ["RdPrs", "ReadP"]):
        widget.precisionFromPV = False
        widget.precision = 2
        widget.displayFormat = _DisplayFormat.Exponential
    return widget

def getGroupTitle(cat, id_num):
    dev_id = id_num
    if cat == "Pump":
        name = "IPS"
    else:
        dev_number, dev_gen = buildIdsVac(id_num)
        if dev_gen == 3:
            dev_id = dev_number
            name = "PRG"
        else:
            dev_id = dev_number * 2
            if dev_gen == 1:
                dev_id -= 1
            name = "CCG"
    return name + buildIdName(dev_id, False)

def getShape(name):
    if any(x in name for x in ["PRG", "normal"]):
        shape = 1
    elif any(x in name for x in ["CCG", "equal"]):
        shape = 3
    elif "on/off" in name:
        shape = 4
    else:
        shape = 2
    return shape

def getLayoutWidget(orient="G"):
    wid = QWidget()
    if orient == "G":
        lay = QGridLayout()
    elif orient == "H":
        lay = QHBoxLayout()
    else:
        lay = QVBoxLayout()
    wid.setLayout(lay)
    return wid, lay

def showLegend(self, legend):
    """ Show one of the legends present in the LEGEND variable in util"""
    wid, lay = getLayoutWidget()
    lay.addWidget(
        QLabel('<b>'+legend+'</b>'),
        0, 0, 1, 2, alignment=Qt.AlignCenter)
    row = 1
    for item in LEGEND[legend]:
        column = 0
        if 'color' in item:
            shape = getShape(legend)
            lay.addWidget(
                LedLegend(self, shape,
                    item['color'].name()),
                row, column, 1, 1,
                alignment=Qt.AlignCenter)
            column = 1

        lay.addWidget(
            QLabel(item['text']),
            row, column, 1, 1,
            alignment=Qt.AlignLeft)
        row += 1
    return wid

def buildLed(self, pv_name, sufix_list, comp, bit=-1):
    if comp == 'normal':
        if "Gauge" in pv_name:
            comp='diff'
        led = PyDMLed(
            init_channel=pv_name+sufix_list, bit=bit)
    else: 
        if comp == 'on/off':
            chan2vals = {
                pv_name + sufix_list[0]: 1,
                pv_name + sufix_list[1]: 0
            }
        elif comp == 'equal':
            chan2vals = {
                pv_name + sufix_list[0]: 1,
                pv_name + sufix_list[1]: 1
            }
        led = PyDMLedMultiChannel(
            self, chan2vals)
    shape = getShape(comp)
    led.shape = shape
    if shape not in [1, 2]: shape-=2
    led.setStyleSheet("min-width:"+str(shape)+"em; max-width:"+str(shape)+"em;")
    return led

def SPRBWidget(self, title, control, readback, wid_type, kp_unit=False, sec_wid="label"):
    wid, lay = getLayoutWidget("H")
    if title != "":
        label = QLabel(title, alignment=Qt.AlignCenter)
        label.setStyleSheet("min-width:5em;")
        lay.addWidget(label)
    lay.addWidget(
        getWidget(self, control, wid_type, kp_unit), 
        alignment=Qt.AlignRight)
    widget = getWidget(self, readback, sec_wid, kp_unit, wid_type!='enum')
    lay.addWidget(
        widget, 
        alignment=Qt.AlignLeft)
    return wid

def getWidget(self, name, wid_type='button', keep_unit=False, precision=True):
    pv_name = self.devpref + name
    if wid_type == 'led':
        if 'ReadS' in name:
            bit = 1
        else:
            bit = -1
        widget = buildLed(
            self, pv_name, '', 'normal', bit)
    elif wid_type == 'enum':
        widget = SiriusEnumComboBox(
            self, init_channel=pv_name)
        widget.setStyleSheet("min-width:4em;")
    else:
        if wid_type == 'edit':
            widget = SiriusLineEdit(
                init_channel=pv_name)
        else:
            widget = SiriusLabel(
                init_channel=pv_name)
            if keep_unit:
                widget._keep_unit = True
        if precision:
            widget.precisionFromPV = False
            widget.precision = 2
            widget.displayFormat = _DisplayFormat.Exponential
        widget.setAlignment(Qt.AlignCenter)
        widget.setStyleSheet("min-width:4em;")
    return widget

def showAllLegends(self, list=LEGEND):
    wid, lay = getLayoutWidget("H")
    for leg in list:
        if leg != 'size':
            lay.addWidget( 
                showLegend(self, leg))
    return wid