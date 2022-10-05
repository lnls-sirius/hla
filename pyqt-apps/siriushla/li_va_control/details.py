""" All the detail Chart Windows """

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
from .functions import BaseFunctionsInterface
from .util import IPS_DETAILS, PVS_CONFIG, VGC_DETAILS, COLORS
from ..widgets import SiriusMainWindow


class IpsDetailWindow(SiriusMainWindow, BaseFunctionsInterface):
    """ Display IPS Detail Window"""

    def __init__(self, parent=None, prefix='', id_ips=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.main_dev = PVS_CONFIG["Pump"]["prefix"]
        self.devpref = self.prefix + self.main_dev + self.buildIdName(id_ips)
        self.setObjectName('LIApp')
        title = "IPS "+str(id_ips)+" Details"
        self.setWindowTitle(title)
        self._setupUi(title)

    def buildIPSDetail(self, info):
        """ Display IPS measurement complete information """
        wid = QGroupBox()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)
        for info_type, type_config in info.items():
            name = self.devpref + type_config['text']
            widget = self.setupUnitView(
                name, type_config['color'], 6)
            lay.addWidget(widget, alignment=Qt.AlignCenter)
        return wid

    def buildGroup(self, info, title):
        """ Display one detail group """
        group = QGroupBox()
        lay = QVBoxLayout()
        group.setTitle(title)
        group.setLayout(lay)
        for item in info:
            if 'title' in item:
                if item['widget'] == 'state':
                    sec_wid = 'led'
                else:
                    sec_wid = 'label'
                lay.addWidget(
                    self.SPRBWidget(
                        item['title'], item['control'],
                        item['status'], item['widget'],
                        True, False, sec_wid), 2)
            else:
                lay.addWidget(
                    self.getWidget(
                        item['status'], item['widget']),
                    3, alignment=Qt.AlignCenter)

        return group

    def _setupUi(self, title):
        """."""
        wid, lay = self.getLayoutWidget()
        self.setCentralWidget(wid)
        pos = [1, 0, 1, 1]
        lay.setContentsMargins(10, 0, 10, 0)
        lay.addWidget(
            QLabel("<strong>"+title+"</strong>"),
            0, 0, 1, 2, alignment=Qt.AlignCenter)
        for title, info in IPS_DETAILS.items():
            pos[3] = 1
            if title == "General":
                group = self.buildIPSDetail(info)
                pos[3] = 2
            else:
                group = self.buildGroup(info, title)
            lay.addWidget(
                group, pos[0], pos[1], pos[2], pos[3])
            pos[0] = 2
            if title != "General":
                pos[1] += 1


class VgcDetailWindow(SiriusMainWindow, BaseFunctionsInterface):
    """ Display VGC Detail Window"""

    def __init__(self, parent=None, prefix='', id_vgc=''):
        """Init."""
        super().__init__(parent)
        self.config = PVS_CONFIG["Vacuum"]
        self.prefix = prefix
        self.main_dev = self.config["prefix"]
        self.setObjectName('LIApp')
        self.number, gen = self.buildIdsVac(id_vgc)
        title = "VGC "+str(self.number)+" Details"
        self.setWindowTitle(title)
        self.devpref = self.prefix + self.main_dev
        self._setupUi(title)

    def setupDevices(self, title, data, lay, col):
        """ Display the infomation of three devices of the same group"""
        row = 1
        for gen in range(3, 0, -1):
            vgc_id = (self.number * 3)-(gen-1)
            pv_number, generation = self.buildVacPv(vgc_id)
            pv_suf = self.getSufixes(data)
            if title == "Gauge":
                widget = QLabel(
                    '<strong>'+self.getGroupTitle(data, vgc_id)+'</strong>',
                    alignment=Qt.AlignCenter)
            elif isinstance(data, dict):
                if title == "Setpoint":
                    show_title = False
                    if gen == 3:
                        show_title = True
                    widget = self.getSPTable(
                        pv_number, generation, data, show_title)
                elif 'title' in data:
                    widget = self.getVgcSPRB(
                        data, pv_suf, pv_number, generation)
                else:
                    pv_name = self.devpref + str(pv_number) + data['text']
                    widget = self.getVgcLed(
                        pv_name, generation, data['sufix'])
            else:
                widget = self.getSimplePvWidget(
                    title,
                    pv_suf, pv_number, generation)
            lay.addWidget(widget, row, col)
            row += 1

    def buildVgcTable(self):
        """ Create the information columns """
        wid, lay = self.getLayoutWidget()
        pos = [0, 0]
        for title, data in VGC_DETAILS.items():
            if title != 'led':
                label = QLabel('<strong>'+title+'</strong>')
                label.setAlignment(Qt.AlignCenter)
                lay.addWidget(
                    label, pos[0], pos[1],
                    alignment=Qt.AlignCenter)
            self.setupDevices(title, data, lay, pos[1])
            pos[1] += 1
        return wid

    def _setupUi(self, title):
        """."""
        wid, lay = self.getLayoutWidget("V")
        self.setCentralWidget(wid)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.addWidget(
            QLabel("<strong>"+title+"</strong>"),
            alignment=Qt.AlignCenter)
        lay.addWidget(self.buildVgcTable())
        leg_list = [
            'CCG', 'PRG', 'Gauge Status', 'Relay Status']
        lay.addWidget(
            self.buildAllLegends(leg_list))


class DetailWindow(SiriusMainWindow, BaseFunctionsInterface):
    """ Display General Detail Window"""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self.devpref = ""
        self.window = None
        self.setObjectName('LIApp')
        self.setWindowTitle("Vacuum Details")
        self._setupUi()

    def selWindow(self, cat, id_win=0):
        """ Open selected window with click """
        if cat == "Pump":
            self.window = IpsDetailWindow(id_ips=id_win)
        else:
            self.window = VgcDetailWindow(id_vgc=id_win)
        self.window.show()

    def setupAllDevices(self, title, data, lay, pos):
        """ Display the VGC informations of one device"""
        config = PVS_CONFIG["Vacuum"]
        pv_range = config['iterations']
        self.devpref = config['prefix']
        for vgc_id in range(pv_range[0], pv_range[1]+1):
            pv_number, generation = self.buildVacPv(vgc_id)
            pos_temp = self.getVacPosition(vgc_id, False)
            pos[0] = pos_temp[0]
            pv_suf = self.getSufixes(data)
            if title == "Gauge":
                pos[1] = 0
                lay.addWidget(
                    self.setWindowBtn(
                        "Vacuum", vgc_id), pos[0], pos[1], 1, 1)
                pos[1] += 1
                widget = QLabel(
                    '<strong>'+self.getGroupTitle(data, vgc_id)+'</strong>')
            elif isinstance(data, dict):
                if title == "Setpoint":
                    widget = self.getSPTable(
                        pv_number, generation,
                        data, pos[0] == 1, True)
                elif 'title' in data:
                    widget = self.getVgcSPRB(
                        data, pv_suf, pv_number, generation)
                else:
                    pv_name = self.devpref + pv_number + data['text']
                    widget = self.getVgcLed(
                        pv_name, generation, data['sufix'])
            else:
                if title == "Gauge<br/>Message":
                    if generation == 3:
                        limits = [-4, -2]
                    else:
                        limits = [-11, -2]
                    widget = self.getProgressBar(
                        self.devpref+pv_number+config["bar"]+str(generation),
                        limits, COLORS["gre_blu"])
                else:
                    widget = self.getSimplePvWidget(
                        title,
                        pv_suf, pv_number, generation)
            lay.addWidget(
                widget, pos[0], pos[1], 1, 1, Qt.AlignCenter)
            pos[0] += 1
        return pos

    def setupIPSControl(self, pv_name):
        """ Display simple buttons for IPS Control """
        wid, lay = self.getLayoutWidget("G")
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        pos = [0, 0]
        for item in IPS_DETAILS["Status"]:
            if 'title' in item:
                if item['title'] != "State":
                    name = pv_name + item['control']
                    if item['title'] != "Local/\nRemote":
                        lbl = QLabel(item['title'])
                        lbl.setStyleSheet(
                            "font: 8pt;max-height:0.6em; min-width:2em;")
                        lay.addWidget(lbl, pos[0], pos[1])
                    pos[0] += 1
                    lay.addWidget(
                        self.getWidget(name[12:], item['widget']),
                        pos[0], pos[1])
                    pos[1] += 1
                    pos[0] = 0

        return wid

    def setupVgcListDet(self):
        """ Display VGC Widget List with all VGC elements """
        wid, lay = self.getLayoutWidget("G")
        pos = [0, 1]
        for title, data in VGC_DETAILS.items():
            pos[0] = 0
            if title != 'led':
                label = QLabel('<strong>'+title+'</strong>')
                label.setAlignment(Qt.AlignCenter)
                lay.addWidget(label, pos[0], pos[1], 1, 1)
            pos[0] += 1
            pos = self.setupAllDevices(title, data, lay, pos)
            pos[1] += 1
        return wid

    def setupIPSListDet(self):
        """ Display IPS Widget List with all IPS elements """
        wid, lay = self.getLayoutWidget("V")
        cat = "Pump"
        config = PVS_CONFIG[cat]
        self.devpref = config['prefix']
        pv_range = config["iterations"]
        for item in range(pv_range[0], pv_range[1]+1):
            pv_name = self.devpref + self.buildIdName(item)
            lay_item, widget = self.buildBasicGroup(
                cat, item, "H")
            self.buildIPSInfo(pv_name, lay_item, "H")
            lay_item.addWidget(
                self.setupIPSControl(pv_name))
            lay.addWidget(widget)
        return wid

    def buildList(self, cat):
        """ Select which widget list to build """
        if cat == "Vacuum":
            wid = self.setupVgcListDet()
        else:
            wid = self.setupIPSListDet()
        return wid

    def widgetLists(self):
        """ Build all lists """
        wid, lay = self.getLayoutWidget("H")
        lay.setContentsMargins(0, 0, 0, 0)
        size = 3
        for cat in PVS_CONFIG:
            if cat != "Valve":
                group = QGroupBox()
                lay_group = QVBoxLayout()
                lay_group.setSpacing(0)
                lay_group.setContentsMargins(0, 0, 0, 0)
                group.setTitle(cat)
                group.setLayout(lay_group)
                lay_group.addWidget(self.buildList(cat))
                lay.addWidget(group, size)
                size = 1
        return wid

    def _setupUi(self):
        """."""
        wid, lay = self.getLayoutWidget("V")
        self.setCentralWidget(wid)
        lay.setContentsMargins(0, 0, 0, 0)

        lay.addWidget(self.widgetLists(), 5)
        lay.addWidget(self.buildAllLegends(), 1)
