"""Utilities."""


SEC_2_CHANNELS = {
    'BO': {
        'Emergency': 'BO-05D:RF-Intlk:EStop-Mon',
        'Sirius Intlk': 'RA-RaBO02:RF-IntlkCtrl:IntlkSirius-Mon',
        'LLRF Intlk': 'RA-RaBO01:RF-LLRF:Intlk-Mon',
        'LLRF Intlk Details': {
            'Inputs': {
                'Input': {
                    'Status': {
                        '0': 'BR-RF-DLLRF-01:ILK:0',
                        '1': 'BR-RF-DLLRF-01:ILK:1',
                        '2': 'BR-RF-DLLRF-01:ILK:2',
                        '3': 'BR-RF-DLLRF-01:ILK:3',
                        '4': 'BR-RF-DLLRF-01:ILK:4',
                        '5': 'BR-RF-DLLRF-01:ILK:5',
                        '6': 'BR-RF-DLLRF-01:ILK:6',
                        '7': 'BR-RF-DLLRF-01:ILK:7',
                        'Mon': 'BR-RF-DLLRF-01:Intlk-Mon',
                    },
                    'Labels': (
                        'Rev Out SSA',
                        'Not Used (RevSSA2)',
                        'Not Used (RefSSA3)',
                        'Not Used (RevSSA4)',
                        'Rev Cavity',
                        'Not Used (Ext LLRF1)',
                        'Not Used (Ext LLRF2)',
                        'Not Used (Ext LLRF3)',
                        'Manual',
                        'PLC',
                        'Plunger 1 End Sw Up',
                        'Plunger 1 End Sw Down',
                        'Plunger 2 End Sw Up',
                        'Plunger 2 End Sw Down',
                    ),
                },
                'Fast Input': {
                    'Status': {
                        '0': 'BR-RF-DLLRF-01:FAST:ILK:0',
                        '1': 'BR-RF-DLLRF-01:FAST:ILK:1',
                        '2': 'BR-RF-DLLRF-01:FAST:ILK:2',
                        '3': 'BR-RF-DLLRF-01:FAST:ILK:3',
                        '4': 'BR-RF-DLLRF-01:FAST:ILK:4',
                        '5': 'BR-RF-DLLRF-01:FAST:ILK:5',
                        '6': 'BR-RF-DLLRF-01:FAST:ILK:6',
                        '7': 'BR-RF-DLLRF-01:FAST:ILK:7',
                        'Mon': 'BR-RF-DLLRF-01:FASTINLK-MON',
                    },
                    'Labels': (
                        'Cavity Voltage',
                        'Cavity Fwd',
                        'SSA 1 Out Fwd',
                        'Cell 2 Voltage (RFIN7)',
                        'Cell 4 Voltage (RFIN8)',
                        'Cell 1 Voltage (RFIN9)',
                        'Cell 5 Voltage (RFIN10)',
                        'Pre-Drive In (RFIN11)',
                        'Pre-Drive Out Fwd (RFIN12)',
                        'Pre-Drive Out Rev (RFIN13)',
                        'Circulator Out Fwd (RFIN14)',
                        'Circulator Out Rev (RFIN15)',
                        'LLRF Beam Trip',
                    ),
                }
            },
            'Timestamps': {
                '1': 'BR-RF-DLLRF-01:TS1',
                '2': 'BR-RF-DLLRF-01:TS2',
                '3': 'BR-RF-DLLRF-01:TS3',
                '4': 'BR-RF-DLLRF-01:TS4',
                '5': 'BR-RF-DLLRF-01:TS5',
                '6': 'BR-RF-DLLRF-01:TS6',
                '7': 'BR-RF-DLLRF-01:TS7',
            }
        },
        'Reset': {
            'Global': 'RA-RaBO02:RF-Intlk:Reset-Cmd',
            'LLRF': 'BR-RF-DLLRF-01:Reset-Cmd',
        },
        'Cav Sts': {
            'Geral': 'BO-05D:RF-P5Cav:Sts-Mon',
            'Temp': {
                'Cells': (
                    ('BO-05D:RF-P5Cav:Cylin1T-Mon', 'blue'),
                    ('BO-05D:RF-P5Cav:Cylin2T-Mon', 'red'),
                    ('BO-05D:RF-P5Cav:Cylin3T-Mon', 'darkGreen'),
                    ('BO-05D:RF-P5Cav:Cylin4T-Mon', 'magenta'),
                    ('BO-05D:RF-P5Cav:Cylin5T-Mon', 'darkCyan'),
                ),
                'Cells Limits PVs': ('BO-05D:RF-P5Cav:Cylin1TLowerLimit-Cte',
                                     'BO-05D:RF-P5Cav:Cylin1TUpperLimit-Cte'),
                'Cells Limits': [0.0, 0.0],
                'Coupler': ('BO-05D:RF-P5Cav:CoupT-Mon', 'black'),
                'Coupler Limits PVs': ('BO-05D:RF-P5Cav:CoupTLowerLimit-Cte',
                                       'BO-05D:RF-P5Cav:CoupTUpperLimit-Cte'),
                'Coupler Limits': [0.0, 0.0],
                'Discs': (
                    'BO-05D:RF-P5Cav:Disc1Tms-Mon',
                    'BO-05D:RF-P5Cav:Disc2Tms-Mon',
                    'BO-05D:RF-P5Cav:Disc3Tms-Mon',
                    'BO-05D:RF-P5Cav:Disc4Tms-Mon',
                    'BO-05D:RF-P5Cav:Disc5Tms-Mon',
                    'BO-05D:RF-P5Cav:Disc6Tms-Mon',
                ),
            },
            'FlwRt': {
                'Flow Switch 1': 'BO-05D:RF-P5Cav:Hd1FlwRt-Mon',
                'Flow Switch 2': 'BO-05D:RF-P5Cav:Hd2FlwRt-Mon',
                'Flow Switch 3': 'BO-05D:RF-P5Cav:Hd3FlwRt-Mon',
                'Flow Switch 4': 'BO-05D:RF-P5Cav:Hd4FlwRt-Mon',
            },
            'Vac': {
                'Cells': 'BO-05D:VA-CCG-RFC:Pressure-Mon',
                'Cond': 'BR-RF-DLLRF-01:VACUUM',
                'Cells ok': 'BO-05D:RF-P5Cav:Pressure-Mon',
                'Coupler ok': 'BO-05D:RF-P5Cav:CoupPressure-Mon',
            }
        },
        'TL Sts': {
            'Geral': 'RA-TLBO:RF-TrLine:Sts-Mon',
            'label_led': {
                'Circulator Temp. Drift': {
                    'label': 'RA-TLBO:RF-Circulator:dT-Mon',
                    'led': 'RA-TLBO:RF-Circulator:TDrift-Mon'
                },
                'Circulator Coil': {
                    'label': 'RA-TLBO:RF-Circulator:Current-Mon',
                    'led': 'RA-TLBO:RF-Circulator:Sts-Mon'
                },
                'Room Temp.': {
                    'label': 'RA-TLBO:RF-Circulator:Tamb-Mon',
                    'led': 'RA-TLBO:RF-Circulator:TEnv-Mon'
                }
            },
            'Circulator Temp. In': {
                'label': 'RA-TLBO:RF-Circulator:Tin-Mon',
                'led': {
                    'RA-TLBO:RF-Circulator:TinDown-Mon': 0,
                    'RA-TLBO:RF-Circulator:TinUp-Mon': 0
                }
            },
            'label': {
                'Circulator Temp. Out': 'RA-TLBO:RF-Circulator:Tout-Mon',
                'Circulator In Reflected Power': 'RA-TLBO:RF-Circulator:PwrRevIndBm-Mon'
            },
            'led': {
                'Circulator Arc Detector': 'RA-TLBO:RF-Circulator:Arc-Mon',
                'Circulator Arc Detector Supply Fail': 'RA-RaBO02:RF-ArcDetec-Circ:PwrFail-Mon',
                'Circulator Flow': 'RA-TLBO:RF-Circulator:FlwRt-Mon',
                'Load Flow': 'RA-TLBO:RF-Load:FlwRt-Mon',
                'TCU Status': 'RA-TLBO:RF-Circulator:IntlkOp-Mon',
            },
            'Circ Limits': (19.0, 23.0),
        },
        'SSA': {
            'Name': 'SSA',
            'Status': 'RA-ToBO:RF-SSAmpTower:Sts-Mon',
            'Power': 'RA-ToBO:RF-SSAmpTower:PwrFwdOutLLRF-Mon',
            'SRC 1': {
                'Label': '300VDC',
                'Enable': 'RA-ToBO:RF-ACDCPanel:300VdcEnbl-Sel',
                'Disable': 'RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel',
                'Mon': 'RA-ToBO:RF-ACDCPanel:300Vdc-Sts'
            },
            'SRC 2': {
                'Label': 'DC/DC',
                'Enable': 'RA-ToBO:RF-SSAmpTower:PwrCnvEnbl-Sel',
                'Disable': 'RA-ToBO:RF-SSAmpTower:PwrCnvDsbl-Sel',
                'Mon': 'RA-ToBO:RF-SSAmpTower:PwrCnv-Sts'
            },
            'PinSw': {
                'Label': 'PinSw',
                'Enable': 'RA-RaBO01:RF-LLRFPreAmp:PinSwEnbl-Cmd',
                'Disable': 'RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd',
                'Mon': 'RA-RaBO01:RF-LLRFPreAmp:PinSw-Mon'
            },
            'PreDrive': 'BR-RF-DLLRF-01:INPRE:AMP',
            'PreDriveThrs': 4,  # mV
        },
        'SL': {
            'Enbl': 'BR-RF-DLLRF-01:SL',
            'Mode': 'BR-RF-DLLRF-01:MODE',
            'IRef': 'BR-RF-DLLRF-01:I:SL:REF',
            'QRef': 'BR-RF-DLLRF-01:Q:SL:REF',
            'ARef': 'BR-RF-DLLRF-01:SL:REF:AMP',
            'PRef': 'BR-RF-DLLRF-01:SL:REF:PHS',
            'IInp': 'BR-RF-DLLRF-01:I:SL:INP',
            'QInp': 'BR-RF-DLLRF-01:Q:SL:INP',
            'AInp': 'BR-RF-DLLRF-01:SL:INP:AMP',
            'PInp': 'BR-RF-DLLRF-01:SL:INP:PHS',
            'IErr': 'BR-RF-DLLRF-01:I:SL:ERR',
            'QErr': 'BR-RF-DLLRF-01:Q:SL:ERR',
            'AErr': 'BR-RF-DLLRF-01:SL:ERR:AMP',
            'PErr': 'BR-RF-DLLRF-01:SL:ERR:PHS',
            'ASet': ['BR-RF-DLLRF-01:mV:AL:REF', 'RA-RaBO01:RF-LLRF:AmpVCav'],
            'PSet': 'BR-RF-DLLRF-01:PL:REF',
            'AInc': 'BR-RF-DLLRF-01:AMPREF:INCRATE',
            'PInc': 'BR-RF-DLLRF-01:PHSREF:INCRATE',
            'Inp': 'BR-RF-DLLRF-01:SL:SEL',
            'PIL': 'BR-RF-DLLRF-01:SL:PILIMIT',
            'KI': 'BR-RF-DLLRF-01:SL:KI',
            'KP': 'BR-RF-DLLRF-01:SL:KP',
        },
        'Tun': {
            'Auto': 'BR-RF-DLLRF-01:TUNE',
            'DTune': 'BR-RF-DLLRF-01:DTune-RB',
            'DPhase': 'BR-RF-DLLRF-01:TUNE:DEPHS',
            'Acting': 'BR-RF-DLLRF-01:TUNE:OUT',
            'Deadbnd': 'BR-RF-DLLRF-01:TUNE:MARGIN:HI',
            'Oversht': 'BR-RF-DLLRF-01:TUNE:MARGIN:LO',
            'Pl1Down': 'BR-RF-DLLRF-01:PLG1:MOVE:DN',
            'Pl1Up': 'BR-RF-DLLRF-01:PLG1:MOVE:UP',
            'Pl2Down': 'BR-RF-DLLRF-01:PLG2:MOVE:DN',
            'Pl2Up': 'BR-RF-DLLRF-01:PLG2:MOVE:UP',
            'PlM1Curr': 'RA-RaBO01:RF-CavPlDrivers:Dr1Current-Mon',
            'PlM2Curr': 'RA-RaBO01:RF-CavPlDrivers:Dr2Current-Mon',
        },
        'FFlat': {
            'Sts': 'BR-RF-DLLRF-01:FF:ON',
            'Auto': 'BR-RF-DLLRF-01:FF',
            'Pos': 'BR-RF-DLLRF-01:FF:POS',
            'Gain1': 'BR-RF-DLLRF-01:FF:GAIN:CELL2',
            'Gain2': 'BR-RF-DLLRF-01:FF:GAIN:CELL4',
            'Cell1': 'BR-RF-DLLRF-01:FF:CELL2',
            'Cell2': 'BR-RF-DLLRF-01:FF:CELL4',
            'Deadband': 'BR-RF-DLLRF-01:FF:DEADBAND',
            'Err': 'BR-RF-DLLRF-01:FF:ERR',
        },
        'PwrMtr': {
            'Cavity Power': {
                'W': 'BO-05D:RF-P5Cav:Cell3Pwr-Mon',
                'dBm': 'BO-05D:RF-P5Cav:Cell3PwrdBm-Mon',
                'mV': 'BR-RF-DLLRF-01:CAV:AMP',
                'color': 'blue',
            },
            'Power Forward': {
                'W': 'BO-05D:RF-P5Cav:PwrFwd-Mon',
                'dBm': 'BO-05D:RF-P5Cav:PwrFwddBm-Mon',
                'mV': 'BR-RF-DLLRF-01:FWDCAV:AMP',
                'color': 'darkGreen',
            },
            'Power Reverse': {
                'W': 'BO-05D:RF-P5Cav:PwrRev-Mon',
                'dBm': 'BO-05D:RF-P5Cav:PwrRevdBm-Mon',
                'mV': 'BR-RF-DLLRF-01:REVCAV:AMP',
                'color': 'red',
            },
        },
        'CavVGap': 'BO-05D:RF-P5Cav:AmpVCav-Mon',
        'TempMon': {
            'Temp.': {
                'Cells': {
                    'Cell 1': 'BO-05D:RF-P5Cav:Cylin1T-Mon',
                    'Cell 2': 'BO-05D:RF-P5Cav:Cylin2T-Mon',
                    'Cell 3': 'BO-05D:RF-P5Cav:Cylin3T-Mon',
                    'Cell 4': 'BO-05D:RF-P5Cav:Cylin4T-Mon',
                    'Cell 5': 'BO-05D:RF-P5Cav:Cylin5T-Mon',
                },
            }
        },
        'Ramp': {
            'W': {
                'Bottom': {
                    'CavPwr': 'BO-05D:RF-P5Cav:Cell3PwrBot-Mon',
                    'PowFwd': 'BO-05D:RF-P5Cav:PwrFwdBot-Mon',
                    'PowRev': 'BO-05D:RF-P5Cav:PwrRevBot-Mon'
                },
                'Top': {
                    'CavPwr': 'BO-05D:RF-P5Cav:Cell3PwrTop-Mon',
                    'PowFwd': 'BO-05D:RF-P5Cav:PwrFwdTop-Mon',
                    'PowRev': 'BO-05D:RF-P5Cav:PwrRevTop-Mon'
                }
            },
            'mV': {
                'Bottom': {
                    'CavPwr': 'BR-RF-DLLRF-01:BOT:CELL3:AMP',
                    'PowFwd': 'BR-RF-DLLRF-01:BOT:FWDCAV:AMP',
                    'PowRev': 'BR-RF-DLLRF-01:BOT:REVCAV:AMP'
                },
                'Top': {
                    'CavPwr': 'BR-RF-DLLRF-01:TOP:CELL3:AMP',
                    'PowFwd': 'BR-RF-DLLRF-01:TOP:FWDCAV:AMP',
                    'PowRev': 'BR-RF-DLLRF-01:TOP:REVCAV:AMP'
                }
            }
        },
        'FDL': {
            'Signals': (
                ('Cav', 'BR-RF-DLLRF-01:FDL:CAV:AMP', 'BR-RF-DLLRF-01:FDL:CAV:PHS', 'blue'),
                ('Fwd Cav', 'BR-RF-DLLRF-01:FDL:FWDCAV:AMP', 'BR-RF-DLLRF-01:FDL:FWDCAV:PHS', 'red'),
                ('Rev Cav', 'BR-RF-DLLRF-01:FDL:REVCAV:AMP', 'BR-RF-DLLRF-01:FDL:REVCAV:PHS', 'darkSlateBlue'),
                ('Fwd Ssa', 'BR-RF-DLLRF-01:FDL:FWDSSA:AMP', 'BR-RF-DLLRF-01:FDL:FWDSSA:PHS', 'darkGreen'),
                ('Rev Ssa', 'BR-RF-DLLRF-01:FDL:REVSSA:AMP', 'BR-RF-DLLRF-01:FDL:REVSSA:PHS', 'magenta'),
                ('Ctrl', 'BR-RF-DLLRF-01:FDL:CTRL:AMP', 'BR-RF-DLLRF-01:FDL:CTRL:PHS', 'darkCyan'),
                ('Ref', 'BR-RF-DLLRF-01:FDL:SL:REF:AMP', 'BR-RF-DLLRF-01:FDL:SL:REF:PHS', 'darkRed'),
                ('Err', 'BR-RF-DLLRF-01:FDL:SL:ERR:AMP', 'BR-RF-DLLRF-01:FDL:SL:ERR:PHS', 'purple'),
                ('Err Acc', 'BR-RF-DLLRF-01:FDL:SL:ERRACC:AMP', 'BR-RF-DLLRF-01:FDL:SL:ERRACC:PHS', 'saddlebrown'),
                ('MO', 'BR-RF-DLLRF-01:FDL:MO:AMP', 'BR-RF-DLLRF-01:FDL:MO:PHS', 'darkBlue'),
                ('Tune', None, 'BR-RF-DLLRF-01:FDL:TUNE:DEPHS', 'orangered'),
                ('Tune Filt', None, 'BR-RF-DLLRF-01:FDL:TUNE:DEPHS:FILT', 'darkOliveGreen')
            ),
            'Time': 'BR-RF-DLLRF-01:FDL:SCALE:32',
            'Mode': 'BR-RF-DLLRF-01:FDL:MODE',
            'SW Trig': 'BR-RF-DLLRF-01:FDL:SWTRIG',
            'HW Trig': 'BR-RF-DLLRF-01:FDL:HWTRIG',
            'Trig': 'BR-RF-DLLRF-01:FDL:TRIG:S',
            'Processing': 'BR-RF-DLLRF-01:FDL:PROCESSING',
            'Rearm': 'BR-RF-DLLRF-01:FDL:REARM',
            'Raw': 'BR-RF-DLLRF-01:FDL:RAW',
            'Qty': 'BR-RF-DLLRF-01:FDL:FrameQty-',
            'Size': 'BR-RF-DLLRF-01:FDL:Size-Mon',
            'Duration': 'BR-RF-DLLRF-01:FDL:Duration-Mon',
            'Delay': 'BR-RF-DLLRF-01:FDL:TriggerDelay'
        }
    },
    'SI': {
        'Emergency': 'RA-RaSIA02:RF-IntlkCtrl:EStop-Mon',
        'Sirius Intlk': 'RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon',
        'LLRF Intlk': 'RA-RaSIA01:RF-LLRF:Intlk-Mon',
        'LLRF Intlk Details': {
            'Inputs': {
                'Input': {
                    'Status': {
                        '0': 'SR-RF-DLLRF-01:ILK:0',
                        '1': 'SR-RF-DLLRF-01:ILK:1',
                        '2': 'SR-RF-DLLRF-01:ILK:2',
                        '3': 'SR-RF-DLLRF-01:ILK:3',
                        '4': 'SR-RF-DLLRF-01:ILK:4',
                        '5': 'SR-RF-DLLRF-01:ILK:5',
                        '6': 'SR-RF-DLLRF-01:ILK:6',
                        '7': 'SR-RF-DLLRF-01:ILK:7',
                        'Mon': 'SR-RF-DLLRF-01:Intlk-Mon',
                    },
                    'Labels': (
                        'Rev Out SSA 1',
                        'Rev Out SSA 2',
                        'Not Used (RefSSA3)',
                        'Not Used (RevSSA4)',
                        'Rev Cavity',
                        'Not Used (Ext LLRF1)',
                        'Not Used (Ext LLRF2)',
                        'Not Used (Ext LLRF3)',
                        'Manual',
                        'PLC',
                        'Plunger 1 End Sw Up',
                        'Plunger 1 End Sw Down',
                        'Plunger 2 End Sw Up',
                        'Plunger 2 End Sw Down',
                    ),
                },
                'Fast Input': {
                    'Status': {
                        '0': 'SR-RF-DLLRF-01:FAST:ILK:0',
                        '1': 'SR-RF-DLLRF-01:FAST:ILK:1',
                        '2': 'SR-RF-DLLRF-01:FAST:ILK:2',
                        '3': 'SR-RF-DLLRF-01:FAST:ILK:3',
                        '4': 'SR-RF-DLLRF-01:FAST:ILK:4',
                        '5': 'SR-RF-DLLRF-01:FAST:ILK:5',
                        '6': 'SR-RF-DLLRF-01:FAST:ILK:6',
                        '7': 'SR-RF-DLLRF-01:FAST:ILK:7',
                        'Mon': 'SR-RF-DLLRF-01:FASTINLK-MON',
                    },
                    'Labels': (
                        'Cavity Voltage',
                        'Cavity Fwd',
                        'SSA 1 Out Fwd',
                        'Cell 2 Voltage (RFIN7)',
                        'Cell 6 Voltage (RFIN8)',
                        'SSA 2 Out Fwd (RFIN9)',
                        'SSA 2 Rev Fwd (RFIN10)',
                        'Pre-Drive 1 In (RFIN11)',
                        'Pre-Drive 1 Out (RFIN12)',
                        'Pre-Drive 2 In (RFIN13)',
                        'Pre-Drive 2 Out (RFIN14)',
                        'Circulator Out Fwd (RFIN15)',
                        'LLRF Beam Trip',
                    ),
                },
            },
            'Timestamps': {
                '1': 'SR-RF-DLLRF-01:TS1',
                '2': 'SR-RF-DLLRF-01:TS2',
                '3': 'SR-RF-DLLRF-01:TS3',
                '4': 'SR-RF-DLLRF-01:TS4',
                '5': 'SR-RF-DLLRF-01:TS5',
                '6': 'SR-RF-DLLRF-01:TS6',
                '7': 'SR-RF-DLLRF-01:TS7',
            }
        },
        'Reset': {
            'Global': 'RA-RaSIA02:RF-Intlk:Reset-Cmd',
            'LLRF': 'SR-RF-DLLRF-01:Reset-Cmd',
        },
        'Cav Sts': {
            'Geral': 'SI-02SB:RF-P7Cav:Sts-Mon',
            'Temp': {
                'Cells': (
                    ('SI-02SB:RF-P7Cav:Cylin1T-Mon', 'blue'),
                    ('SI-02SB:RF-P7Cav:Cylin2T-Mon', 'red'),
                    ('SI-02SB:RF-P7Cav:Cylin3T-Mon', 'yellow'),
                    ('SI-02SB:RF-P7Cav:Cylin4T-Mon', 'darkGreen'),
                    ('SI-02SB:RF-P7Cav:Cylin5T-Mon', 'magenta'),
                    ('SI-02SB:RF-P7Cav:Cylin6T-Mon', 'darkCyan'),
                    ('SI-02SB:RF-P7Cav:Cylin7T-Mon', 'darkRed'),
                ),
                'Cells Limits PVs': ('SI-02SB:RF-P7Cav:Cylin1TLowerLimit-Cte',
                                     'SI-02SB:RF-P7Cav:Cylin1TUpperLimit-Cte'),
                'Cells Limits': [0.0, 0.0],
                'Coupler': ('SI-02SB:RF-P7Cav:CoupT-Mon', 'black'),
                'Coupler Limits PVs': ('SI-02SB:RF-P7Cav:CoupTLowerLimit-Cte',
                                       'SI-02SB:RF-P7Cav:CoupTUpperLimit-Cte'),
                'Coupler Limits': [0.0, 0.0],
                'Discs': (
                    'SI-02SB:RF-P7Cav:Disc1Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc2Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc3Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc4Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc5Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc6Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc7Tms-Mon',
                    'SI-02SB:RF-P7Cav:Disc8Tms-Mon',
                ),
            },
            'FlwRt': {
                'Flow Switch 1': 'SI-02SB:RF-P7Cav:HDFlwRt1-Mon',
                'Flow Switch 2': 'SI-02SB:RF-P7Cav:HDFlwRt2-Mon',
                'Flow Switch 3': 'SI-02SB:RF-P7Cav:HDFlwRt3-Mon',
            },
            'Vac': {
                'Cells': 'SI-02SB:VA-CCG-CAV:Pressure-Mon',
                'Cond': 'SR-RF-DLLRF-01:VACUUM',
                'Cells ok': 'SI-02SB:RF-P7Cav:Pressure-Mon',
                'Coupler ok': 'SI-02SB:RF-P7Cav:CoupPressure-Mon',
            }
        },
        'TL Sts': {
            'Geral': 'RA-TLSIA:RF-TrLine:Sts-Mon',
            'Circulator Temp. In': {
                'label': 'RA-TLSIA:RF-Circulator:Tin-Mon',
                'led': {
                    'RA-TLSIA:RF-Circulator:TinDown-Mon': 0,
                    'RA-TLSIA:RF-Circulator:TinUp-Mon': 0
                }
            },
            'label_led': {
                'Circulator Temp. Drift': {
                    'label': 'RA-TLSIA:RF-Circulator:dT-Mon',
                    'led': 'RA-TLSIA:RF-Circulator:TDrift-Mon'
                },
                'Circulator Coil': {
                    'label': 'RA-TLSIA:RF-Circulator:Current-Mon',
                    'led': 'RA-TLSIA:RF-Circulator:Sts-Mon'
                },
                'Room Temp.': {
                    'label': 'RA-TLSIA:RF-Circulator:Tamb-Mon',
                    'led': 'RA-TLSIA:RF-Circulator:TEnv-Mon'
                }
            },
            'label': {
                'Circulator Temp. Out': 'RA-TLSIA:RF-Circulator:Tout-Mon',
                'Circulator In Reflected Power': 'RA-TLSIA:RF-Circulator:PwrRevIndBm-Mon',
                'Combiner': 'RA-TLSIA:RF-Combiner:T-Mon'
            },
            'led': {
                'Circulator Arc Detector': 'RA-TLSIA:RF-Circulator:Arc-Mon',
                'Circulator Arc Detector Supply Fail': 'RA-RaSIA02:RF-ArcDetec-Circ:PwrFail-Mon',
                'Arc Detector Load': 'RA-TLSIA:RF-Load:Arc-Mon',
                'Arc Detector Load Supply Fail': 'RA-RaSIA02:RF-ArcDetec-Load:PwrFail-Mon',
                'Circulator Flow': 'RA-TLSIA:RF-Circulator:FlwRt-Mon',
                'Load Flow': 'RA-TLSIA:RF-Load:FlwRt-Mon',
                'TCU Status': 'RA-TLSIA:RF-Circulator:IntlkOp-Mon',
            },
            'Circ Limits': (19.0, 23.0),
        },
        'SSA': {
            '1': {
                'Name': 'SSA 01',
                'Status': 'RA-ToSIA03:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIA03:RF-SSAmpTower:PwrFwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIA03:RF-ACPanel:PwrACEnbl-Cmd',
                    'Disable': 'RA-ToSIA03:RF-ACPanel:PwrACDsbl-Cmd',
                    'Mon': 'RA-ToSIA03:RF-ACPanel:PwrAC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIA03:RF-TDKSource:PwrDCEnbl-Cmd',
                    'Disable': 'RA-ToSIA03:RF-TDKSource:PwrDCDsbl-Cmd',
                    'Mon': 'RA-ToSIA03:RF-TDKSource:PwrDC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIA03:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIA03:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIA03:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'SR-RF-DLLRF-01:INPRE1:AMP',
                'PreDriveThrs': 5,  # mV
            },
            '2': {
                'Name': 'SSA 02',
                'Status': 'RA-ToSIA04:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIA04:RF-SSAmpTower:PwrFwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIA04:RF-ACPanel:PwrACEnbl-Cmd',
                    'Disable': 'RA-ToSIA04:RF-ACPanel:PwrACDsbl-Cmd',
                    'Mon': 'RA-ToSIA04:RF-ACPanel:PwrAC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIA04:RF-TDKSource:PwrDCEnbl-Cmd',
                    'Disable': 'RA-ToSIA04:RF-TDKSource:PwrDCDsbl-Cmd',
                    'Mon': 'RA-ToSIA04:RF-TDKSource:PwrDC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIA04:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIA04:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIA04:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'SR-RF-DLLRF-01:INPRE2:AMP',
                'PreDriveThrs': 5,  # mV
            }
        },
        'SL': {
            'Enbl': 'SR-RF-DLLRF-01:SL',
            'Mode': 'SR-RF-DLLRF-01:MODE',
            'IRef': 'SR-RF-DLLRF-01:I:SL:REF',
            'QRef': 'SR-RF-DLLRF-01:Q:SL:REF',
            'ARef': 'SR-RF-DLLRF-01:SL:REF:AMP',
            'PRef': 'SR-RF-DLLRF-01:SL:REF:PHS',
            'IInp': 'SR-RF-DLLRF-01:I:SL:INP',
            'QInp': 'SR-RF-DLLRF-01:Q:SL:INP',
            'AInp': 'SR-RF-DLLRF-01:SL:INP:AMP',
            'PInp': 'SR-RF-DLLRF-01:SL:INP:PHS',
            'IErr': 'SR-RF-DLLRF-01:I:SL:ERR',
            'QErr': 'SR-RF-DLLRF-01:Q:SL:ERR',
            'AErr': 'SR-RF-DLLRF-01:SL:ERR:AMP',
            'PErr': 'SR-RF-DLLRF-01:SL:ERR:PHS',
            'ASet': ['SR-RF-DLLRF-01:mV:AL:REF', 'RA-RaSIA01:RF-LLRF:AmpVCav'],
            'PSet': 'SR-RF-DLLRF-01:PL:REF',
            'AInc': 'SR-RF-DLLRF-01:AMPREF:INCRATE',
            'PInc': 'SR-RF-DLLRF-01:PHSREF:INCRATE',
            'Inp': 'SR-RF-DLLRF-01:SL:SEL',
            'PIL': 'SR-RF-DLLRF-01:SL:PILIMIT',
            'KI': 'SR-RF-DLLRF-01:SL:KI',
            'KP': 'SR-RF-DLLRF-01:SL:KP',
        },
        'Tun': {
            'Auto': 'SR-RF-DLLRF-01:TUNE',
            'DTune': 'SR-RF-DLLRF-01:DTune-RB',
            'DPhase': 'SR-RF-DLLRF-01:TUNE:DEPHS',
            'Acting': 'SR-RF-DLLRF-01:TUNE:OUT',
            'Deadbnd': 'SR-RF-DLLRF-01:TUNE:MARGIN:HI',
            'Oversht': 'SR-RF-DLLRF-01:TUNE:MARGIN:LO',
            'Pl1Down': 'SR-RF-DLLRF-01:PLG1:MOVE:DN',
            'Pl1Up': 'SR-RF-DLLRF-01:PLG1:MOVE:UP',
            'Pl2Down': 'SR-RF-DLLRF-01:PLG2:MOVE:DN',
            'Pl2Up': 'SR-RF-DLLRF-01:PLG2:MOVE:UP',
            'PlM1Curr': 'RA-RaSIA01:RF-CavPlDrivers:Dr1Current-Mon',
            'PlM2Curr': 'RA-RaSIA01:RF-CavPlDrivers:Dr2Current-Mon',
        },
        'FFlat': {
            'Sts': 'SR-RF-DLLRF-01:FF:ON',
            'Auto': 'SR-RF-DLLRF-01:FF',
            'Pos': 'SR-RF-DLLRF-01:FF:POS',
            'Gain1': 'SR-RF-DLLRF-01:FF:GAIN:CELL2',
            'Gain2': 'SR-RF-DLLRF-01:FF:GAIN:CELL4',
            'Cell1': 'SR-RF-DLLRF-01:FF:CELL2',
            'Cell2': 'SR-RF-DLLRF-01:FF:CELL4',
            'Deadband': 'SR-RF-DLLRF-01:FF:DEADBAND',
            'Err': 'SR-RF-DLLRF-01:FF:ERR',
        },
        'PwrMtr': {
            'Cav - Cell 2': {
                'W': 'SI-02SB:RF-P7Cav:PwrCell2-Mon',
                'dBm': 'SI-02SB:RF-P7Cav:PwrCell2dBm-Mon',
                'mV': 'SR-RF-DLLRF-01:CELL2:AMP',
                'color': 'darkRed',
            },
            'Cav - Cell 4': {
                'W': 'SI-02SB:RF-P7Cav:PwrCell4-Mon',
                'dBm': 'SI-02SB:RF-P7Cav:PwrCell4dBm-Mon',
                'mV': 'SR-RF-DLLRF-01:CAV:AMP',
                'color': 'black',
            },
            'Cav - Cell 6': {
                'W': 'SI-02SB:RF-P7Cav:PwrCell6-Mon',
                'dBm': 'SI-02SB:RF-P7Cav:PwrCell6dBm-Mon',
                'mV': 'SR-RF-DLLRF-01:CELL6:AMP',
                'color': 'darkBlue',
            },
            'Cav - Coup Fwd': {
                'W': 'SI-02SB:RF-P7Cav:PwrFwd-Mon',
                'dBm': 'SI-02SB:RF-P7Cav:PwrFwddBm-Mon',
                'mV': 'SR-RF-DLLRF-01:FWDCAV:AMP',
                'color': 'blue',
            },
            'Cav - Coup Rev': {
                'W': 'SI-02SB:RF-P7Cav:PwrRev-Mon',
                'dBm': 'SI-02SB:RF-P7Cav:PwrRevdBm-Mon',
                'mV': 'SR-RF-DLLRF-01:REVCAV:AMP',
                'color': 'red',
            },
            'SSA1 - Fwd Out': {
                'W': 'RA-ToSIA03:RF-SSAmpTower:PwrFwdOutLLRF-Mon',
                'dBm': 'RA-ToSIA03:RF-SSAmpTower:PwrFwdOutdBm-Mon',
                'mV': 'SR-RF-DLLRF-01:FWDSSA1:AMP',
                'color': 'magenta',
            },
            'SSA1 - Rev Out': {
                'W': 'RA-ToSIA03:RF-SSAmpTower:PwrRevOutLLRF-Mon',
                'dBm': 'RA-ToSIA03:RF-SSAmpTower:PwrRevOutdBm-Mon',
                'mV': 'SR-RF-DLLRF-01:REVSSA1:AMP',
                'color': 'darkGreen',
            },
            'SSA2 - Fwd Out': {
                'W': 'RA-ToSIA04:RF-SSAmpTower:PwrFwdOutLLRF-Mon',
                'dBm': 'RA-ToSIA04:RF-SSAmpTower:PwrFwdOutdBm-Mon',
                'mV': 'SR-RF-DLLRF-01:FWDSSA2:AMP',
                'color': 'yellow',
            },
            'SSA2 - Rev Out': {
                'W': 'RA-ToSIA04:RF-SSAmpTower:PwrRevOutLLRF-Mon',
                'dBm': 'RA-ToSIA04:RF-SSAmpTower:PwrRevOutdBm-Mon',
                'mV': 'SR-RF-DLLRF-01:REVSSA2:AMP',
                'color': 'cyan',
            },
            'Circ - Fwd Out': {
                'W': 'RA-TL:RF-Circulator-SIA:PwrFwdOut-Mon',
                'dBm': 'RA-TL:RF-Circulator-SIA:PwrFwdOutdBm-Mon',
                'mV': 'SR-RF-DLLRF-01:FWDCIRC:AMP',
                'color': 'darkCyan',
            },
        },
        'CavVGap': 'SI-02SB:RF-P7Cav:AmpVCav-Mon',
        'TempMon': {
            'Temp.': {
                'Cells': {
                    'Cell 1': 'SI-02SB:RF-P7Cav:Cylin1T-Mon',
                    'Cell 2': 'SI-02SB:RF-P7Cav:Cylin2T-Mon',
                    'Cell 3': 'SI-02SB:RF-P7Cav:Cylin3T-Mon',
                    'Cell 4': 'SI-02SB:RF-P7Cav:Cylin4T-Mon',
                    'Cell 5': 'SI-02SB:RF-P7Cav:Cylin5T-Mon',
                    'Cell 6': 'SI-02SB:RF-P7Cav:Cylin6T-Mon',
                    'Cell 7': 'SI-02SB:RF-P7Cav:Cylin7T-Mon',
                },
            },
            'Water Temp.': {
                'Cells': {
                    'Cell 1': 'SI-02SB:RF-P7Cav:Cylin1WT-Mon',
                    'Cell 2': 'SI-02SB:RF-P7Cav:Cylin2WT-Mon',
                    'Cell 3': 'SI-02SB:RF-P7Cav:Cylin3WT-Mon',
                    'Cell 4': 'SI-02SB:RF-P7Cav:Cylin4WT-Mon',
                    'Cell 5': 'SI-02SB:RF-P7Cav:Cylin5WT-Mon',
                    'Cell 6': 'SI-02SB:RF-P7Cav:Cylin6WT-Mon',
                    'Cell 7': 'SI-02SB:RF-P7Cav:Cylin7WT-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-02SB:RF-P7Cav:Disc1WT-Mon',
                    'Disc 2': 'SI-02SB:RF-P7Cav:Disc2WT-Mon',
                    'Disc 3': 'SI-02SB:RF-P7Cav:Disc3WT-Mon',
                    'Disc 4': 'SI-02SB:RF-P7Cav:Disc4WT-Mon',
                    'Disc 5': 'SI-02SB:RF-P7Cav:Disc5WT-Mon',
                    'Disc 6': 'SI-02SB:RF-P7Cav:Disc6WT-Mon',
                    'Disc 7': 'SI-02SB:RF-P7Cav:Disc7WT-Mon',
                    'Disc 8': 'SI-02SB:RF-P7Cav:Disc8WT-Mon',
                },
                'Input + Plungers + Coupler': {
                    'Input': 'SI-02SB:RF-P7Cav:WInT-Mon',
                    'Plunger 1': 'SI-02SB:RF-P7Cav:Pl1WT-Mon',
                    'Plunger 2': 'SI-02SB:RF-P7Cav:Pl2WT-Mon',
                    'Coupler': 'SI-02SB:RF-P7Cav:CoupWT-Mon',
                },
            },
            'Water dTemp.': {
                'Cells': {
                    'Cell 1': 'SI-02SB:RF-P7Cav:Cylin1WdT-Mon',
                    'Cell 2': 'SI-02SB:RF-P7Cav:Cylin2WdT-Mon',
                    'Cell 3': 'SI-02SB:RF-P7Cav:Cylin3WdT-Mon',
                    'Cell 4': 'SI-02SB:RF-P7Cav:Cylin4WdT-Mon',
                    'Cell 5': 'SI-02SB:RF-P7Cav:Cylin5WdT-Mon',
                    'Cell 6': 'SI-02SB:RF-P7Cav:Cylin6WdT-Mon',
                    'Cell 7': 'SI-02SB:RF-P7Cav:Cylin7WdT-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-02SB:RF-P7Cav:Disc1WdT-Mon',
                    'Disc 2': 'SI-02SB:RF-P7Cav:Disc2WdT-Mon',
                    'Disc 3': 'SI-02SB:RF-P7Cav:Disc3WdT-Mon',
                    'Disc 4': 'SI-02SB:RF-P7Cav:Disc4WdT-Mon',
                    'Disc 5': 'SI-02SB:RF-P7Cav:Disc5WdT-Mon',
                    'Disc 6': 'SI-02SB:RF-P7Cav:Disc6WdT-Mon',
                    'Disc 7': 'SI-02SB:RF-P7Cav:Disc7WdT-Mon',
                    'Disc 8': 'SI-02SB:RF-P7Cav:Disc8WdT-Mon',
                },
            },
            'Dissip. Power (Water)': {
                'Cells': {
                    'Cell 1': 'SI-02SB:RF-P7Cav:PwrDissCell1-Mon',
                    'Cell 2': 'SI-02SB:RF-P7Cav:PwrDissCell2-Mon',
                    'Cell 3': 'SI-02SB:RF-P7Cav:PwrDissCell3-Mon',
                    'Cell 4': 'SI-02SB:RF-P7Cav:PwrDissCell4-Mon',
                    'Cell 5': 'SI-02SB:RF-P7Cav:PwrDissCell5-Mon',
                    'Cell 6': 'SI-02SB:RF-P7Cav:PwrDissCell6-Mon',
                    'Cell 7': 'SI-02SB:RF-P7Cav:PwrDissCell7-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-02SB:RF-P7Cav:PwrDissDisc1-Mon',
                    'Disc 2': 'SI-02SB:RF-P7Cav:PwrDissDisc2-Mon',
                    'Disc 3': 'SI-02SB:RF-P7Cav:PwrDissDisc3-Mon',
                    'Disc 4': 'SI-02SB:RF-P7Cav:PwrDissDisc4-Mon',
                    'Disc 5': 'SI-02SB:RF-P7Cav:PwrDissDisc5-Mon',
                    'Disc 6': 'SI-02SB:RF-P7Cav:PwrDissDisc6-Mon',
                    'Disc 7': 'SI-02SB:RF-P7Cav:PwrDissDisc7-Mon',
                    'Disc 8': 'SI-02SB:RF-P7Cav:PwrDissDisc8-Mon',
                },
            },
            'Power (Water)': {
                'Cell 1': 'SI-02SB:RF-P7Cav:PwrWtCell1-Mon',
                'Cell 2': 'SI-02SB:RF-P7Cav:PwrWtCell2-Mon',
                'Cell 3': 'SI-02SB:RF-P7Cav:PwrWtCell3-Mon',
                'Cell 4': 'SI-02SB:RF-P7Cav:PwrWtCell4-Mon',
                'Cell 5': 'SI-02SB:RF-P7Cav:PwrWtCell5-Mon',
                'Cell 6': 'SI-02SB:RF-P7Cav:PwrWtCell6-Mon',
                'Cell 7': 'SI-02SB:RF-P7Cav:PwrWtCell7-Mon',
                # 'Total': 'SI-02SB:RF-P7Cav:PwrWtTotal-Mon',
                # 'Fwd': 'RA-RaSIA01:RF-RFCalSys:PwrW2-Mon',
            },
        },
        'FDL': {
            'Signals': (
                ('Cav', 'SR-RF-DLLRF-01:FDL:CAV:AMP', 'SR-RF-DLLRF-01:FDL:CAV:PHS', 'blue'),
                ('Fwd Cav', 'SR-RF-DLLRF-01:FDL:FWDCAV:AMP', 'SR-RF-DLLRF-01:FDL:FWDCAV:PHS', 'red'),
                ('Rev Cav', 'SR-RF-DLLRF-01:FDL:REVCAV:AMP', 'SR-RF-DLLRF-01:FDL:REVCAV:PHS', 'darkSlateBlue'),
                ('Fwd Ssa', 'SR-RF-DLLRF-01:FDL:FWDSSA:AMP', 'SR-RF-DLLRF-01:FDL:FWDSSA:PHS', 'darkGreen'),
                ('Rev Ssa', 'SR-RF-DLLRF-01:FDL:REVSSA:AMP', 'SR-RF-DLLRF-01:FDL:REVSSA:PHS', 'magenta'),
                ('Ctrl', 'SR-RF-DLLRF-01:FDL:CTRL:AMP', 'SR-RF-DLLRF-01:FDL:CTRL:PHS', 'darkCyan'),
                ('Ref', 'SR-RF-DLLRF-01:FDL:SL:REF:AMP', 'SR-RF-DLLRF-01:FDL:SL:REF:PHS', 'darkRed'),
                ('Err', 'SR-RF-DLLRF-01:FDL:SL:ERR:AMP', 'SR-RF-DLLRF-01:FDL:SL:ERR:PHS', 'purple'),
                ('Err Acc', 'SR-RF-DLLRF-01:FDL:SL:ERRACC:AMP', 'SR-RF-DLLRF-01:FDL:SL:ERRACC:PHS', 'saddlebrown'),
                ('MO', 'SR-RF-DLLRF-01:FDL:MO:AMP', 'SR-RF-DLLRF-01:FDL:MO:PHS', 'darkBlue'),
                ('Tune', None, 'SR-RF-DLLRF-01:FDL:TUNE:DEPHS', 'orangered'),
                ('Tune Filt', None, 'SR-RF-DLLRF-01:FDL:TUNE:DEPHS:FILT', 'darkOliveGreen')
            ),
            'Time': 'SR-RF-DLLRF-01:FDL:SCALE:32',
            'Mode': 'SR-RF-DLLRF-01:FDL:MODE',
            'SW Trig': 'SR-RF-DLLRF-01:FDL:SWTRIG',
            'HW Trig': 'SR-RF-DLLRF-01:FDL:HWTRIG',
            'Trig': 'SR-RF-DLLRF-01:FDL:TRIG:S',
            'Processing': 'SR-RF-DLLRF-01:FDL:PROCESSING',
            'Rearm': 'SR-RF-DLLRF-01:FDL:REARM',
            'Raw': 'SR-RF-DLLRF-01:FDL:RAW',
            'Qty': 'SR-RF-DLLRF-01:FDL:FrameQty-',
            'Size': 'SR-RF-DLLRF-01:FDL:Size-Mon',
            'Duration': 'SR-RF-DLLRF-01:FDL:Duration-Mon',
            'Delay': 'SR-RF-DLLRF-01:FDL:TriggerDelay'
        }
    },
}
