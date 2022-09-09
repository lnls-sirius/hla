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
# PRG (0)
# CCG (1 e 2)
PVS_CONFIG = {
    "Vacuum": {
        'prefix': 'LA-VA:H1VGC-',
        'iterations': [1, 15],
        # 'unit': ':RdUnit',
        'text': ':RdPrs-',
        'color': COLORS["light_green"].name(),
        'led': {
            'text': ':RdState',
            'sufix': {
                0: '.B3',
                1: ['.BB', '.BA'],
                2: ['.B7', '.B6']
            }
        },
        'position': [
            [20, 0], [00, 0], [00, 0],
            [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0]
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
            [40, 0], [50, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0], [0, 0],
            [0, 0], [0, 0], [0, 0], [0, 0],
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
            [50, 20], [50, 10]],
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
