''' Diagnostic Interface of the LINAC's Screen'''
import os as _os
from qtpy.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets  import QGroupBox, QHBoxLayout, QVBoxLayout, \
    QWidget, QFrame, QLabel, QGridLayout, QRadioButton, QStackedWidget
from pydm.widgets import PyDMEnumComboBox, PyDMLabel, PyDMPushButton, \
    PyDMWaveformPlot, PyDMSpinbox, PyDMImageView
import qtawesome as qta
from ..util import get_appropriate_color
from ..widgets import SiriusMainWindow, PyDMLedMultiChannel, PyDMStateButton
from .util import DEVICES, SCREENS_PANEL, SCREENS_INFO, HEADER, \
    GRAPH, SCREEN

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
        self.image_container.setMinimumSize(750, 250)
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
                self.image_container.height())
        )
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
        # elif widType == 4:
        #     widget = PyDMStateButton(
        #         init_channel=pvName)
        #     widget._on = 'IL1'
        #     widget._off = 'IH1'
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

    def screenBasicInfo(self, device, label, pv_name, pos, sm_glay):
        ''' Set one screen basic information '''
        pv_name = 'MOTOR:'+pv_name
        sm_glay.addWidget(
            QLabel(label),
            pos[0], pos[1])
        if pv_name in ['MOTOR:MODE', 'MOTOR:AL']:
            sm_glay.addWidget(
                self.setWidgetType(0, device, pv_name, False),
                pos[0], pos[1]+1)
        else:
            sm_glay.addWidget(
                self.setWidgetType(1, device, pv_name, False),
                pos[0], pos[1]+1)

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
            self.setWidgetType(4, device, "MOTOR:"+pvList[1], False))
        return lo_hlay

    def singleScreenInfo(self, device):
        ''' Display selected screen information '''
        group = QGroupBox()
        sm_glay = QGridLayout()
        pos = [0, 0]
        for label, channel in SCREENS_INFO.get('content').items():
            self.screenBasicInfo(device, label, channel, pos, sm_glay)
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
        graph_plot.setMinimumWidth(100)
        graph_plot.setMinimumHeight(100)

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

    def setRBVWidget(self, device, pv_name, label):
        rbv_hlay = QHBoxLayout()
        rbv_hlay.addWidget(
            QLabel(label),
            alignment=Qt.AlignRight)
        for item in range(0, 2):
            pvName = "ROI:" + pv_name[item]
            if 'Min' in pvName and 'RBV' in pvName:
                widget = self.setWidgetType(3, device, pvName, False)
            else:
                widget = self.setWidgetType(0, device, pvName, False)
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
                self.setRBVWidget(device, channel, label))

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
        elif stackType == 2:
            self.stackScreen = stack

    def buildStacks(self, stackType):
        stack = QStackedWidget()
        for device in DEVICES:
            stack.addWidget(
                self.getStackItem(stackType, device))
        self.saveStack(stack, stackType)
        return stack

    def singleScreen(self, device):
        group = QGroupBox()
        ss_vlay = QVBoxLayout()

        ss_vlay.addWidget(
            PyDMImageView(
                image_channel=self.getPvName(device, SCREEN['Screen']['data']),
                width_channel=self.getPvName(device, SCREEN['Screen']['width'])))

        for title, item in SCREEN['info'].items():
            if title == 'LED':
                ss_vlay.addLayout(
                    self.setLightOpt(device, item, title))
            # elif title == 'Counter':


        group.setLayout(ss_vlay)
        # group.setTitle(SCREEN[0])
        return group

    def _setupUi(self):
        '''Build the graphic interface'''
        wid = QWidget(self)
        if_glay = QGridLayout()

        if_glay.addLayout(self.header(), 0, 0, 1, 12)
        if_glay.addWidget(self.imageViewer(), 1, 4, 3, 8)
        if_glay.addWidget(self.buildStacks(0), 1, 2, 3, 2)
        if_glay.addWidget(self.screenPanel(), 1, 0, 3, 2)
        if_glay.addWidget(self.buildStacks(2), 4, 0, 3, 6)
        if_glay.addWidget(self.buildStacks(1), 4, 6, 3, 6)

        wid.setLayout(if_glay)
        self.setCentralWidget(wid)
