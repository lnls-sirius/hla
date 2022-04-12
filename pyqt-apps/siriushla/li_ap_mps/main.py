''' Diagnostic Interface of the LINAC's BPM'''
from qtpy.QtCore import Qt, QEvent
from qtpy.QtWidgets import QWidget, QGroupBox, QHBoxLayout, \
    QVBoxLayout, QGridLayout, QLabel
import qtawesome as qta
from pydm.widgets import PyDMPushButton

from .util import PV_MPS, MPS_PREFIX, CTRL_TYPE, GROUP_POS, LBL_MPS, LBL_WATER
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, SiriusLedState


class MPSController(SiriusMainWindow):
    ''' Monitor Protection System Controller Interface '''


    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')
        self.pvObj = {}

        color = get_appropriate_color('LI')
        self.setObjectName('LIApp')

        self.setWindowTitle('LI MPS Controller')
        self._setupUi()

    def clearLayout(self, lay):
        while lay.count():
            child = lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        return lay

    def controlWidget(self, pv_name, lay):
        widget = QWidget()

        control_layout = self.controlHiddenBox(pv_name, lay)
        widget.setLayout(control_layout)
        self.pvObj.update(
            {widget: {
                "name": pv_name,
                "layout": control_layout
            }})
        widget.installEventFilter(self)
        return widget

    def controlBox(self, pv_name, lay):
        lay = self.clearLayout(lay)
        pos = [0, 0]

        for control_name in CTRL_TYPE:
            lb_title = QLabel(control_name)
            lay.addWidget(lb_title, pos[0], pos[1], 1, 1)
            ctrl_widget = self.getCtrlWidget(
                pv_name, CTRL_TYPE.get(control_name))
            lay.addWidget(ctrl_widget, pos[0]+1, pos[1], 1, 1)
            pos[1] += 1
            if(pos[1]>=2):
                pos[1] = 0
                pos[0] += 2
        return lay

    def setPvLbl(self, pv_name):
        pvLbl = LBL_WATER.get(pv_name)
        lb_titleWid = QLabel(pvLbl)
        lb_titleWid.setAlignment(Qt.AlignCenter)
        return lb_titleWid


    def controlHiddenBox(self, pv_name, cb_glay):
        '''Display the box for the control Interface'''

        if cb_glay == '':
            cb_glay = QGridLayout()
        else:
            cb_glay = self.clearLayout(cb_glay)

        if pv_name.find('WFS') != -1:
            cb_glay.addWidget(
                self.setPvLbl(pv_name), 0, 0, 1, 1)

        widget = self.getCtrlWidget(pv_name, '_L')
        widget.clicked.connect(
            lambda: self.controlBox(pv_name, cb_glay))
        cb_glay.addWidget(widget, 1, 0, 1, 1)

        return cb_glay

    def eventFilter(self, ob, event):
        obj = self.pvObj.get(ob)
        # if event.type() == QEvent.Enter:
        #     self.controlBox(obj.get("name"), obj.get("layout"))
        #     self.stop = True
        #     return True
        if event.type() == QEvent.Leave:
            self.controlHiddenBox(obj.get("name"), obj.get("layout"))
            self.stop = False
        return False

    def getDeviceName(self, pv_name):
        if pv_name.find('LA-RF:LLRF:KLY') != -1:
            device_name = ''
        else:
            device_name = MPS_PREFIX
        return device_name

    def getCtrlWidget(self, pv_name, ctrl_type):
        device_name = self.getDeviceName(pv_name)
        if ctrl_type in ['_I', '_L', '']:
            widget = SiriusLedState(
                init_channel = device_name + pv_name + ctrl_type)
        elif ctrl_type == '_B':
            #Change this widget for '_R' and '_B' for value on btn down and up
            #edit: Label -> Active if off and Byspass if
            widget = PyDMPushButton(
                init_channel = device_name + pv_name + ctrl_type,
                label = 'Active')
        elif ctrl_type == '_R':
            widget = PyDMPushButton(
                init_channel = device_name + pv_name + ctrl_type,
                label = 'Reset')

        return widget

    def getListSize(self, pv_data):
        for item in pv_data:
            if type(item) == list:
                return len(item)
        return 1

    def statusBox(self, pv_name):
        sb_hlay = QHBoxLayout()
        sb_hlay.addWidget(
            self.getCtrlWidget(pv_name, ''), 1)
        return sb_hlay

    def genStringPV(self, prefix, suffix, num):

        if prefix in ['HeartBeat', 'LAWarn', 'LAAlarm', 'Gun', 'WaterState']:
            pv_name = str(prefix)+str(suffix)
        elif prefix == 'PPState':
            pv_name = str(prefix)+str(num+6)+str(suffix)
        else:
            pv_name = str(prefix)+str(num)+str(suffix)

        return pv_name

    def getLoopQuant(self, loopQuant, index):
        if type(loopQuant) == list:
            return loopQuant[index]+1
        else:
            return loopQuant+1

    def getPVComplement(self, string, index):
        if type(string) == list:
            return string[index]
        else:
            return string

    def updateCount(self, count, title):
        if title in ['Water']:
            if count[1] >= 4:
                count[0] += 1
                count[1] = 1
            else:
                count[1] += 1
        elif title in ['Klystrons', 'General Control', 'Modulator Control']:
            val = 2
            if title == 'Modulator Control':
                val = 1
            if count[0] >= val:
                count[1] += 1
                count[0] = 1
            else:
                count[0] += 1
        else:
            if count in [
                [7, 2], [9, 2], [12, 2], [14, 2],
                [7, 3], [9, 3], [12, 3], [14, 3],
                [7, 4], [14, 4]]:
                count[0] += 1
            elif count in [[3, 2], [3, 3]]:
                count[0] += 2
            elif count == [1, 4]:
                count[0] += 5
            elif count == [9, 4]:
                count[0] += 4
            count[0] += 1
            if count[0] >= 17:
                count[1] += 1
                count[0] = 1
        return count

    def setTitleLabel(self, item, axis, layout):
        pos = [0, 0]
        for pos[axis] in range(1, len(item)+1):
            lbl_header = QLabel(item[pos[axis]-1])
            lbl_header.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_header, pos[0], pos[1], 1, 1)
        return layout

    def getSingleTitle(self, title, layout):
        pos = [0, 0]
        if title in LBL_MPS:
            lbl_item = LBL_MPS.get(title)
            layout = self.setTitleLabel(lbl_item[0], 0, layout)
            layout = self.setTitleLabel(lbl_item[1], 1, layout)
        return layout

    def displayGroup(self, pv_data, pv_size, title):
        dg_glay = QGridLayout()
        group = QGroupBox()
        count = [1, 1]

        dg_glay = self.getSingleTitle(title, dg_glay)
        for index in range(0, pv_size):
            loop_quant = self.getLoopQuant(pv_data[0], index)
            for counter in range(1, loop_quant):
                pv_name = self.genStringPV(
                    self.getPVComplement(pv_data[1], index),
                    self.getPVComplement(pv_data[2], index),
                    counter)
                if pv_data[4]:
                    dg_glay.addWidget(
                        self.controlWidget(pv_name, ''),
                        count[0], count[1], 1, 1)
                else:
                    dg_glay.addLayout(
                        self.statusBox(pv_name),
                        count[0], count[1], 1, 1)

                count = self.updateCount(count, title)

        group.setTitle(title)
        group.setLayout(dg_glay)

        return group

    def displayMpsGroups(self):
        dm_glay = QGridLayout()
        for group in PV_MPS:
            pv_data = PV_MPS.get(group)
            pv_size = self.getListSize(pv_data)
            group_pos = GROUP_POS.get(group)

            dm_glay.addWidget(
                self.displayGroup(pv_data, pv_size, group),
                group_pos[0], group_pos[1], group_pos[2], group_pos[3])

        return dm_glay

    def _setupUi(self):

        wid = QWidget(self)
        if_glay = QGridLayout()
        if_glay.addLayout(self.displayMpsGroups(), 0, 0, 1, 1)
        if_glay.setAlignment(Qt.AlignTop)

        wid.setLayout(if_glay)
        self.setCentralWidget(wid)
