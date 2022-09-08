from qtpy.QtGui import QColor

COLORS = {
    "light_green": QColor(0, 140, 0),
    "dark_green": QColor(20, 80, 10),
    "yellow": QColor(210, 205, 0),
    "red": QColor(207, 0, 0),
    "gray": QColor(169, 169, 169),
    "blue": QColor(0, 0, 115),
    "purple": QColor(75, 0, 130)
}

# Styles
# CCG (1 e 2)
# PRG (3)
PVS_CONFIG = {
    "Vacuum": {
        'prefix': 'LA-VA:H1VGC-',
        'iterations': [1, 5],
        'unit': ':RdUnit',
        'value': {
            'text': ':RdPrs-',
            'iterations': [1, 3]
        },
        'led': {
            'text': ':RdState',
            1: ['.BB', '.BA'],
            2: ['.B7', '.B6'],
            3: '.B3'
        },
        'position': [
            [[0, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0]],
            [[0, 0], [0, 0], [0, 0]]
        ],
        'size': {
            "V": [8, 17],
            "H": [15, 8]
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
        'position': [
            [0, 0], [0, 20], [0, 40], [0, 60],
            [0, 40], [0, 50], [0, 60], [0, 70],
            [0, 80], [0, 90], [0, 100], [0, 0],
            [0, 0], [0, 0], [0, 0], [0, 0]
        ],
        'size': {
            "V": [8, 17],
            "H": [13, 12]
        }
    },
    "Valve": {
        'prefix': 'LA-CN:H1MPS-1:Gval',
        'sufix': ['Opened', 'Closed'],
        'iterations': [1, 2],
        'position': [
            [20, 20], [10, 10]],
        'size': [10, 10]
    }
}

LEGEND = {
    'Gauge Status': [
        {
            'color': COLORS["dark_green"],
            'text': 'ON'
        },
        {
            'color': COLORS["light_green"],
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
            'color': COLORS["dark_green"],
            'text': 'ON / Remote'
        },
        {
            'color': COLORS["light_green"],
            'text': 'OFF / Local'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Inconsistent'
        }
    ],
    'CCG': [
        {
            'color': COLORS["dark_green"],
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
            'color': COLORS["dark_green"],
            'text': 'Ok'
        },
        {
            'color': COLORS["yellow"],
            'text': 'Warning'
        }
    ]
}

# MULTI_LED_CONFIG = {
#     {
#         self.prefix+ch_coup: {'comp': 'ne', 'value': pvs},
#         self.prefix+ch_coup: {'comp': 'ne', 'value': pvs},
#         self.prefix+ch_coup: {'comp': 'ne', 'value': pvs}
#     }
