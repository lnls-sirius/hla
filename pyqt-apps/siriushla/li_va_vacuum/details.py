from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
from siriushla.li_va_vacuum.widgets import OnOffBtn
from .functions import SPRBWidget, buildBasicGroup, buildIPSInfo, buildIdName, buildIdsVac, buildVacPv, getLayoutWidget, \
    getGroupTitle, getProgressBar, getSPTable, getSimplePvWidget, getSufixes, getVacPosition, getVgcLed, \
    getVgcSPRB, getWidget, setWindowBtn, showAllLegends, showUnitView
from .util import IPS_DETAILS, PVS_CONFIG, VGC_DETAILS
from ..widgets import SiriusMainWindow

class IpsDetailWindow(SiriusMainWindow):
    """ Display IPS Detail Window"""

    def __init__(self, parent=None, prefix='', id_ips=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.main_dev = PVS_CONFIG["Pump"]["prefix"]
        self.devpref = self.prefix + self.main_dev + buildIdName(id_ips)
        self.setObjectName('LIApp')
        self.setWindowTitle("IPS "+str(id_ips)+" Details")
        self._setupUi()

    def buildIPSDetail(self, info):
        """ Display IPS measurement complete information """
        wid = QGroupBox()
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        wid.setLayout(lay)
        for info_type, type_config in info.items():
            name = self.devpref + type_config['text']
            widget = showUnitView(
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
                lay.addWidget(
                    SPRBWidget(self,
                        item['title'], item['control'], 
                        item['status'], item['widget'],
                        True))
            else:
                lay.addWidget(
                    getWidget(
                        self, item['status'], item['widget']),
                    alignment=Qt.AlignCenter)
                    
        return group

    def _setupUi(self):
        """."""
        wid, lay = getLayoutWidget()
        self.setCentralWidget(wid)
        pos = [0, 0, 1, 1]
        lay.setContentsMargins(10, 0, 10, 0)
        for title, info in IPS_DETAILS.items():
            pos[3] = 1
            if title == "General":
                group = self.buildIPSDetail(info)
                pos[3] = 2
            else:
                group = self.buildGroup(info, title) 
            lay.addWidget(
                group, pos[0], pos[1], pos[2], pos[3])
            pos[0] = 1
            if title != "General":
                pos[1] += 1
            

class VgcDetailWindow(SiriusMainWindow):
    """ Display VGC Detail Window"""

    def __init__(self, parent=None, prefix='', id_vgc=''):
        """Init."""
        super().__init__(parent)
        self.config = PVS_CONFIG["Vacuum"]
        self.prefix = prefix
        self.main_dev = self.config["prefix"]
        self.setObjectName('LIApp')
        self.number, gen = buildIdsVac(id_vgc)
        self.setWindowTitle(
            "VGC "+str(self.number)+" Details")
        self.devpref = self.prefix + self.main_dev
        self._setupUi()

    def showDevices(self, title, data, lay, col):
        """ Display the infomation of three devices of the same group"""
        row = 1
        for gen in range(3, 0, -1):
            vgc_id = (self.number * 3)-(gen-1)
            pv_number, generation = buildVacPv(vgc_id)
            pv_suf = getSufixes(data)
            if title == "Gauge":
                widget = QLabel(
                    '<strong>'+getGroupTitle(data, vgc_id)+'</strong>', 
                    alignment=Qt.AlignCenter)
            elif isinstance(data, dict):
                if title == "Setpoint":
                    showTitle = False
                    if gen == 3:
                        showTitle = True
                    widget = getSPTable(
                        self, pv_number, generation, data, showTitle)
                elif 'title' in data:
                    widget = getVgcSPRB(
                        self, data, pv_suf, pv_number, generation)
                else:
                    pv_name = self.devpref + str(pv_number) + data['text']
                    widget = getVgcLed(
                        self, pv_name, generation, data['sufix'])
            else:
                widget = getSimplePvWidget(
                    self, title, pv_suf, pv_number, generation)
            lay.addWidget(widget, row, col)
            row += 1

    def buildVgcTable(self):
        """ Create the information columns """
        wid, lay = getLayoutWidget()
        pos = [0, 0]
        for title, data in VGC_DETAILS.items():
            if title != 'led':
                label = QLabel('<strong>'+title+'</strong>')
                label.setAlignment(Qt.AlignCenter)
                lay.addWidget(
                    label, pos[0], pos[1],
                    alignment=Qt.AlignCenter)
            self.showDevices(title, data, lay, pos[1])
            pos[1] += 1
        return wid

    def _setupUi(self):
        """."""
        wid, lay = getLayoutWidget("V")
        self.setCentralWidget(wid)
        lay.setContentsMargins(10, 0, 10, 0)

        lay.addWidget(self.buildVgcTable())
        lay.addWidget(showAllLegends(self, 
            ['CCG', 'PRG', 'Gauge Status', 'Relay Status']))
         

class DetailWindow(SiriusMainWindow):
    """ Display General Detail Window"""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self.setObjectName('LIApp')
        self.setWindowTitle("Vacuum Details")
        self._setupUi()
    
    def selWindow(self, cat, id=0):
        """ Open selected window with click """
        if cat == "Pump":
            self.window = IpsDetailWindow(id_ips=id)
        else:
            self.window = VgcDetailWindow(id_vgc=id)
        self.window.show()
    
    def showAllDevices(self, title, data, lay, pos):
        """ Display the VGC informations of one device"""
        config = PVS_CONFIG["Vacuum"]
        pv_range = config['iterations']
        self.devpref = config['prefix']
        for vgc_id in range(pv_range[0], pv_range[1]+1):
            pv_number, generation = buildVacPv(vgc_id)
            pos_temp = getVacPosition(vgc_id, False)
            pos[0] = pos_temp[0]
            pv_suf = getSufixes(data)
            if title == "Gauge":
                pos[1] = 0
                lay.addWidget(
                    setWindowBtn(
                        self, "Vacuum", vgc_id), pos[0], pos[1], 1, 1)
                pos[1] += 1
                widget = QLabel(
                    '<strong>'+getGroupTitle(data, vgc_id)+'</strong>')
            elif isinstance(data, dict):
                if title == "Setpoint":
                    widget = getSPTable(
                        self, pv_number, generation, data, pos[0]==1, True)
                elif 'title' in data:
                    widget = getVgcSPRB(
                        self, data, pv_suf, pv_number, generation)
                else:
                    pv_name = self.devpref + pv_number + data['text']
                    widget = getVgcLed(
                        self, pv_name, generation, data['sufix'])
            else:
                if title  == "Gauge<br/>Message":
                    if generation == 3:
                        limits = [-4, -2]
                    else:
                        limits = [-11, -2]
                    widget = getProgressBar(
                        self.devpref+pv_number+config["bar"]+str(generation), limits)
                else:
                    widget = getSimplePvWidget(
                        self, title, pv_suf, pv_number, generation)
            lay.addWidget(
                widget, pos[0], pos[1], 1, 1, Qt.AlignCenter)
            pos[0] += 1
        return pos

    def showIPSControl(self, pv_name, lay_item):
        """ Display simple buttons for IPS Control """
        for item in IPS_DETAILS["Status"]:
            if 'title' in item:
                if item['title'] != "State":
                    name = pv_name + item['control']
                    if item['title'] == "Local/\nRemote":
                        wid = getWidget(self, name[12:], item['widget'])
                        max = 3.5
                    else:
                        wid = OnOffBtn(
                            self, init_channel=name, label=item['title'])
                        max = 2.5
                    wid.setStyleSheet("max-width:"+str(max)+"em;")
                    lay_item.addWidget(wid)

    def showVgcList(self):
        """ Display VGC Widget List with all VGC elements """
        wid, lay = getLayoutWidget("G")
        pos = [0, 1]
        for title, data in VGC_DETAILS.items():
            pos[0] = 0
            if title != 'led':
                label = QLabel('<strong>'+title+'</strong>')
                label.setAlignment(Qt.AlignCenter)
                lay.addWidget(label, pos[0], pos[1], 1, 1)
            pos[0] += 1
            pos = self.showAllDevices(title, data, lay, pos)
            pos[1] += 1
        return wid

    def showIPSList(self):
        """ Display IPS Widget List with all IPS elements """
        wid, lay = getLayoutWidget("V")
        cat = "Pump"
        config = PVS_CONFIG[cat]
        self.devpref = config['prefix']
        pv_range = config["iterations"]
        for item in range(pv_range[0], pv_range[1]+1):
            pv_name = self.devpref + buildIdName(item)
            lay_item, widget = buildBasicGroup(
                self, cat, item, "H")
            buildIPSInfo(pv_name, lay_item, "H")
            self.showIPSControl(pv_name, lay_item)
            lay.addWidget(widget)
        return wid

    def buildList(self, cat):
        """ Select which widget list to build """
        if cat == "Vacuum":
            wid = self.showVgcList()
        else:
            wid = self.showIPSList()
        return wid

    def widgetLists(self):
        """ Build all lists """
        wid, lay = getLayoutWidget("H")
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        size = 3
        for cat in PVS_CONFIG:
            if cat != "Valve":
                lay.addWidget(
                    self.buildList(cat), size)
                size = 1
        return wid

    def _setupUi(self):
        """."""
        wid, lay = getLayoutWidget("V")
        self.setCentralWidget(wid)
        lay.setContentsMargins(10, 0, 10, 0)

        lay.addWidget(self.widgetLists())
        lay.addWidget(showAllLegends(self))