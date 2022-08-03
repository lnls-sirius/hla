
MPS_PREFIX = 'LA-CN:H1MPS-1:'

SEC_2_POS = {
    'General': (1, 0, 2, 1),
    'Egun': (1, 1, 1, 1),
    'Modulators': (2, 1, 1, 1),
    'Klystrons': (3, 0, 1, 2),
    'VA': (5, 0, 1, 2),
    'Compressed Air': (6, 0, 1, 1),
    'Water Conductivity': (6, 1, 1, 1),
    'Water': (7, 0, 1, 2),
}

SEC_2_STATUS = {
    'General': {
        'MPS Heartbeat': ('HeartBeat', 0),
        'MPS Alarm': ('LAAlarm', 1),
        'MPS Warn': ('LAWarn', 1),
        'PPS - Gate': ('PPState7_L', 0),
        'PPS - Dose': ('PPState8_L', 0),
        'BS and SR Intlk 1': ('BSState1_L', 0),
        'BS and SR Intlk 2': ('BSState2_L', 0),
        'Emergency 1': ('Emergency1_L', 0),
        'Emergency 2': ('Emergency2_L', 0),
    },
    'Egun': {
        'Trigger Permit': ('GunPermit', 1),
        'Vacuum Alarm': ('GunVacState', 1),
        'Gate Valve': ('GunGvalState', 1),
    },
    'Modulators': {
        'Header': ['Status', 'Trigger\nPermit'],
        'Mod 1':  [('Mod1State_L', 0), ('Mod1Permit', 1)],
        'Mod 2':  [('Mod2State_L', 0), ('Mod2Permit', 1)],
    },
    'Klystrons': {
        'Header':     ['Status', 'Oil-tank\nWT alarm', 'Focus-coil\nWT alarm',
                       'Refl. PW\nIntlk'],
        'Klystron 1': [('K1PsState_L', 0), ('K1TempState1', 1),
                       ('K1TempState2', 1),
                       ('LA-RF:LLRF:KLY1:GET_INTERLOCK', 0)],
        'Klystron 2': [('K2PsState_L', 0), ('K2TempState1', 1),
                       ('K2TempState2', 1),
                       ('LA-RF:LLRF:KLY2:GET_INTERLOCK', 0)],
    },
    'VA': {
        'Header':  ['IP\nWarn',         'CCG\nWarn',         'CCG\nAlarm',
                    'PRG\nWarn'],
        'EGUN':    [('IP1Warn_L', 0),  ('CCG1Warn_L', 0),  ('CCG1Alarm_L', 0),
                    ('PRG1Warn_L', 0)],
        'SBUN':    [('IP2Warn_L', 0),  ('CCG2Warn_L', 0),  ('CCG2Alarm_L', 0),
                    ''],
        'A0WG':    [('IP5Warn_L', 0),  ('CCG4Warn_L', 0),  ('CCG4Alarm_L', 0),
                    ''],
        'K1-A0WG': [('IP6Warn_L', 0),  '', '', ''],
        'A1WG':    [('IP7Warn_L', 0),  '', '', ''],
        'K1-A1WG': [('IP8Warn_L', 0),  ('CCG5Warn_L', 0),  ('CCG5Alarm_L', 0),
                    ''],
        'A2WG':    [('IP9Warn_L', 0),  ('CCG6Warn_L', 0),  ('CCG6Alarm_L', 0),
                    ('PRG3Warn_L', 0)],
        'K1-A2WG': [('IP10Warn_L', 0), '',  '', ''],
        'K1':      [('IP11Warn_L', 0), ('CCG7Warn_L', 0),  ('CCG7Alarm_L', 0),
                    ('PRG4Warn_L', 0)],
        'A3WG':    [('IP12Warn_L', 0), '', '', ''],
        'K2-A3WG': [('IP13Warn_L', 0), ('CCG8Warn_L', 0),  ('CCG8Alarm_L', 0),
                    ''],
        'A4WG':    [('IP14Warn_L', 0), ('CCG9Warn_L', 0),  ('CCG9Alarm_L', 0),
                    ''],
        'K2-A4WG': [('IP15Warn_L', 0), '', '', ''],
        'K2':      [('IP16Warn_L', 0), ('CCG10Warn_L', 0), ('CCG10Alarm_L', 0),
                    ('PRG5Warn_L', 0)],
        'A4END':   [('IP3Warn_L', 0),  '', '', ''],
        'BEND':    [('IP4Warn_L', 0),  ('CCG3Warn_L', 0),  ('CCG3Alarm_L', 0),
                    ('PRG2Warn_L', 0)],
    },
    'Compressed Air': [[('GPS1_L', 0), ], ],
    'Water Conductivity': [[('WaterState_L', 0), ], ],
    'Water': [
        [('WFS1_L', 0), ('WFS2_L', 0), ('WFS3_L', 0), ('WFS4_L', 0),
         ('WFS5_L', 0), ('WFS6_L', 0), ('WFS7_L', 0), ('WFS8_L', 0)],
        [('WFS9_L', 0), ('WFS10_L', 0), ('WFS11_L', 0), ('WFS12_L', 0),
         ('WFS13_L', 0), ('WFS14_L', 0), ('WFS15_L', 0), ('WFS16_L', 0)]
    ]
}

PV_MPS = {
    'General': {
        'name': [
            'HeartBeat', 'LAAlarm', 'LAWarn',
            'PPState7', 'PPState8', 'BSState1',
            'BSState2', 'Emergency1', 'Emergency2'
        ],
        'config':
            [0, 1, 1,
                0, 0, 0,
                0, 0, 0],
        'control':
            [False, False, False,
                True, True, True,
                True, True, True]
    },
    'Modulator': {
        'name': [
            'Mod1State', 'Mod1Permit',
            'Mod2State', 'Mod2Permit'
        ],
        'config': [
            0, 1,
            0, 1
        ],
        'control': [
            True, False,
            True, False
        ]
    },
    'Egun': {
        'name': [
            'GunPermit',
            'GunVacState',
            'GunGvalState'
        ],
        'config': 1,
        'control': False
    },
    'Klystrons': {
        'name': [
            'K1PsState', 'K1TempState1',
            'K1TempState2', 'LA-RF:LLRF:KLY1:GET_INTERLOCK',
            'K2PsState', 'K2TempState1',
            'K2TempState2', 'LA-RF:LLRF:KLY2:GET_INTERLOCK'
        ],
        'config': [
            0, 1, 1, 0,
            0, 1, 1, 0
        ],
        'control': [
            True, False, False, False,
            True, False, False, False
        ]
    },
    'Compressed Air': {
        'name': ['GPS1'],
        'config': 0,
        'control': True
    },
    'Water Conductivity': {
        'name': ['WaterState'],
        'config': 0,
        'control': True
    },
    'VA': {
        'name': [
            'IP1Warn', 'CCG1Warn', 'CCG1Alarm', 'PRG1Warn',
            'IP2Warn', 'CCG2Warn', 'CCG2Alarm',
            'IP5Warn', 'CCG4Warn', 'CCG4Alarm',
            'IP6Warn',
            'IP7Warn',
            'IP8Warn', 'CCG5Warn', 'CCG5Alarm',
            'IP9Warn', 'CCG6Warn', 'CCG6Alarm', 'PRG3Warn',
            'IP10Warn',
            'IP11Warn', 'CCG7Warn', 'CCG7Alarm', 'PRG4Warn',
            'IP12Warn',
            'IP13Warn', 'CCG8Warn', 'CCG8Alarm',
            'IP14Warn', 'CCG9Warn', 'CCG9Alarm',
            'IP15Warn',
            'IP16Warn', 'CCG10Warn', 'CCG10Alarm', 'PRG5Warn',
            'IP3Warn',
            'IP4Warn', 'CCG3Warn', 'CCG3Alarm', 'PRG2Warn'
        ],
        'config': 0,
        'control': True
    },
    'Water': {
        'name': [
            'WFS1', 'WFS2', 'WFS3', 'WFS4',
            'WFS5', 'WFS6', 'WFS7', 'WFS8',
            'WFS9', 'WFS10', 'WFS11', 'WFS12',
            'WFS13', 'WFS14', 'WFS15', 'WFS16'
        ],
        'config': 0,
        'control': True
    },
    'Gate Valve': {
        'name': [
            'ShutGval1',
            'Gval1Opened', 'UOpenGval1', 'Gval1Closed', 'UCloseGval1',
            'ShutGval2',
            'Gval2Opened', 'UOpenGval2', 'Gval2Closed', 'UCloseGval2'
        ],
        'config': [
            1, 1, 0, 0, 0,
            1, 1, 0, 0, 0
        ],
        'control': False
    }
}

GROUP_POS = {
    'General': [0, 0, 2, 1],
    'Egun': [0, 1, 1, 1],
    'Modulator': [1, 1, 1, 1],
    'VA': [0, 2, 7, 1],
    'Compressed Air': [2, 1, 1, 1],
    'Water Conductivity': [2, 0, 1, 1],
    'Klystrons': [3, 0, 2, 2],
    'Gate Valve': [5, 0, 2, 2],
    'Water': [7, 0, 1, 3],
    'Water Temperature': [3, 0, 1, 1],
    'Temperature': [1, 0, 1, 1]
}

GROUP_POSALL = {
    'Modulator': [1, 1, 1, 1],
    'Egun': [0, 1, 1, 1],
    'VA': [0, 2, 7, 1],
    'Klystrons': [3, 0, 2, 2],
    'Gate Valve': [5, 0, 2, 2],
    'General': [0, 0, 2, 1],
    'Water Conductivity': [2, 0, 1, 1],
    'Compressed Air': [2, 1, 1, 1],
    'Water': [7, 0, 2, 3],
    'Water Temperature': [3, 0, 1, 1],
    'Temperature': [1, 0, 1, 1]
}

CTRL_TYPE = {
    'Status': '_I',
    'Byspass': '_B',
    'Latch': '_L',
    'Reset': '_R'
}

TEMP_TYPE = {
    'Value': '',
    'Set': 'Thrd',
    'Setpoint<br>Readback': 'Thrd_RB'
}

LBL_ALL = [
    'PPState7', 'Mod1State', 'GPS1', 'WaterState',
    'K1PsState', 'IP1Warn', 'CCG1Warn', 'CCG1Alarm',
    'PRG1Warn', 'WFS1', 'WFS2', 'WFS3', 'WFS4', 'WFS5', 'WFS6'
]

LBL_MPS = {
    'Klystrons': [
        ['Kly 1', 'Kly 2'],
        ['Status', 'Oil-tank<br>WT Alarm', 'Focus-coil<br>WT Alarm', 'Refl. PW<br>Intlk']
    ],
    'General': [
        ['Heart Beat', 'MPS Alarm', 'MPS Warn',
            'PPS - Gate', 'PPS - Dose', 'BS and SR<br>Intlk 1', 'BS and SR<br>Intlk 2',
            'Emergency 1', 'Emergency 2'], ''
    ],
    'Modulator': [
        ['Mod 1', 'Mod 2'], ['Status', 'Trigger<br>Permit']
    ],
    'Egun': [
        ['Trigger<br>Permit', 'Vaccum<br>Alarm', 'Gate Valve'], ''
    ],
    'VA': [
        ['EGUN', 'SBUN', 'A0WG', 'K1-A0WG', 'A1WG', 'K1-A1WG',
            'A2WG', 'K1-A2WG', 'K1', 'A3WG', 'K2-A3WG', 'A4WG',
            'K2-A4WG', 'K2', 'A4END', 'BEND'],
        ['IP<br>Warn', 'CCG<br>Warn', 'CCG<br>Alarm', 'PRG<br>Warn']
    ],
    'Water': [
        ['', 'Waveguide', 'Load'], ''
    ],
    'Gate Valve':
    [
        ['Valve 1', 'Valve 2'],
        ['Control', 'Opened', '', 'Closed', '']
    ],
    'Temperature':
    [
        ['Tube A1', 'Tube A2', 'Tube A3', 'Tube A4'],
        ['1', '2']
    ],
    'Water Temperature':
    [
        ['Body', 'Waveguide', 'Oil-tank', 'Focus-coil', 'In', 'Test-load'],
        ['K1', 'K2']
    ]
}

LBL_WATER = {
    'WFS1': 'Sub<br>Buncher', 'WFS2': 'Buncher<br>A0',
    'WFS3': 'Tube<br>A1', 'WFS4': 'Tube<br>A2',
    'WFS5': 'Tube<br>A3', 'WFS6': 'Tube<br>A4',
    'WFS7': '1', 'WFS8': '2',
    'WFS9':  '3,4', 'WFS10':  '5',
    'WFS11':  '6,7', 'WFS12':  'A0',
    'WFS13': 'A1', 'WFS14': 'A2',
    'WFS15': 'A3', 'WFS16': 'A4'
}

PV_TEMP_MPS = {
    'Water Temperature': [
        [2, 6], 'K'
    ],
    'Temperature': [
        [4, 2], 'A'
    ]
}
