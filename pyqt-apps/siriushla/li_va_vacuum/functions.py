from qtpy.QtCore import Qt
import math as _math
from pydm.widgets.display_format import DisplayFormat as _DisplayFormat
from ..widgets import SiriusLabel


def buildIdName(name, id_num, isValve=False):
    pv_id = ""
    if not isValve:
        if id_num < 10:
            pv_id = "0"
    pv_id += str(id_num)
    return name + pv_id

def buildVacPv(config, id_num):
    dev_number, dev_gen = buildIdsVac(id_num)
    if dev_gen == 2:
        dev_number -= 5
    pv_name = buildIdName(
        config["prefix"], dev_number, False)
    return pv_name, dev_gen

def buildIdsVac(id_num):
    dev_number = _math.ceil(id_num / 3)
    dev_gen = id_num % 3
    if dev_gen == 2:
        dev_number += 5
    if not dev_gen:
        dev_gen = 3
    return dev_number, dev_gen

def showUnitView(pv_name, color="#000000", min_width=3):
    widget = SiriusLabel(init_channel=pv_name)
    styled = """
        min-height:0.75em;min-width: """+str(min_width)+"""em;
        max-height:0.75em;max-width: 10em;
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