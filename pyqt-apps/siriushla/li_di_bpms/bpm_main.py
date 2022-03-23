from re import S
import json
from PyQt5.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, QVBoxLayout, QTabWidget
from pydm.widgets import PyDMLabel, PyDMLineEdit, enum_button, PyDMEnumComboBox
from ..widgets import SiriusLedState
from siriushla.as_di_bpms.base import GraphWave

# Class Digital Beam Position Processor


class DigBeamPosProc(QWidget):


    #Contain all the graphic interface data
    def __init__(self, parent=None):
        """Init."""

        super().__init__(parent)

        self.setObjectName('LIApp')

        self.device_name = "LA-BI:BPM2"

        self.header = {
            "Trigger": "TRIGGER_STATUS",
            "IOC": "HEART_BEAT"
        }

        self.graph_allData = {
            "ADC Raw Waveform":{
                "title": "ADC",
                "labelX": "Waveform Index",
                "unitX": "",
                "labelY": "ADC Value",
                "unitY": "count",
                "channels":{
                    "CH1":{
                        "path": "CH1_ADX_WAVEFORM",
                        "name": "AntA",
                        "color": "#0000FF"
                    },
                    "CH2" :{
                        "path": "CH2_ADX_WAVEFORM",
                        "name": "AntB",
                        "color": "#FF0000"
                    },
                    "CH3":{
                        "path": "CH3_ADX_WAVEFORM",
                        "name": "AntC",
                        "color": "#008800"
                    },
                    "CH4":{
                        "path": "CH4_ADX_WAVEFORM",
                        "name": "AntD",
                        "color": "#FF00FF"
                    }
                }
            },
            "Hilbert":{
                "Amplitude":{
                    "title": "Amplitude",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Amplitude Value",
                    "unitY": "count",
                    "channels":{
                        "CH1":{
                            "path": "CH1_HIB_AMP_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2":{
                            "path": "CH2_HIB_AMP_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3":{
                            "path": "CH3_HIB_AMP_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4":{
                            "path": "CH4_HIB_AMP_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                },
                "Phase":{
                    "title": "Phase",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Phase Value",
                    "unitY": "count",
                    "channels":{
                        "CH1":{
                            "path": "CH1_HIB_PH_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2":{
                            "path": "CH2_HIB_PH_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3":{
                            "path": "CH3_HIB_PH_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4":{
                            "path": "CH4_HIB_PH_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                }
            },
            "FFT":{
                "Amplitude":{
                    "title": "Amplitude",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Amplitude Value",
                    "unitY": "count",
                    "channels":{
                        "CH1":{
                            "path": "CH1_FFT_AMP_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2":{
                            "path": "CH2_FFT_AMP_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3":{
                            "path": "CH3_FFT_AMP_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4":{
                            "path": "CH4_FFT_AMP_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                },
                "Phase":{
                    "title": "Phase",
                    "labelX": "Waveform Index",
                    "unitX": "",
                    "labelY": "Phase Value",
                    "unitY": "count",
                    "channels":{
                        "CH1":{
                            "path": "CH1_FFT_PH_WAVEFORM",
                            "name": "AntA",
                            "color": "#0000FF"
                        },
                        "CH2":{
                            "path": "CH2_FFT_PH_WAVEFORM",
                            "name": "AntB",
                            "color": "#FF0000"
                        },
                        "CH3":{
                            "path": "CH3_FFT_PH_WAVEFORM",
                            "name": "AntC",
                            "color": "#008800"
                        },
                        "CH4":{
                            "path": "CH4_FFT_PH_WAVEFORM",
                            "name": "AntD",
                            "color": "#FF00FF"
                        }
                    }
                }
            }
        }

        self.bpm_mainData = '''
            [
                {
                    "text" : "Max ADC",
                    "info" :
                    {
                            "A" : "CH1_MAXADC",
                            "B" : "CH2_MAXADC",
                            "C" : "CH3_MAXADC",
                            "D" : "CH4_MAXADC"
                    }
                },
                {
                    "text" : "Position",
                    "info" :
                    {
                        "X" : "POS_X",
                        "Y" : "POS_Y",
                        "S" : "POS_S"
                    }
                },
                {
                    "text" : "V",
                    "info" :
                    {
                        "A" : "POS_VA",
                        "B" : "POS_VB",
                        "C" : "POS_VC",
                        "D" : "POS_VD"
                    }
                },
                {
                    "text" : "Trigger Cnt",
                    "info" : "TRIGGER_CNT"
                },
                {
                    "text" : "Cycle",
                    "info" : "ACQ_TIME_USED"
                },
                {
                    "text" : "FFT",
                    "info" :
                    {
                        "Center" : "FFT_CENTER",
                        "Width" : "FFT_WIDTH"
                    }
                },
                {
                    "text" : "Hilbert",
                    "info" :
                    {
                        "Center" : "HIB_CENTER",
                        "Width" : "HIB_WIDTH"
                    }
                },
                {
                    "text" : "Gain",
                    "info" :
                    {
                        "X" : "POS_KX",
                        "Y" : "POS_KY",
                        "S" : "POS_KS"
                    }
                },
                {
                    "text" : "Offset",
                    "info" :
                    {
                        "X" : "POS_OX",
                        "Y" : "POS_OY"
                    }
                }
            ]
        '''

        self.bpm_secData = {
                "Attenuator": "FE_ATTEN_SP",
                "ADC Threshold" : "ADC_THD",
                "Orientation" : "BPM_STRIP"
            }

        self.selectors_data = '''
            [
                {
                    "text" : "Trigger Mode",
                    "info" : "ACQ_TRIGGER"
                },
                {
                    "text" : "Position Algorithm",
                    "info" : "POS_ALG"
                }
            ]'''

        self._setupUi()

    # Build the graphic interface
    def _setupUi(self):

        self.setWindowTitle(self.device_name)

        ifGlay = QGridLayout()
        ifGlay.addLayout(self.display_header(), 0, 0, 1, 3)
        ifGlay.addLayout(self.display_graph(), 1, 0, 2, 1)
        ifGlay.addLayout(self.display_mainData(), 1, 1, 1, 1)
        ifGlay.addLayout(self.display_selectors(), 1, 2, 1, 1)
        ifGlay.setAlignment(Qt.AlignTop)
        ifGlay.setColumnStretch(0, 10)
        self.setLayout(ifGlay)

    # Display the header of the interface
    def display_header(self):

        hdGlay = QGridLayout()

        title_lb = QLabel("DIGITAL BEAM POSITION PROCESSOR")
        title_lb.setStyleSheet('''
               font-weight: bold;
               font-size: 20px;
            ''')
        title_lb.setAlignment(Qt.AlignCenter)
        hdGlay.addWidget(title_lb, 0, 2, 2, 1)

        countx = 0

        for led_lb, led_channel in self.header.items():
            trig_led = SiriusLedState(init_channel = self.device_name + ':' + led_channel)
            trig_led.setFixedSize(30, 30)
            hdGlay.addWidget(trig_led, 0, countx, 1, 1)

            trig_lb = QLabel(led_lb)
            trig_lb.setAlignment(Qt.AlignCenter)
            hdGlay.addWidget(trig_lb, 1, countx, 1, 1)

            countx += 1

        hdGlay.setAlignment(Qt.AlignCenter)

        return hdGlay

    # Build a graph widget
    def createGraph(self, graph_data):
        graphPlot = GraphWave()

        graphPlot.graph.title = graph_data.get("title")
        graphPlot.setLabel('left', text = graph_data.get("labelY"), units = graph_data.get("unitY"))
        graphPlot.setLabel('bottom', text = graph_data.get("labelX"), units = graph_data.get("unitX"))

        for channel in graph_data.get("channels"):

            channel_data = graph_data.get("channels").get(channel)
            graphPlot.addChannel(
                y_channel = self.device_name + ':' + channel_data.get('path'),
                name = channel_data.get('name'),
                color = channel_data.get('color'),
                lineWidth= 1)

        graphPlot.setMinimumWidth(600)
        graphPlot.setMinimumHeight(250)

        return graphPlot

    # Display the graph tabs and all their contents
    def display_graph(self):

        gpVlay = QVBoxLayout()
        tab = QTabWidget()

        for graph_name in self.graph_allData:
            tablay = QVBoxLayout()
            tab_content = QWidget()

            graph_item = self.graph_allData.get(graph_name)

            if(len(graph_item.items()) != 2):
                tablay.addWidget(self.createGraph(graph_item), 10)
                tab_content.setLayout(tablay)
            else:
                for data in graph_item:
                    tablay.addWidget(self.createGraph(graph_item.get(data)), 10)

                tab_content.setLayout(tablay)
            tab.addTab(tab_content, graph_name)

        gpVlay.addWidget(tab)

        return gpVlay

    # Get data channel info
    def dataItem(self, channel, type):
        if(type == 0):
            channelInfo = PyDMLabel(
                parent=self,
                init_channel= self.device_name + ':' + channel)
        elif(type == 1 or type == 2 or type == 4):
            channelInfo = PyDMLineEdit(
                parent=self,
                init_channel= self.device_name + ':' + channel)
        else:
            channelInfo = QLabel("Error", self)

        return channelInfo

    # Build a data widget
    def display_data(self, title, info, x, y, type):

        layGrid = QGridLayout()
        group = QGroupBox()

        countx = 0
        county = 0

        if(type == 0):
            for text, channel in info.items():

                text_lb = QLabel(text, self)
                layGrid.addWidget(text_lb, countx, county)

                channel_lb = self.dataItem(channel, y)
                channel_lb.showUnits = True
                layGrid.addWidget(channel_lb, countx, county+1)

                countx += 1
        else:
            channel_lb = self.dataItem(info, y)
            channel_lb.showUnits = True
            layGrid.addWidget(channel_lb, x, y)

        layGrid.setAlignment(Qt.AlignCenter)

        group.setTitle(title)
        group.setLayout(layGrid)

        return group

    # Display all main data widgets
    def display_mainData(self):
        countx = 0
        county = 0

        mdGlay = QGridLayout()

        bpm_info = json.loads(self.bpm_mainData)

        for bpm in bpm_info:

            if(bpm["text"] == " "):
                countx += 1
            elif (bpm["text"] == "Max ADC"
                or bpm["text"] == "V"
                or bpm["text"] == "Position"
                or bpm["text"] == "FFT"
                or bpm["text"] == "Hilbert"
                or bpm["text"] == "Gain"
                or bpm["text"] == "Offset"):
                mdGlay.addWidget(self.display_data(bpm["text"], bpm["info"], countx, county, 0), countx, county, 2, 1)
                countx += 2
            else:
                mdGlay.addWidget(self.display_data(bpm["text"], bpm["info"], countx, county, 1), countx, county, 1, 1)
                countx += 1

            if(countx > 7):
                countx = 0
                county += 2

        mdGlay.setAlignment(Qt.AlignCenter)

        return mdGlay

    # Build the secondary data widget
    def display_secData(self):

        group = QGroupBox()
        scGlay = QGridLayout()

        countx = 0
        for text, channel in self.bpm_secData.items():

            if(text!="Orientation"):
                text_lb = QLabel(text, self)
                scGlay.addWidget(text_lb, countx, 0, 1, 1)

                channel_lb = self.dataItem(channel, 1)
                channel_lb.showUnits = True
                scGlay.addWidget(channel_lb, countx, 1, 1, 1)
            else:
                text_lb = QLabel(text, self)
                text_lb.setAlignment(Qt.AlignCenter)
                scGlay.addWidget(text_lb, countx, 0, 1, 2)
                selection = PyDMEnumComboBox(init_channel = self.device_name + ":" + channel)
                scGlay.addWidget(selection, countx+1, 0, 1, 2)
            countx += 1

        scGlay.setAlignment(Qt.AlignTop)
        group.setLayout(scGlay)

        return group

    # Build a selection widget
    def selectionItem(self, title, channel, orientation):
        group = QGroupBox()
        lay = QVBoxLayout()

        selector = enum_button.PyDMEnumButton(init_channel = self.device_name + ":" + channel)
        selector.widgetType = 0
        selector.orientation = orientation
        lay.addWidget(selector, 0)

        group.setLayout(lay)
        group.setTitle(title)

        return group

    # Display the selector and the secondary data
    def display_selectors(self):

        slVlay = QVBoxLayout()

        selection_data = json.loads(self.selectors_data)
        count = 0
        for selector in selection_data:
            slVlay.addWidget(self.selectionItem(selector["text"], selector["info"], 2), 1)
            count += 1

        slVlay.addWidget(self.display_secData(), 0)

        return slVlay
