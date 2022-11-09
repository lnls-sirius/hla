""" Static information about the PVs and colors """
from qtpy.QtGui import QColor

COLORS = {
    "light_green": QColor(0, 140, 0),
    "dark_green": QColor(20, 80, 10),
    "yellow": QColor(210, 205, 0),
    "red": QColor(207, 0, 0),
    "blue": QColor(130, 143, 255),
    "purple": QColor(148, 60, 255),
    "cyan": QColor(0, 187, 196),
    "gre_blu": QColor(0, 175, 175),
    "black": QColor(0, 0, 0),
    "orange": QColor(255, 150, 0),
    "btn_bg": "#77f2b6bc"
}

# Styles
# PRG (0)
# CCG (1 e 2)
PVS_CONFIG = {
    "Pump": {
        'prefix': 'LA-VA:H1IPS-',
        'iterations': [1, 16],
        'position': [
            [86, 90], [73, 90], [21.5, 68], [14.5, 70],
            [73, 72.5], [73, 43], [63, 72.5], [63, 55],
            [50, 65], [50, 49], [55.5, 15], [40, 72.5],
            [40, 55], [30.5, 72.5], [26, 49], [50, 15]
        ],
        'size': [5, 9],
        'list': {
            'coord': [2.5, 0],
            'size': [37, 65]
        }
    },
    "Vacuum": {
        'prefix': 'LA-VA:H1VGC-',
        'bar': ':LOGPrs-',
        'iterations': [1, 15],
        'position': [
            [93.5, 83], [79.75, 90], [93.5, 90],
            [3.5, 74], [72.25, 58], [4.5, 67],
            [63, 40], [53.5, 58], [51.5, 72.5],
            [57, 7], [40, 40], [60, 22],
            [30, 58], [47, 7], [43, 22]
        ],
        'size': [7, 9],
        'list': {
            'coord': [77.5, 0],
            'size': [23, 70]
        }
    },
    "Valve": {
        'prefix': 'LA-CN:H1MPS-1:Gval',
        'sufix': ['Opened', 'Closed'],
        'iterations': [1, 2],
        'position': [
            [85, 77.5], [22, 77.5]],
        'size': [10, 10]
    }
}

IPS_DETAILS = {
    "General": {
        'current': {
            'text': ':ReadI',
            'color': COLORS["purple"].name()
        },
        'voltage': {
            'text': ':ReadV',
            'color': COLORS["blue"].name()
        },
        'pressure': {
            'text': ':ReadP',
            'color': COLORS["cyan"].name()
        }
    },
    "Status": [
        {
            "title": "4KV",
            "status": ":4KVState",
            "control": ":V4K",
            "widget": "state"
        },
        {
            "title": "6KV",
            "status": ":6KVState",
            "control": ":V6K",
            "widget": "state"
        },
        {
            "title": "BAKE",
            "status": ":BkState",
            "control": ":Bk",
            "widget": "state"
        },
        {
            "title": "Local/\nRemote",
            "status": ":LoReState",
            "control": ":LoRe",
            "widget": "enum"
        },
        {
            "title": "State",
            "status": ":StWoState",
            "control": ":StartWork",
            "widget": "enum"
        },
        {
            "title": "FAILED",
            "status": ":ReadS.B4",
            "control": ":Reset",
            "widget": "button"
        }
    ],
    "Parameters": [
        {
            "title": "Enable",
            "status": ":ParSetEn",
            "control": ":Da",
            "widget": "state"
        },
        {
            "title": "IPS No.",
            "status": ":ReadJH",
            "control": ":SetJH",
            "widget": "edit"
        },
        {
            "title": "High Protect\nPressure(mA)",
            "status": ":ReadBH",
            "control": ":SetBH",
            "widget": "edit"
        },
        {
            "title": "Low Protect\nPressure(mA)",
            "status": ":ReadBA",
            "control": ":SetBA",
            "widget": "edit"
        },
        {
            "title": "Start Current\n(mA)",
            "status": ":ReadQD",
            "control": ":SetQD",
            "widget": "edit"
        },
        {
            "title": "Work Current\n(mA)",
            "status": ":ReadYX",
            "control": ":SetYX",
            "widget": "edit"
        }
    ]
}

VGC_DETAILS = {
    "Gauge": "Vacuum",
    "led": {
        'text': ':RdState',
        'sufix': {
            0: '.B3',
            1: ['.BB', '.BA'],
            2: ['.B7', '.B6']
        }
    },
    "Pressure<br/>Readback": ":RdPrs-",
    "Gauge<br/>Message": [":RdPrs-", "s"],
    "Gauge Status": {
        "title": "",
        "status": ":GaugeSts-",
        "control": ":GaugeOn-",
        "widget": "state"
    },
    "Setpoint": {
        "No.": [
            (9, 10), (1, 2), (5, 6)],
        "SP": {
            "title": "",
            "status": ":RdSP-",
            "control": ":SetSP-",
            "widget": "edit"
        },
        "SP-H": {
            "title": "",
            "status": ":RdSH-",
            "control": ":SetSH-",
            "widget": "edit"
        },
        "Relay Status": {
            "title": "",
            "status": ":RdRlySts-",
            "control": ":SetRlySts-",
            "widget": "enum"
        }
    },
    "Unit": ":RdUnit"
}

LEGEND = {
    'size': [8.5, 15],
    'CCG': [
        {
            'color': COLORS["light_green"],
            'text': 'Ok'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Warning'
        },
        {
            'color': COLORS["red"],
            'text': 'Alarm'
        }
    ],
    'PRG': [
        {
            'color': COLORS["light_green"],
            'text': 'Ok'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Warning'
        }
    ],
    'Gauge Status': [
        {
            'color': COLORS["light_green"],
            'text': 'ON'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Inconsistent'
        },
        {
            'color': COLORS["red"],
            'text': 'OFF'
        }
    ],
    'Relay Status': [
        {
            'text': 'ENABLE: Depends on the pressure\n and the setpoint value'
        },
        {
            'text': 'SET: Forces relay activation'
        },
        {
            'text': 'CLEAR: Disable the relay'
        }
    ]
}
