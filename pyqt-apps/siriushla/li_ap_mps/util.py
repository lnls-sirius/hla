
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
        [('WFS1_L', 0), ('WFS2_L', 0), ('WFS3_L', 0), ('WFS4_L', 0)],
        [('WFS5_L', 0), ('WFS6_L', 0), ('WFS7_L', 0), ('WFS8_L', 0)],
        [('WFS9_L', 0), ('WFS10_L', 0), ('WFS11_L', 0), ('WFS12_L', 0)],
        [('WFS13_L', 0), ('WFS14_L', 0), ('WFS15_L', 0), ('WFS16_L', 0)]
    ],
}

PV_MPS = {
    'General Status': [
        1,
        ['HeartBeat', 'LAWarn', 'LAAlarm'],
        '', [0, 1, 1], False
    ],
    'Modulator Trigger Permit': [
        2, 'Mod', 'Permit', 1, False
    ],
    'Egun': [
        1, 'Gun',
        ['Permit', 'VacState', 'GvalState'],
        [0, 0, 0], False
    ],
    'Klystrons': [
        2, ['K', 'K', 'K', 'LA-RF:LLRF:KLY'],
        ['PsState_L', 'TempState1', 'TempState2', ':GET_INTERLOCK'],
        [0, 1, 1, 0], False
    ],
    'Compressed Air': [
        1, 'GPS', '', 0, True
    ],
    'Water Conductivity': [
        1, 'WaterState', '', 0, True
    ],
    'Modulator Status': [
        2, 'Mod', 'State', 0, True
    ],
    'General Control': [
        2, ['Emergency', 'BSState', 'PPState'], '',
        [0, 0, 0], True
    ],
    'VA': [
        [16, 10, 10, 5],
        ['IP', 'CCG', 'CCG', 'PRG'],
        ['Warn', 'Warn', 'Alarm', 'Warn'],
        0, True
    ],
    'Water': [
        16, 'WFS', '', 0, True
    ],
    'Gate Valve': [
        2,
        ['ShutGval', 'Gval', 'UOpenGval', 'Gval', 'UCloseGval'],
        ['', 'Opened', '', 'Closed', ''],
        [1, 1, 0, 0, 0], False
    ]
}

GROUP_POS = {
    'Klystrons': [0, 0, 1, 1],
    'General Status': [0, 1, 1, 1],
    'Modulator Trigger Permit': [0, 2, 1, 1],
    'Egun': [0, 3, 1, 1],
    'Gate Valve': [1, 0, 1, 4],
    'General Control': [2, 0, 2, 2],
    'Modulator Status': [2, 2, 1, 2],
    'Compressed Air': [3, 2, 1, 1],
    'Water Conductivity': [3, 3, 1, 1],
    'Water': [4, 0, 4, 4],
    'VA': [0, 4, 8, 1],
    'WT': [0, 0, 1, 1],
    'T': [0, 1, 1, 1]
}

CTRL_TYPE = {
    'Status': '_I',
    'Byspass': '_B',
    'Latch': '_L',
    'Reset': '_R'
}

LBL_MPS = {
    'Klystrons': [
        ['1', '2'],
        ['Status', 'Oil-tank\nWT Alarm', 'Focus-coil\nWT Alarm', 'Refl. PW\nIntlk']
    ],
    'General Status': [
        ['Heart Beat', 'MPS Warn', 'MPS Alarm'], ''
    ],
    'Modulator Trigger Permit': [
        ['1', '2'], ''
    ],
    'Egun': [
        ['Trigger Permit', 'Vaccum Alarm', 'Gate Valve'], ''
    ],
    'General Control': [
        ['1 (Gate)', '2 (Dose)'], ['Emergency', 'Vaccum Alarm', 'Gate Valve']
    ],
    'Modulator Status': [
        '', ['1', '2']
    ],
    'VA': [
        ['EGUN', 'SBUN', 'A4END', 'BEND', 'A0WG', 'K1-A0WG',
            'A1WG', 'K1-A1WG', 'A2WG', 'K1-A2WG', 'K1', 'A3WG',
            'K2-A3WG', 'A4WG', 'K2-A4WG', 'K2'],
        ['IP\nWarn', 'CCG\nWarn', 'CCG\nAlarm', 'PRG\nWarn']
    ],
    'Gate Valve':
    [
        ['1', '2'],
        ['Control', 'Opened', '', 'Closed', '']
    ]
}

LBL_WATER = {
    'WFS1': 'Sub Buncher', 'WFS2': 'Buncher A0',
    'WFS3': 'Tube A1', 'WFS4': 'Tube A2',
    'WFS5': 'Tube A3', 'WFS6': 'Tube A4',
    'WFS7': 'Waveguide 1', 'WFS8': 'Waveguide 2',
    'WFS9':  'Waveguide 3,4', 'WFS10':  'Waveguide 5',
    'WFS11':  'Waveguide 6,7', 'WFS12':  'Load A0',
    'WFS13': 'Load A1', 'WFS14': 'Load A2',
    'WFS15': 'Load A3', 'WFS16': 'Load A4'
}

PV_TEMP_MPS = {
    'WT': [
        [2, 6], 'K'
    ],
    'T': [
        [4, 2], 'A'
    ]
}

TEMP_TYPE = {
    'Value': '',
    'Set': 'Thrd',
    'Setpoint Readback': 'Thrd_BR'
}
