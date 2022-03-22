from re import S
import sys
import json
from epics import PV 
from PyQt5.QtCore import Qt
from qtpy.QtWidgets import QWidget, QLabel, QGridLayout, QGroupBox, QVBoxLayout, QTabWidget
from pydm.widgets import PyDMLabel, PyDMLineEdit, enum_button, PyDMEnumComboBox
from ..widgets import SiriusLedState
from siriushla.as_di_bpms.base import GraphWave

# Class Digital Beam Position Processor

class DigBeamPosProc(QWidget): 
    

    def __init__(self, parent=None): 
        """Init."""
        
        super().__init__(parent)

        self.setObjectName('LIApp')

        self.device_name = "LA-BI:BPM2"

        self.graph_data = {
            "Hilbert":{
                "Amplitude":{
                    "title": "Hilbert Amplitude",
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
                    "title": "Hilbert Phase",
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
                    "title": "FFT Amplitude",
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
                    "title": "FFT Phase",
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
            },
            "ADC Raw Waveform":{
                "title": "ADC Raw Waveform",
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
                    "CH2":{
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
            }
        }

        self.bpm_relData = '''
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
        
        self.bpm_OthData = {
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

    def _setupUi(self):

        self.setWindowTitle(self.device_name)

        lay = QGridLayout()
        lay.addLayout(self.display_header(), 0, 0, 1, 3)
        lay.addLayout(self.display_graph(), 1, 0, 2, 1)
        lay.addLayout(self.display_bpm_relData(), 1, 1, 1, 1)
        lay.addLayout(self.display_selectors(), 1, 2, 1, 1)
        lay.setAlignment(Qt.AlignTop)
        lay.setColumnStretch(0, 10)
        self.setLayout(lay)

    def display_header(self):
        
        layGrid = QGridLayout()

        trig_led = SiriusLedState(init_channel = self.device_name + ':' + "TRIGGER_STATUS")
        trig_led.setFixedSize(30, 30)
        layGrid.addWidget(trig_led, 0, 0, 1, 1)

        trig_label = QLabel("Trigger")
        trig_label.setAlignment(Qt.AlignCenter)
        layGrid.addWidget(trig_label, 1, 0, 1, 1)

        ioc_led = SiriusLedState(init_channel = self.device_name + ':' + 'HEART_BEAT')
        ioc_led.autoFillBackground()
        ioc_led.setFixedSize(30, 30)
        layGrid.addWidget(ioc_led, 0, 1, 1, 1)

        ioc_label = QLabel("IOC")
        ioc_label.setAlignment(Qt.AlignCenter)
        layGrid.addWidget(ioc_label, 1, 1, 1, 1)

        title_label = QLabel("DIGITAL BEAM POSITION PROCESSOR")
        title_label.setStyleSheet('''
               font-weight: bold;
               font-size: 20px;
            ''')
        title_label.setAlignment(Qt.AlignCenter)
        layGrid.addWidget(title_label, 0, 2, 2, 1)

        layGrid.setAlignment(Qt.AlignCenter)

        return layGrid

    def display_graph(self):

        mainlay = QVBoxLayout()
        tab = QTabWidget()

        graph_names = [
            "ADC Raw Waveform",
            "FFT",
            "Hilbert"
        ]

        for count in range(0, 3):
            vlay = QVBoxLayout()
            tab_content = QWidget()

            graph_data = self.graph_data.get(graph_names[count])

            if(len(graph_data.items()) != 2):
                vlay.addWidget(self.createGraph(graph_data), 10)
                tab_content.setLayout(vlay)
            else:
                county = 0 
                for data in graph_data:
                    title_label = QLabel(graph_data.get(data).get("title"))
                    title_label.setAlignment(Qt.AlignCenter)
                    title_label.setFixedHeight(15)
                    vlay.addWidget(title_label, 1)

                    vlay.addWidget(self.createGraph(graph_data.get(data)), 10)
                    county += 1
                tab_content.setLayout(vlay)
            tab.addTab(tab_content, graph_names[count])

        mainlay.addWidget(tab)

        return mainlay

    def createGraph(self, graph_data):
        graph = GraphWave()

        graph.setLabel('left', text = graph_data.get("labelY"), units = graph_data.get("unitY"))
        graph.setLabel('bottom', text = graph_data.get("labelX"), units = graph_data.get("unitX"))

        for channel in graph_data.get("channels"):
    
            channel_data = graph_data.get("channels").get(channel)
            graph.addChannel(
                y_channel = self.device_name + ':' + channel_data.get('path'),
                name = channel_data.get('name'), 
                color = channel_data.get('color'), 
                lineWidth= 1)

        graph.setMinimumWidth(600)
        graph.setMinimumHeight(250)

        return graph

    def data(self, channel, type):
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

    def display(self, title, info, x, y, type):
        
        layG = QGridLayout()
        group = QGroupBox()

        countx = 0
        county = 0

        if(type == 0):
            for text, channel in info.items():
                
                text_label = QLabel(text, self)
                layG.addWidget(text_label, countx, county)

                channel_label = self.data(channel, y)
                channel_label.showUnits = True
                layG.addWidget(channel_label, countx, county+1)

                countx += 1
        else:
            channel_label = self.data(info, y)
            channel_label.showUnits = True
            layG.addWidget(channel_label, x, y)       
        
        layG.setAlignment(Qt.AlignCenter)
        
        group.setTitle(title)
        group.setLayout(layG)

        return group

    def display_bpm_relData(self):
        countx = 0
        county = 0

        lay = QGridLayout()
        
        bpm_info = json.loads(self.bpm_relData)
        
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
                lay.addWidget(self.display(bpm["text"], bpm["info"], countx, county, 0), countx, county, 2, 1)
                countx += 2; 
            else:
                lay.addWidget(self.display(bpm["text"], bpm["info"], countx, county, 1), countx, county, 1, 1)
                countx += 1
            
            if(countx > 7): 
                countx = 0
                county += 2
        
        lay.setAlignment(Qt.AlignCenter)

        return lay

    def display_OthData(self):
        
        group = QGroupBox()
        lay = QGridLayout()

        countx = 0
        for text, channel in self.bpm_OthData.items():
        
            if(text!="Orientation"):
                text_label = QLabel(text, self)
                lay.addWidget(text_label, countx, 0, 1, 1)

                channel_label = self.data(channel, 1)
                channel_label.showUnits = True
                lay.addWidget(channel_label, countx, 1, 1, 1)
            else:
                text_label = QLabel(text, self)
                text_label.setAlignment(Qt.AlignCenter)
                lay.addWidget(text_label, countx, 0, 1, 2)
                selection = PyDMEnumComboBox(init_channel = self.device_name + ":" + channel)
                lay.addWidget(selection, countx+1, 0, 1, 2)
            countx += 1

        lay.setAlignment(Qt.AlignTop)
        group.setLayout(lay)

        return group

    def selectionItem(self, title, channel, orientation):
            group = QGroupBox()
            lay = QVBoxLayout()
            
            selection1 = enum_button.PyDMEnumButton(init_channel = self.device_name + ":" + channel)
            selection1.widgetType = 0
            selection1.orientation = orientation
            lay.addWidget(selection1, 0)
    
            group.setLayout(lay)
            group.setTitle(title)

            return group

    def display_selectors(self):

        layV = QVBoxLayout()

        selection_data = json.loads(self.selectors_data)
        count = 0
        for selection in selection_data:
            layV.addWidget(self.selectionItem(selection["text"], selection["info"], 2), 1)
            count += 1

        layV.addWidget(self.display_OthData(), 0)

        return layV
