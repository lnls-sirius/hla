GREEN = '#00FF00'
RED = '#FF0000'
BLUE = '#0000FF'
YELLOW = '#FFFF00'

COLORS = [RED, GREEN, BLUE, YELLOW]

# Styles
# CCG (1 e 2)
# PRG (3)
PVS_CONFIG = {
    "Vacuum": {
        'prefix': 'LA-VA:H1VGC-0',
        'iterations': [1, 5],
        'unit': ':RdUnit',
        'value': {
            'text': ':RdPrs-',
            'iterations': [1, 3]
        },
        'led': {
            'text': ':RdState',
            1: {
                'up': '.BB',
                'low': '.BA'
            },
            2: {
                'up': '.B7',
                'low': '.B6'
            },
            3: '.B3'
        },
        'position': [
            [(), (), ()],
            [(), (), ()],
            [(), (), ()],
            [(), (), ()],
            [(), (), ()]
        ]
    },
    "Pump": {
        'prefix': 'LA-VA:H1IPS-',
        'iterations': [1, 16],
        'voltage': ':ReadV',
        'current': ':ReadI',
        'position': [
            (), (), (), (),
            (), (), (), (),
            (), (), (), (),
            (), (), (), ()
        ]
    },
    "Valve": {
        'prefix': 'LA-CN:H1MPS-1:Gval',
        'sufix': ['Opened', 'Closed'],
        'iterations': [1, 2],
        'position': [
            (), ()]
    }
}

LEGEND = {
    'Gauge Status': [
        {
            'color': GREEN,
            'text': 'ON'
        },
        {
            'color': BLUE,
            'text': 'OFF'
        },
        {
            'color': YELLOW,
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
            'color': GREEN,
            'text': 'ON / Remote'
        },
        {
            'color': BLUE,
            'text': 'OFF / Local'
        },
        {
            'color': YELLOW,
            'text': 'Inconsistent'
        }
    ],
    'CCG': [
        {
            'color': [GREEN, GREEN],
            'text': 'Ok'
        },
        {
            'color': [YELLOW, GREEN],
            'text': 'Warning'
        },
        {
            'color': [YELLOW, RED],
            'text': 'Alarm'
        }
    ],
    'PRG': [
        {
            'color': GREEN,
            'text': 'Ok'
        },
        {
            'color': YELLOW,
            'text': 'Warning'
        }
    ]
}
