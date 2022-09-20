from qtpy.QtGui import QColor

COLORS = {
    "light_green": QColor(0, 140, 0),
    "dark_green": QColor(20, 80, 10),
    "yellow": QColor(210, 205, 0),
    "red": QColor(207, 0, 0),
    "blue": QColor(130, 143, 255),
    "purple": QColor(186, 130, 255),
    "cyan": QColor(0, 187, 196),
    "btn_bg": "#77f2b6bc"
}

# Styles
# PRG (0)
# CCG (1 e 2)
PVS_CONFIG = {
    "Vacuum": {
        'prefix': 'LA-VA:H1VGC-',
        'iterations': [1, 15],
        'text': ':RdPrs-',
        'color': '',
        'led': {
            'text': ':RdState',
            'sufix': {
                0: '.B3',
                1: ['.BB', '.BA'],
                2: ['.B7', '.B6']
            }
        },
        'position': [
            [93.5, 83], [53.5, 58], [93.5, 90],
            [79.75, 90], [57, 7], [4.5, 67],
            [3.5, 74], [40, 40], [51.5, 72.5],
            [72.25, 58], [30, 58], [60, 22],
            [63, 40], [47, 7], [43, 22]
        ],
        'size': [7, 9],
        'list': {
            'coord': [77.5, 0],
            'size': [23, 70]
        }
    },
    "Pump": {
        'prefix': 'LA-VA:H1IPS-',
        'iterations': [1, 16],
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
        },
        'position': [
            [86, 90], [73, 90], [21.5, 68], [14.5, 70],
            [73, 72.5], [73, 43], [63, 72.5], [63, 55],
            [50, 65], [50, 49], [55.5, 15], [40, 72.5],
            [40, 55], [30.5, 72.5], [26, 49], [50, 15]
        ],
        'size': [5, 9],
        'list': {
            'coord': [2.5, 0],
            'size': [30, 60] 
        }
    },
    "Valve": {
        'prefix': 'LA-CN:H1MPS-1:Gval',
        'sufix': ['Opened', 'Closed'],
        'iterations': [1, 2],
        'position': [
            [22, 77.5], [85, 77.5]],
        'size': [10, 10]
    }
}

IPS_DETAILS = {
    "Status": [
        {
            "title": "4KV",
            "name": ":4KVState",
            "widget": "button"
        },
        {
            "title": "6KV",
            "name": ":6KVState",
            "widget": "button"
        },
        {
            "title": "BAKE",
            "name": ":BkState",
            "widget": "button"
        },
        {
            "title": "Local/Remote",
            "name": ":LoReState",
            "widget": "button"
        },
        {
            "title": "State",
            "name": "StWoState",
            "widget": "button"
        },
        {
            "name": ":ReadS",
            "widget": "led"
        }
    ],
    "Parameter": [
        {
            "title": "IPS No.",
            "name": ":SetJH",
            "widget": "edit"
        },
        {
            "title": "High Protect Pressure",
            "name": ":SetBH",
            "widget": "edit"
        },
        {
            "title": "Low Protect Pressure",
            "name": ":SetBA",
            "widget": "edit"
        },
        {
            "title": "Start Current",
            "name": ":SetQD",
            "widget": "edit"
        },
        {
            "title": "Work Current",
            "name": ":SetYX",
            "widget": "edit"
        },
        {
            "name": ":ParSetEn",
            "widget": "button"
        }
    ]
}

# VGC_DETAILS = {
#     "Gauge": "",
#     "Pressure Readback": ":RdPrs-"+n,
#     "Pressure Readback": ":RdPrs-"+n+"s",
#     "On/Off - Control": ":GaugeOn-"+n,
#     "On/Off - RB": ":GaugeSts-"+n,
#     "led": {
#         'text': ':RdState',
#         'sufix': {
#             0: '.B3',
#             1: ['.BB', '.BA'],
#             2: ['.B7', '.B6']
#         }
#     },
#     "SP": {
#         "No.": [
#             (1, 2), (5, 6), (9, 10)],
#         "SP": (":SetSP-", ":RdSP-"),
#         "SP-H": (":SetSH-", ":RdSH-")
#     },
#     "relay": (":SetRlySts-"+n, ":RdRlySts-"+n),
#     "unit": ":RdUnit"
# }

LEGEND = {
    'size': [8.5, 15],
    'Gauge Status': [
        {
            'color': COLORS["light_green"],
            'text': 'ON'
        },
        {
            'color': COLORS["dark_green"],
            'text': 'OFF'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Inconsistent'
        }
    ],
    'Relay Status': [
        {
            'text': 'ENABLE: Depends on the pressure and\nthe setpoint value'
        },
        {
            'text': 'SET: Forces relay activation'
        },
        {
            'text': 'CLEAR: Disable the relay'
        }
    ],
    'IPS Control': [
        {
            'color': COLORS["light_green"],
            'text': 'ON / Remote'
        },
        {
            'color': COLORS["dark_green"],
            'text': 'OFF / Local'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Inconsistent'
        }
    ],
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
    ]
}
