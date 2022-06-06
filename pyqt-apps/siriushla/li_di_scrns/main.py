''' Diagnostic Interface of the LINAC's Screen'''
import os as _os
from qtpy.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets  import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QFrame, QLabel, QGridLayout, QRadioButton, QStackedWidget
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMPushButton, \
    PyDMWaveformPlot, PyDMSpinbox, PyDMImageView, PyDMLineEdit
import qtawesome as qta
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, PyDMLedMultiChannel
from .util import DEVICES, SCREENS_PANEL, SCREENS_INFO, HEADER, \
    GRAPH, SCREEN, SCREEN_CONFIG
from .motorBtn import MotorBtn

class LiBeamProfile(SiriusMainWindow):
    ''' Linac Profile Screen '''

    def __init__(self, prefix='', parent=None):
        '''Contain all the graphic interface data'''
        super().__init__(parent)
        self.prefix = prefix + ('-' if prefix else '')

        self.setObjectName('LIApp')
        color = get_appropriate_color('LI')

        self.device_name = 'LA-BI'

        self.setWindowIcon(qta.icon('mdi.camera-metering-center', color=color))
        self.setWindowTitle(self.device_name)
        self.image_container = QLabel()
        self.pixmap = QPixmap(_os.path.join(
                _os.path.abspath(_os.path.dirname(__file__)), "linac.png"))
        self.stackScreens = QStackedWidget()
        self.stackScreen = QStackedWidget()
        self.stackGraphs = QStackedWidget()
        self._setupUi()

    def getPvName(self, device, pv_name):
        ''' Build PV name '''
        return self.device_name + ':' + device + ":" + pv_name

    def resizeEvent(self, event):
        ''' Resize Image'''
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height())
        )
        SiriusMainWindow.resizeEvent(self, event)

    def header(self):
        ''' Display the header'''
        hd_hlay = QHBoxLayout()
        title = QLabel("<h2>Screen View</h2>")
        hd_hlay.addWidget(title, alignment=Qt.AlignCenter)
        hd_hlay.setStretch(0, 4)
        for label, channel in HEADER.items():
            hd_hlay.addWidget(
                self.setWidgetType(2, "PRF:MOTOR", channel, label),
                alignment=Qt.AlignRight)
        return hd_hlay

    def imageViewer(self):
        ''' Display the image'''
        self.image_container.setPixmap(
            self.pixmap.scaled(
                self.image_container.width(),
                self.image_container.height()))
        self.image_container.setMinimumSize(500, 250)
        self.image_container.setMaximumSize(1500, 250)
        self.image_container.setAlignment(Qt.AlignCenter)
        return self.image_container

    def setWidgetType(self, widType, device, pv_name, label):
        ''' Get widget type '''
        pvName = self.getPvName(device, pv_name)
        if widType == 0:
            widget = PyDMLabel(self,
                init_channel=pvName)
            widget.showUnits = True
            widget.setAlignment(Qt.AlignCenter)
        elif widType == 1:
            ch2vals = {pvName: 0}
            widget = PyDMLedMultiChannel(self)
            widget.set_channels2values(ch2vals)
        elif widType == 2:
            widget = PyDMPushButton(self,
                        init_channel=pvName,
                        label=label,
                        pressValue=0)
        elif widType == 3:
            widget = PyDMSpinbox(
                init_channel=pvName)
            widget.showStepExponent = False
        elif widType == 4:
            widget = PyDMLineEdit(
                init_channel=pvName)
            widget.setAlignment(Qt.AlignCenter)
        elif widType == 5:
            widget = MotorBtn(
                init_channel=pvName)
        else:
            widget = QLabel("Error: Unknown device")
        return widget

    def radioBtnClick(self):
        ''' Action on radio button change '''
        radioButton = self.sender()
        if radioButton.isChecked():
            self.selected_device = radioButton.device
            deviceIndex = DEVICES.index(self.selected_device)
            self.stackScreens.setCurrentIndex(deviceIndex)
            self.stackScreen.setCurrentIndex(deviceIndex)
            self.stackGraphs.setCurrentIndex(deviceIndex)


    def radioSetBtn(self, device):
        ''' Get the one radio button '''
        radiobutton = QRadioButton(device)
        radiobutton.device = device
        radiobutton.toggled.connect(self.radioBtnClick)
        if device == DEVICES[0]:
            radiobutton.setChecked(True)
        return radiobutton

    def screenHeader(self, device):
        ''' Display screen panel header '''
        mi_hlay = QHBoxLayout()
        for text in SCREENS_PANEL.get('labels'):
            label = QLabel('<h4>'+text+'</h4>')
            label.setAlignment(Qt.AlignCenter)
            mi_hlay.addWidget(label, alignment=Qt.AlignCenter)
        return mi_hlay

    def screenInfo(self, device):
        ''' Display information of one screen in screen panel '''
        mi_hlay = QHBoxLayout()
        pvList = SCREENS_PANEL.get('content')
        pv_name = 'MOTOR'+":"

        mi_hlay.addWidget(
            self.radioSetBtn(device), alignment=Qt.AlignCenter)

        for item in range(0, len(pvList)):
            mi_hlay.addWidget(
                self.setWidgetType(item, device, pv_name+pvList[item], False),
                alignment=Qt.AlignCenter)

        return mi_hlay

    def screenPanel(self):
        ''' Display the screen panel'''
        group = QGroupBox()
        am_vlay = QVBoxLayout()
        am_vlay.addLayout(self.screenHeader(SCREENS_PANEL.get('title')))
        for device in DEVICES:
            am_vlay.addLayout(self.screenInfo(device))

        group.setTitle(SCREENS_PANEL.get('title'))
        group.setLayout(am_vlay)
        return group

    def setScreenSelectionBtns(self, device, pv_name, labels, counter):
        ''' Set the button label for the position of the screen '''
        if pv_name == 'POS5.PROC' and device != 'PRF5':
            return False
        elif device == 'PRF5':
            if pv_name == 'POS4.PROC':
                return labels[counter+1]
            if pv_name == 'POS5.PROC':
                return labels[counter-1]
        elif pv_name == 'POS3.PROC':
            if device == 'PRF4':
                return labels[counter+2]
        return labels[counter]

    def setScreenSelection(self, selectionInfo, device):
        ''' Display the screen position selection menu '''

        widget = QFrame()
        ms_vlay = QVBoxLayout()
        ms_vlay.addWidget(
            PyDMLabel(
                init_channel=self.getPvName(
                                        device, 'MOTOR:' + selectionInfo.get('selected'))),
            alignment=Qt.AlignCenter)
        for counter in range(0, len(selectionInfo.get('content'))):
            pv_name = selectionInfo.get('content')[counter]
            labels = selectionInfo.get('labels')
            label = self.setScreenSelectionBtns(device, pv_name, labels, counter)
            if label != False:
                ms_vlay.addWidget(
                    PyDMPushButton(
                        init_channel=self.getPvName(device, 'MOTOR:' + pv_name),
                        label=label))
        widget.setStyleSheet('''QFrame{
                border-radius: 0.5em;
                border: 0.1em solid #ff8b98;}''')
        widget.setLayout(ms_vlay)
        return widget

    def screenBasicInfo(self, device, label, pv_name):
        ''' Set one screen basic information '''
        bi_hlay = QHBoxLayout()
        bi_hlay.addWidget(
            QLabel(label),
            alignment=Qt.AlignCenter)
        if label in ['Limit Mode', 'Motor Code', 'Counter']:
            widType = 0
        elif label == "Centroid Threshold":
            widType = 4
        else:
            widType = 1
        bi_hlay.addWidget(
            self.setWidgetType(widType, device, pv_name, False))
        return bi_hlay

    def setZeroOpt(self, item, device):
        ''' Display Zero Operation Component'''
        zo_hlay = QHBoxLayout()
        zo_hlay.addWidget(
            QLabel(item["title"]))
        count = 0
        for label, pv_name in item["content"].items():
            zo_hlay.addWidget(
                self.setWidgetType(2, device, "MOTOR:"+pv_name, label))
            count += 1
        return zo_hlay

    def setLightOpt(self, device, pvList, title):
        lo_hlay = QHBoxLayout()
        lo_hlay.addWidget(
            QLabel(title))
        lo_hlay.addWidget(
            self.setWidgetType(1, device, "MOTOR:"+pvList[0], False))
        lo_hlay.addWidget(
            self.setWidgetType(5, device, "MOTOR:"+pvList[1], False))
        return lo_hlay

    def singleScreenInfo(self, device):
        ''' Display selected screen information '''
        group = QGroupBox()
        sm_glay = QGridLayout()
        pos = [0, 0]
        for label, channel in SCREENS_INFO.get('content').items():
            sm_glay.addLayout(
                self.screenBasicInfo(device, label, 'MOTOR:'+channel),
                pos[0], pos[1])
            pos[0]+=1

        sm_glay.addLayout(
            self.setZeroOpt(
                SCREENS_INFO.get('special_content')[1], device),
            pos[0], pos[1], 1, 3)

        pos[0] = 0

        sm_glay.addWidget(
            self.setScreenSelection(
                SCREENS_INFO.get('special_content')[0], device),
            pos[0], pos[1]+2, 5, 1)

        group.setTitle(SCREENS_INFO.get('title'))
        group.setLayout(sm_glay)
        return group

    def createGraph(self, device, graph_data, title):
        '''Build a graph widget'''

        graph_plot = PyDMWaveformPlot(background="#ffffff")
        graph_plot.setTitle(title)
        graph_plot.setLabel(
            'left',
            text=graph_data.get("labelY"))
        graph_plot.setLabel(
            'bottom',
            text=graph_data.get("labelX"))
        graph_plot.addChannel(
            y_channel=self.getPvName(device, graph_data['channel']['centroid']),
            color="#ff8b98",
            lineWidth=1)
        graph_plot.addChannel(
            y_channel=self.getPvName(device, graph_data['channel']['data']),
            color="#ff0000",
            lineWidth=1)
        graph_plot.setMinimumSize(50, 100)

        return graph_plot

    def graphInfo(self, device, graph_info):
        gi_hlay = QHBoxLayout()
        for label, channel in graph_info.items():
            gi_hlay.addWidget(
                QLabel(label),
                alignment=Qt.AlignRight)
            if label == 'Coefficient':
                gi_hlay.addWidget(
                    self.setWidgetType(3, device, channel, False),
                    alignment=Qt.AlignCenter)
            else:
                gi_hlay.addWidget(
                    self.setWidgetType(0, device, channel, False),
                    alignment=Qt.AlignCenter)
        return gi_hlay

    def setRBVObj(self, device, pv_name, label, pv_prefix):
        rbv_hlay = QHBoxLayout()
        rbv_hlay.addWidget(
            QLabel(label),
            alignment=Qt.AlignRight)
        for item in range(0, 2):
            pvName = pv_prefix + pv_name[item]
            if 'RBV' not in pvName:
                if label in ['Gain', 'Exposure']:
                    widType = 4
                else:
                    widType = 3
            else:
                widType = 0
            widget = self.setWidgetType(widType, device, pvName, False)
            widget.setMaximumWidth(75)
            if item == 0:
                rbv_hlay.addWidget(
                        widget,
                        alignment=Qt.AlignRight)
                sepLabel = QLabel("/")
                sepLabel.setFixedWidth(2)
                rbv_hlay.addWidget(
                    sepLabel,
                    Qt.AlignCenter)
            else:
                rbv_hlay.addWidget(
                        widget,
                        alignment=Qt.AlignLeft)
        return rbv_hlay

    def roiInfo(self, device, roi_data, title):
        group = QGroupBox()
        ri_hlay = QHBoxLayout()
        for label, channel in roi_data.items():
            ri_hlay.addLayout(
                self.setRBVObj(device, channel, label, 'ROI:'))

        group.setLayout(ri_hlay)
        group.setTitle(title)
        return group

    def getGraphs(self, device):
        group = QGroupBox()
        ag_vlay = QVBoxLayout()
        for title, graph_data in GRAPH.items():
            if title == "ROI":
                ag_vlay.addWidget(self.roiInfo(device, graph_data, title))
            else:
                ag_vlay.addWidget(self.createGraph(device, graph_data, title))
                ag_vlay.addLayout(self.graphInfo(device, graph_data['info']))

        group.setLayout(ag_vlay)
        group.setTitle("Projections")
        return group

    def getStackItem(self, stackType, device):
        if stackType == 0:
            return self.singleScreenInfo(device)
        elif stackType == 1:
            return self.getGraphs(device)
        elif stackType == 2:
            return self.singleScreen(device)

    def saveStack(self, stack, stackType):
        if stackType == 0:
            self.stackScreens = stack
        elif stackType == 1:
            self.stackGraphs = stack
            self.stackGraphs.setMaximumWidth(1250)
        elif stackType == 2:
            self.stackScreen = stack

    def buildStacks(self, stackType):
        stack = QStackedWidget()
        for device in DEVICES:
            stack.addWidget(
                self.getStackItem(stackType, device))
        self.saveStack(stack, stackType)
        return stack

    def setScreenConfig(self, device):
        sc_hlay = QHBoxLayout()
        for title, item in SCREEN_CONFIG.items():
            if(item == "RESET.PROC"):
                sc_hlay.addWidget(
                    self.setWidgetType(2, device, "CAM:"+item, title))
            else:
                sc_hlay.addLayout(
                    self.screenBasicInfo(device, title, "CAM:"+item))
        return sc_hlay


    def setScreenInfo(self, device):
        si_hlay = QHBoxLayout()
        for title, item in SCREEN['info'].items():
            if title == 'LED':
                si_hlay.addLayout(
                    self.setLightOpt(device, item, title))
            elif title in ['Gain', 'Exposure']:
                si_hlay.addLayout(
                    self.setRBVObj(device, item, title, 'CAM:'))
            else:
                si_hlay.addLayout(
                    self.screenBasicInfo(device, title, item))
        return si_hlay

    def singleScreen(self, device):
        group = QGroupBox()
        ss_vlay = QVBoxLayout()

        ss_vlay.addWidget(
            PyDMImageView(
                image_channel=self.getPvName(device, SCREEN['Screen']['data']),
                width_channel=self.getPvName(device, SCREEN['Screen']['width'])))
        ss_vlay.addLayout(
            self.setScreenConfig(device))
        ss_vlay.addLayout(
            self.setScreenInfo(device))

        group.setLayout(ss_vlay)
        return group

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0, 1, 10)
        if_glay.addWidget(self.buildStacks(0), 1, 2, 3, 2)
        if_glay.addWidget(self.imageViewer(), 1, 4, 3, 6)
        if_glay.addWidget(self.screenPanel(), 1, 0, 3, 2)
        if_glay.addWidget(self.buildStacks(2), 4, 0, 3, 7)
        if_glay.addWidget(self.buildStacks(1), 4, 7, 3, 3)
        wid.setLayout(if_glay)
        self.setCentralWidget(wid)
