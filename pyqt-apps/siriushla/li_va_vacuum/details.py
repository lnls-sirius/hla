from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QLabel, QGridLayout
from .functions import SPRBWidget, buildIdName, buildIdsVac, buildLed, buildVacPv, getLayoutWidget, \
    getGroupTitle, getWidget, showAllLegends, showUnitView
from .util import IPS_DETAILS, PVS_CONFIG, VGC_DETAILS
from ..widgets import SiriusMainWindow

class IpsDetailWindow(SiriusMainWindow):
    """."""

    def __init__(self, parent=None, prefix='', id_ips=''):
        """Init."""
        super().__init__(parent)
        self.prefix = prefix
        self.main_dev = PVS_CONFIG["Pump"]["prefix"]
        self.devpref = self.prefix + self.main_dev + buildIdName(id_ips)
        self.setObjectName('LIApp')
        self.setWindowTitle("IPS "+str(id_ips)+" Details")
        self._setupUi()

    def buildIPSInfo(self, info):
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
                group = self.buildIPSInfo(info)
                pos[3] = 2
            else:
                group = self.buildGroup(info, title) 
            lay.addWidget(
                group, pos[0], pos[1], pos[2], pos[3])
            pos[0] = 1
            if title != "General":
                pos[1] += 1
            

class VgcDetailWindow(SiriusMainWindow):
    """."""

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

    def getSufixes(self, data):
        pv_suf = ["", ""]
        if isinstance(data, str):
            pv_suf[0] = data
        elif isinstance(data, list):
            pv_suf[0] = data[0]
            pv_suf[1] = data[1]
        elif isinstance(data, dict) and 'title' in data:
            pv_suf = {
                'status': data['status'], 
                'control': data['control']
            }
        return pv_suf

    def showSPTable(self, num, gen, data):
        pos = [0, 0]
        wid, lay = getLayoutWidget()
        lay.setSpacing(0)
        for title, obj_data in data.items():
            lay.addWidget(
                QLabel('<strong>'+title+'</strong>'), pos[0], pos[1],
                1, 3, alignment=Qt.AlignCenter)
            pos[0] += 1
            for sp_gen in data["No."][gen%3]:
                if title == "No.":
                    widget = QLabel('<strong>'+str(sp_gen)+'</strong>')
                else:
                    pv_name = {}
                    pv_suf = self.getSufixes(obj_data)
                    for data_type, name in pv_suf.items():
                        pv_name[data_type] = num + name + str(sp_gen)
                    widget = SPRBWidget(
                        self, obj_data["title"], pv_name["control"],
                        pv_name["status"], obj_data["widget"])
                lay.addWidget(
                    widget, pos[0], pos[1], 
                    1, 1, alignment=Qt.AlignCenter)
                pos[0] += 1
            pos[1] += 3
            pos[0] = 0
        return wid

    def showDevices(self, title, data, lay, col):
        row = 1
        for gen in range(3, 0, -1):
            vgc_id = (self.number * 3)-(gen-1)
            pv_number, generation = buildVacPv(vgc_id)
            pv_suf = self.getSufixes(data)
            if title == "Gauge":
                widget = QLabel(
                    '<strong>'+getGroupTitle(data, vgc_id)+'</strong>', 
                    alignment=Qt.AlignCenter)
            elif isinstance(data, dict):
                if title == "Setpoint":
                    widget = self.showSPTable(pv_number, generation, data)
                elif 'title' in data:
                    pv_name = {}
                    for data_type, name in pv_suf.items():
                        pv_name[data_type] = pv_number + name + str(generation)
                    widget = SPRBWidget(
                        self, data['title'], pv_name['control'], 
                        pv_name['status'], data['widget'], sec_wid='led')
                else:
                    pv_name = self.devpref + str(pv_number) + data['text']
                    if generation%3 != 0:
                        comp = 'equal'
                    else:
                        comp = 'normal'
                    widget = buildLed(self, pv_name, data['sufix'][generation%3], comp)
            else:
                pv_name = pv_number + pv_suf[0]
                if title in ["Pressure<br/>Readback", "Gauge<br/>Message"]:
                    pv_name += str(generation) + pv_suf[1]
                    wid_type = "label"
                elif title == "Unit":
                    wid_type = "enum"
                else:
                    wid_type = "label"
                widget = getWidget(
                    self, pv_name, wid_type)
            
            lay.addWidget(widget, row, col)
            row += 1

    def buildVgcTable(self):
        wid, lay = getLayoutWidget()
        pos = [0, 0]
        for title, data in VGC_DETAILS.items():
            if title not in ['led', 'SP']:
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
    """."""

    def __init__(self, parent=None):
        """Init."""
        super().__init__(parent)
        self.setObjectName('LIApp')
        self.setWindowTitle("Vacuum Details")
        self._setupUi()

    def buildList(self, cat):
        wid, lay = getLayoutWidget("V")
        # lay.setSpacing(0)
        # lay.setContentsMargins(0, 0, 0, 0)
        # config = PVS_CONFIG[cat]
        # pv_range = config["iterations"]
        # for item in range(pv_range[0], pv_range[1]+1):
        #     # widget = getGroupWidgets(
        #     #     config, item, cat)
        #     widget = QLabel("213")
        #     lay.addWidget(widget)
        return wid

    def widgetLists(self):
        wid, lay = getLayoutWidget("H")
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        for cat in PVS_CONFIG:
            if cat != "Valve":
                lay.addWidget(
                    self.buildList(cat),
                    alignment=Qt.AlignCenter)
        return wid

    def _setupUi(self):
        """."""
        wid, lay = getLayoutWidget("V")
        self.setCentralWidget(wid)
        lay.setContentsMargins(10, 0, 10, 0)

        lay.addWidget(self.widgetLists())
        lay.addWidget(showAllLegends(self))