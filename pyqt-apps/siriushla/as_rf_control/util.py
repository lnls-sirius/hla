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
                        '0': 'RA-RaBO01:RF-LLRF:Inp1Intlk0-Mon',
                        '1': 'RA-RaBO01:RF-LLRF:Inp1Intlk1-Mon',
                        '2': 'RA-RaBO01:RF-LLRF:Inp1Intlk2-Mon',
                        '3': 'RA-RaBO01:RF-LLRF:Inp1Intlk3-Mon',
                        '4': 'RA-RaBO01:RF-LLRF:Inp1Intlk4-Mon',
                        '5': 'RA-RaBO01:RF-LLRF:Inp1Intlk5-Mon',
                        '6': 'RA-RaBO01:RF-LLRF:Inp1Intlk6-Mon',
                        '7': 'RA-RaBO01:RF-LLRF:Inp1Intlk7-Mon',
                        'Mon': 'RA-RaBO01:RF-LLRF:Inp1Intlk-Mon',
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
                'Input 2': {
                    'Status': {
                        '0': 'RA-RaBO01:RF-LLRF:Inp2Intlk0-Mon',
                        '1': 'RA-RaBO01:RF-LLRF:Inp2Intlk1-Mon',
                        '2': 'RA-RaBO01:RF-LLRF:Inp2Intlk2-Mon',
                        '3': 'RA-RaBO01:RF-LLRF:Inp2Intlk3-Mon',
                        '4': 'RA-RaBO01:RF-LLRF:Inp2Intlk4-Mon',
                        '5': 'RA-RaBO01:RF-LLRF:Inp2Intlk5-Mon',
                        '6': 'RA-RaBO01:RF-LLRF:Inp2Intlk6-Mon',
                        '7': 'RA-RaBO01:RF-LLRF:Inp2Intlk7-Mon',
                        'Mon': 'RA-RaBO01:RF-LLRF:Inp2Intlk-Mon',
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
                '1': 'RA-RaBO01:RF-LLRF:IntlkTs1-Mon',
                '2': 'RA-RaBO01:RF-LLRF:IntlkTs2-Mon',
                '3': 'RA-RaBO01:RF-LLRF:IntlkTs3-Mon',
                '4': 'RA-RaBO01:RF-LLRF:IntlkTs4-Mon',
                '5': 'RA-RaBO01:RF-LLRF:IntlkTs5-Mon',
                '6': 'RA-RaBO01:RF-LLRF:IntlkTs6-Mon',
                '7': 'RA-RaBO01:RF-LLRF:IntlkTs7-Mon',
            }
        },
        'Reset': {
            'Global': 'RA-RaBO02:RF-Intlk:Reset-Cmd',
            'LLRF': 'RA-RaBO01:RF-LLRF:IntlkReset-Cmd',
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
                'Cond': 'RA-RaBO01:RF-LLRF:VacuumFastRly-Mon',
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
                'Circulator In Reflected Power': 'RA-TLBO:RF-Circulator:RevIndBm-Mon'
            },
            'led': {
                'Circulator Arc Detector': 'RA-TLBO:RF-Circulator:Arc-Mon',
                'Circulator Arc Detector Supply Fail': 'RA-RaBO02:RF-ArcDetec-Circ:Fail-Mon',
                'Circulator Flow': 'RA-TLBO:RF-Circulator:FlwRt-Mon',
                'Load Flow': 'RA-TLBO:RF-Load:FlwRt-Mon',
                'TCU Status': 'RA-TLBO:RF-Circulator:IntlkOp-Mon',
            },
            'Circ Limits': (19.0, 23.0),
        },
        'SSA': {
            'Name': 'SSA',
            'Status': 'RA-ToBO:RF-SSAmpTower:Sts-Mon',
            'Power': 'RA-ToBO:RF-SSAmpTower:FwdOutLLRF-Mon',
            'SRC 1': {
                'Label': '300VDC',
                'Enable': 'RA-ToBO:RF-ACDCPanel:300VdcEnbl-Sel',
                'Disable': 'RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel',
                'Mon': 'RA-ToBO:RF-ACDCPanel:300Vdc-Sts'
            },
            'SRC 2': {
                'Label': 'DC/DC',
                'Enable': 'RA-ToBO:RF-SSAmpTower:CnvEnbl-Sel',
                'Disable': 'RA-ToBO:RF-SSAmpTower:CnvDsbl-Sel',
                'Mon': 'RA-ToBO:RF-SSAmpTower:Cnv-Sts'
            },
            'PinSw': {
                'Label': 'PinSw',
                'Enable': 'RA-RaBO01:RF-LLRFPreAmp:PinSwEnbl-Cmd',
                'Disable': 'RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd',
                'Mon': 'RA-RaBO01:RF-LLRFPreAmp:PinSw-Mon'
            },
            'PreDrive': 'RA-RaBO01:RF-LLRFPreAmp:FwdInAmp-Mon',
            'PreDriveThrs': 4,  # mV
        },
        'SSADtls': {
            'HeatSink': {
                'Temp': 'RA-ToBO:RF-HeatSink-H0$(hs_num):T-Mon',
                'TMS': 'RA-ToBO:RF-HeatSink-H0$(hs_num):Tms-Mon',
                'PT-100': [
                        'RA-ToSIA0$(NB):RF-HeatSink-H0$(hs_num):TUp-Mon',
                        'RA-ToSIA0$(NB):RF-HeatSink-H0$(hs_num):TDown-Mon'
                ]
            },
            'PreAmp': {
                'Temp': 'RA-RaBO01:RF-LLRFPreAmp:T1-Mon',
                'PT-100': 'RA-RaBO01:RF-LLRFPreAmp:T1Up-Mon'
            },
            'AC': {
                'Intlk': 'BO-ToBO:RF-ACDCPanel:Intlk-Mon',
                'Ctrl': 'BO-ToBO:RF-ACDCPanel:CtrlMode-Mon',
                '300Vdc': 'RA-ToBO:RF-ACDCPanel:300VdcEnbl-Mon',
                'Volt': 'BO-ToBO:RF-ACDCPanel:300Vdc-Mon',
                'Curr': 'BO-ToBO:RF-ACDCPanel:CurrentVdc-Mon'
            },
            'Rot': 'RA-ToBo:RF-SSAmpTower:HdFlwRt-Mon',
            'Pwr': 'RA-ToBo:RF-SSAmpTower:FwdOut-Mon',
        },
        'SSACurr': {
            'HeatSink': {
                'Curr': 'RA-ToBO:RF-SSAmp-H0$(hs_num)M$(m_num):Current$(curr_num)-Mon',
                'Fwd Top': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrFwdTop-Mon',
                'Rev Top': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrRevTop-Mon',
                'Fwd Bot': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrFwdBot-Mon',
                'Rev Bot': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrRevBot-Mon'
            },
            'PreAmp': {
                'HS': 'RA-ToBO:RF-SSAmp-H0$(hs_num)M$(m_num):Current$(curr_num)-Mon',
                'DC': 'RA-ToBO:RF-SSAmpTower:DC-Cmd'
            },
            'Pwr': {
                'Input': {
                    'Fwd': 'RA-ToBO:RF-SSAmpTower:PwrFwdIn-Mon',
                    'Rev': 'RA-ToBO:RF-SSAmpTower:PwrRevIn-Mon'
                },
                'Output': {
                    'Fwd': 'RA-ToBO:RF-SSAmpTower:PwrFwdOut-Mon',
                    'Rev': 'RA-ToBO:RF-SSAmpTower:PwrRevOut-Mon'
                }
            },
            'Offsets': {
                'FwdPwrTop': ['Forward Power - Top', 'RA-ToBO:OffsetConfig:UpperIncidentPower'],
                'RevPwrTop': ['Reverse Power - Top', 'RA-ToBO:OffsetConfig:UpperReflectedPower'],
                'FwdPwrBot': ['Forward Power - Bottom', 'RA-ToBO:OffsetConfig:LowerIncidentPower'],
                'RevPwrBot': ['Reverse Power - Bottom', 'RA-ToBO:OffsetConfig:LowerReflectedPower'],
                'FwdPwrIn': ['Forward Power In', 'RA-ToBO:OffsetConfig:InputIncidentPower'],
                'RevPwrIn': ['Reverse Power In', 'RA-ToBO:OffsetConfig:InputReflectedPower'],
                'FwdPwrOut': ['Forward Power Out', 'RA-ToBO:OffsetConfig:OutputIncidentPower'],
                'RevPwrOut': ['Reverse Power Out', 'RA-ToBO:OffsetConfig:InputReflectedPower'],
            },
            'Total': 'RA-ToBO:RF-SSAmpTower:DCCurrent-Mon',
            'Alarms': {
                'General': {
                    'Label': 'General Power',
                    'HIHI': 'RA-ToBO:AlarmConfig:GeneralPowerLimHiHi',
                    'HIGH': 'RA-ToBO:AlarmConfig:GeneralPowerLimHigh',
                    'LOW': 'RA-ToBO:AlarmConfig:GeneralPowerLimLow',
                    'LOLO': 'RA-ToBO:AlarmConfig:GeneralPowerLimLoLo',
                },
                'Inter': {
                    'Label': 'Intermediary Power',
                    'HIHI': 'RA-ToBO:AlarmConfig:InnerPowerLimHiHi',
                    'HIGH': 'RA-ToBO:AlarmConfig:InnerPowerLimHigh',
                    'LOW': 'RA-ToBO:AlarmConfig:InnerPowerLimLow',
                    'LOLO': 'RA-ToBO:AlarmConfig:InnerPowerLimLoLo',
                },
                'High': {
                    'Label': 'Current - High Limit',
                    'HIHI': 'RA-ToBO:AlarmConfig:CurrentLimHiHi',
                    'HIGH': 'RA-ToBO:AlarmConfig:CurrentLimHigh',
                    'LOW': 'RA-ToBO:AlarmConfig:CurrentLimLow',
                    'LOLO': 'RA-ToBO:AlarmConfig:CurrentLimLoLo',
                },
            }
        },
        'SL': {
            'ErrDtls': {
                'IRef': 'RA-RaBO01:RF-LLRF:SLRefI-Mon',
                'QRef': 'RA-RaBO01:RF-LLRF:SLRefQ-Mon',
                'IInp': 'RA-RaBO01:RF-LLRF:SLInpI-Mon',
                'QInp': 'RA-RaBO01:RF-LLRF:SLInpQ-Mon',
                'IErr': 'RA-RaBO01:RF-LLRF:SLErrorI-Mon',
                'QErr': 'RA-RaBO01:RF-LLRF:SLErrorQ-Mon',
            },
            'Params': {
                'Inp': 'RA-RaBO01:RF-LLRF:SLInp',
                'PIL': 'RA-RaBO01:RF-LLRF:SLPILim',
                'KI': 'RA-RaBO01:RF-LLRF:SLKI',
                'KP': 'RA-RaBO01:RF-LLRF:SLKP',
            },
            'Over': {
                'Enbl': 'RA-RaBO01:RF-LLRF:SL',
                'Mode': 'RA-RaBO01:RF-LLRF:LoopMode',
                'ASet': 'RA-RaBO01:RF-LLRF:ALRef',
                'PSet': 'RA-RaBO01:RF-LLRF:PLRef',
                'AInc': 'RA-RaBO01:RF-LLRF:AmpIncRate',
                'PInc': 'RA-RaBO01:RF-LLRF:PhsIncRate',
                'ARef': 'RA-RaBO01:RF-LLRF:SLRefAmp-Mon',
                'PRef': 'RA-RaBO01:RF-LLRF:SLRefPhs-Mon',
                'AInp': 'RA-RaBO01:RF-LLRF:SLInpAmp-Mon',
                'PInp': 'RA-RaBO01:RF-LLRF:SLInpPhs-Mon',
                'AErr': 'RA-RaBO01:RF-LLRF:SLErrorAmp-Mon',
                'PErr': 'RA-RaBO01:RF-LLRF:SLErrorPhs-Mon',
            },
            'ASet': 'RA-RaBO01:RF-LLRF:ALRefVGap',
        },
        'Tun': {
            'Auto': 'RA-RaBO01:RF-LLRF:Tune',
            'DTune': 'RA-RaBO01:RF-LLRF:Detune',
            'DPhase': 'RA-RaBO01:RF-LLRF:TuneDephs-Mon',
            'Acting': 'RA-RaBO01:RF-LLRF:TuneOut-Mon',
            'Deadbnd': 'RA-RaBO01:RF-LLRF:TuneMarginHI',
            'Oversht': 'RA-RaBO01:RF-LLRF:TuneMarginHI',
            'Pl1Down': 'BO-05D:RF-P5Cav:Plg1MoveDown-Mon',
            'Pl1Up': 'BO-05D:RF-P5Cav:Plg1MoveUp-Mon',
            'Pl2Down': 'BO-05D:RF-P5Cav:Plg2MoveDown-Mon',
            'Pl2Up': 'BO-05D:RF-P5Cav:Plg2MoveUp-Mon',
            'PlM1Curr': 'RA-RaBO01:RF-CavPlDrivers:Dr1Current-Mon',
            'PlM2Curr': 'RA-RaBO01:RF-CavPlDrivers:Dr2Current-Mon',
        },
        'FFlat': {
            'Sts': 'RA-RaBO01:RF-LLRF:FFOn-Mon',
            'Auto': 'RA-RaBO01:RF-LLRF:FFEnbl',
            'Pos': 'RA-RaBO01:RF-LLRF:FFDir',
            'Gain1': 'RA-RaBO01:RF-LLRF:FFGainCell2',
            'Gain2': 'RA-RaBO01:RF-LLRF:FFGainCell4',
            'Cell1': 'RA-RaBO01:RF-LLRF:FFCell2-Mon',
            'Cell2': 'RA-RaBO01:RF-LLRF:FFCell4-Mon',
            'Deadband': 'RA-RaBO01:RF-LLRF:FFDeadBand',
            'Err': 'RA-RaBO01:RF-LLRF:FFErr-Mon',
            'FwdMin': 'RA-RaBO01:RF-LLRF:TuneFwdMin-Mon'
        },
        'PwrMtr': {
            'Cavity Power': {
                'W': 'BO-05D:RF-P5Cav:Cell3PwrW-Mon',
                'dBm': 'BO-05D:RF-P5Cav:Cell3PwrdBm-Mon',
                'mV': 'BO-05D:RF-P5Cav:Cell3Amp-Mon',
                'color': 'blue',
            },
            'Power Forward': {
                'W': 'BO-05D:RF-P5Cav:FwdPwrW-Mon',
                'dBm': 'BO-05D:RF-P5Cav:FwdPwrdBm-Mon',
                'mV': 'BO-05D:RF-P5Cav:FwdAmp-Mon',
                'color': 'darkGreen',
            },
            'Power Reverse': {
                'W': 'BO-05D:RF-P5Cav:RevPwrW-Mon',
                'dBm': 'BO-05D:RF-P5Cav:RevPwrdBm-Mon',
                'mV': 'BO-05D:RF-P5Cav:RevAmp-Mon',
                'color': 'red',
            },
        },
        'CavVGap': 'BO-05D:RF-P5Cav:Cell3VGap-Mon',
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
                    'CavPwr': 'BO-05D:RF-P5Cav:Cell3BotPwrW-Mon',
                    'PowFwd': 'BO-05D:RF-P5Cav:FwdBotPwrW-Mon',
                    'PowRev': 'BO-05D:RF-P5Cav:RevBotPwrW-Mon'
                },
                'Top': {
                    'CavPwr': 'BO-05D:RF-P5Cav:Cell3TopPwrW-Mon',
                    'PowFwd': 'BO-05D:RF-P5Cav:FwdTopPwrW-Mon',
                    'PowRev': 'BO-05D:RF-P5Cav:RevTopPwrW-Mon'
                }
            },
            'mV': {
                'Bottom': {
                    'CavPwr': 'BO-05D:RF-P5Cav:Cell3BotAmp-Mon',
                    'PowFwd': 'BO-05D:RF-P5Cav:FwdBotAmp-Mon',
                    'PowRev': 'BO-05D:RF-P5Cav:RevBotAmp-Mon'
                },
                'Top': {
                    'CavPwr': 'BO-05D:RF-P5Cav:Cell3TopAmp-Mon',
                    'PowFwd': 'BO-05D:RF-P5Cav:FwdTopAmp-Mon',
                    'PowRev': 'BO-05D:RF-P5Cav:RevTopAmp-Mon'
                }
            }
        },
        'FDL': {
            'Signals': (
                ('Cav', 'RA-RaBO01:RF-LLRF:FDLCavAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLCavPhs-Mon', 'blue'),
                ('Fwd Cav', 'RA-RaBO01:RF-LLRF:FDLCavFwdAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLCavFwdPhs-Mon', 'red'),
                ('Rev Cav', 'RA-RaBO01:RF-LLRF:FDLCavRevAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLCavRevPhs-Mon', 'darkSlateBlue'),
                ('Fwd Ssa', 'RA-RaBO01:RF-LLRF:FDLFwdSSAAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLFwdSSAPhs-Mon', 'darkGreen'),
                ('Rev Ssa', 'RA-RaBO01:RF-LLRF:FDLRevSSAAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLRevSSAPhs-Mon', 'magenta'),
                ('Ctrl', 'RA-RaBO01:RF-LLRF:FDLCtrlAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLCtrlPhs-Mon', 'darkCyan'),
                ('Ref', 'RA-RaBO01:RF-LLRF:FDLSLRefAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLSLRefPhs-Mon', 'darkRed'),
                ('Err', 'RA-RaBO01:RF-LLRF:FDLSLErrAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLSLErrPhs-Mon', 'purple'),
                ('Err Acc', 'RA-RaBO01:RF-LLRF:FDLSLErrAccAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLSLErrAccPhs-Mon', 'saddlebrown'),
                ('MO', 'RA-RaBO01:RF-LLRF:FDLMOAmp-Mon', 'RA-RaBO01:RF-LLRF:FDLMOPhs-Mon', 'darkBlue'),
                ('Tune', None, 'RA-RaBO01:RF-LLRF:FDLTuneDephs-Mon', 'orangered'),
                ('Tune Filt', None, 'RA-RaBO01:RF-LLRF:FDLTuneDephsFilt-Mon', 'darkOliveGreen')
            ),
            'Time': 'RA-RaBO01:RF-LLRF:FDLScale32-Mon',
            'Mode': 'RA-RaBO01:RF-LLRF:FDLMode-Mon',
            'SW Trig': 'RA-RaBO01:RF-LLRF:FDLSwTrig-Mon',
            'HW Trig': 'RA-RaBO01:RF-LLRF:FDLHwTrig-Mon',
            'Trig': 'RA-RaBO01:RF-LLRF:FDLTrig-Cmd',
            'Processing': 'RA-RaBO01:RF-LLRF:FDLProcessing-Mon',
            'Rearm': 'RA-RaBO01:RF-LLRF:FDLRearm-Sel',
            'Raw': 'RA-RaBO01:RF-LLRF:FDLRaw',
            'Qty': 'RA-RaBO01:RF-LLRF:FDLFrame',
            'Size': 'RA-RaBO01:RF-LLRF:FDLSize-Mon',
            'Duration': 'RA-RaBO01:RF-LLRF:FDLDuration-Mon',
            'Delay': 'RA-RaBO01:RF-LLRF:FDLTrigDly'
        },
        'ADCs and DACs': {
            'Input': {
                '0': {
                    'Label': 'V Cav (RF In 1)',
                    'I': 'BO-05D:RF-P5Cav:Cell3I-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell3Q-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:Cell3Amp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell3Phs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:Cell3PwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:Cell3PwrdBm-Mon',
                },
                '2': {
                    'Label': 'Fwd Cav (RF In 2)',
                    'I': 'BO-05D:RF-P5Cav:FwdI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:FwdQ-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:FwdAmp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:FwdPhs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:FwdPwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:FwdPwrdBm-Mon',
                },
                '24': {
                    'Label': 'Rev Cav (RF In 3)',
                    'I': 'BO-05D:RF-P5Cav:RevI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:RevQ-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:RevAmp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:RevPhs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:RevPwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:RevPwrdBm-Mon',
                },
                '35': {
                    'Label': 'Master Osc (RF In 4)',
                    'I': 'RA-RaMO:RF-Gen:BOLLRFI-Mon',
                    'Q': 'RA-RaMO:RF-Gen:BOLLRFQ-Mon',
                    'Amp': 'RA-RaMO:RF-Gen:BOLLRFAmp-Mon',
                    'Phs': 'RA-RaMO:RF-Gen:BOLLRFPhs-Mon',
                    'PwrW': 'RA-RaMO:RF-Gen:BOLLRFPwrW-Mon',
                    'PwrdBm': 'RA-RaMO:RF-Gen:BOLLRFPwrdBm-Mon',
                },
                '20': {
                    'Label': 'Fwd SSA 1 (RF In 5)',
                    'I': 'RA-ToBO:RF-SSAmpTower:FwdOutI-Mon',
                    'Q': 'RA-ToBO:RF-SSAmpTower:FwdOutQ-Mon',
                    'Amp': 'RA-ToBO:RF-SSAmpTower:FwdOutAmp-Mon',
                    'Phs': 'RA-ToBO:RF-SSAmpTower:FwdOutPhs-Mon',
                    'PwrW': 'RA-ToBO:RF-SSAmpTower:FwdOutPwrW-Mon',
                    'PwrdBm': 'RA-ToBO:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                },
                '22': {
                    'Label': 'Rev SSA 1 (RF In 6)',
                    'I': 'RA-ToBO:RF-SSAmpTower:RevOutI-Mon',
                    'Q': 'RA-ToBO:RF-SSAmpTower:RevOutQ-Mon',
                    'Amp': 'RA-ToBO:RF-SSAmpTower:RevOutAmp-Mon',
                    'Phs': 'RA-ToBO:RF-SSAmpTower:RevOutPhs-Mon',
                    'PwrW': 'RA-ToBO:RF-SSAmpTower:RevOutPwrW-Mon',
                    'PwrdBm': 'RA-ToBO:RF-SSAmpTower:RevOutPwrdBm-Mon',
                },
                '37': {
                    'Label': 'V Cell 2 (RF In 7)',
                    'I': 'BO-05D:RF-P5Cav:Cell2I-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell2Q-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:Cell2Amp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell2Phs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:Cell2PwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:Cell2PwrdBm-Mon',
                },
                '39': {
                    'Label': 'V Cell 4 (RF In 8)',
                    'I': 'BO-05D:RF-P5Cav:Cell4I-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell4Q-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:Cell4Amp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell4Phs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:Cell4PwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:Cell4PwrdBm-Mon',
                },
                '41': {
                    'Label': 'V Cell 1 (RF In 9)',
                    'I': 'BO-05D:RF-P5Cav:Cell1I-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell1Q-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:Cell1Amp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell1Phs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:Cell1PwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:Cell1PwrdBm-Mon',
                },
                '43': {
                    'Label': 'V Cell 5 (RF In 10)',
                    'I': 'BO-05D:RF-P5Cav:Cell5I-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell5Q-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:Cell5Amp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell5Phs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:Cell5PwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:Cell5PwrdBm-Mon',
                },
                '45': {
                    'Label': 'Pre-Drive In (RF In 11)',
                    'I': 'RA-RaBO01:RF-LLRFPreAmp:FwdIn1I-Mon',
                    'Q': 'RA-RaBO01:RF-LLRFPreAmp:FwdIn1Q-Mon',
                    'Amp': 'RA-RaBO01:RF-LLRFPreAmp:FwdIn1Amp-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRFPreAmp:FwdIn1Phs-Mon',
                    'PwrW': 'RA-RaBO01:RF-LLRFPreAmp:FwdIn1PwrW-Mon',
                    'PwrdBm': 'RA-RaBO01:RF-LLRFPreAmp:FwdIn1PwrdBm-Mon',
                },
                '47': {
                    'Label': 'Fwd Pre-Drive (RF In 12)',
                    'I': 'RA-RaBO01:RF-LLRFPreAmp:FwdOut1I-Mon',
                    'Q': 'RA-RaBO01:RF-LLRFPreAmp:FwdOut1Q-Mon',
                    'Amp': 'RA-RaBO01:RF-LLRFPreAmp:FwdOut1Amp-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRFPreAmp:FwdOut1Phs-Mon',
                    'PwrW': 'RA-RaBO01:RF-LLRFPreAmp:FwdOut1PwrW-Mon',
                    'PwrdBm': 'RA-RaBO01:RF-LLRFPreAmp:FwdOut1PwrdBm-Mon',
                },
                '49': {
                    'Label': 'Rev Pre-Drive (RF In 13)',
                    'I': 'RA-RaBO01:RF-LLRFPreAmp:RevOut1I-Mon',
                    'Q': 'RA-RaBO01:RF-LLRFPreAmp:RevOut1Q-Mon',
                    'Amp': 'RA-RaBO01:RF-LLRFPreAmp:RevOut1Amp-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRFPreAmp:RevOut1Phs-Mon',
                    'PwrW': 'RA-RaBO01:RF-LLRFPreAmp:RevOut1PwrW-Mon',
                    'PwrdBm': 'RA-RaBO01:RF-LLRFPreAmp:RevOut1PwrdBm-Mon',
                },
                '51': {
                    'Label': 'Fwd Circ (RF In 14)',
                    'I': 'RA-TL:RF-Circulator-BO:FwdOutI-Mon',
                    'Q': 'RA-TL:RF-Circulator-BO:FwdOutQ-Mon',
                    'Amp': 'RA-TL:RF-Circulator-BO:FwdOutAmp-Mon',
                    'Phs': 'RA-TL:RF-Circulator-BO:FwdOutPhs-Mon',
                    'PwrW': 'RA-TL:RF-Circulator-BO:FwdOutPwrW-Mon',
                    'PwrdBm': 'RA-TL:RF-Circulator-BO:FwdOutPwrdBm-Mon',
                },
                '53': {
                    'Label': 'Rev Circ (RF In 15)',
                    'I': 'RA-TL:RF-Circulator-BO:RevOutI-Mon',
                    'Q': 'RA-TL:RF-Circulator-BO:RevOutQ-Mon',
                    'Amp': 'RA-TL:RF-Circulator-BO:RevOutAmp-Mon',
                    'Phs': 'RA-TL:RF-Circulator-BO:RevOutPhs-Mon',
                    'PwrW': 'RA-TL:RF-Circulator-BO:RevOutPwrW-Mon',
                    'PwrdBm': 'RA-TL:RF-Circulator-BO:RevOutPwrdBm-Mon',
                },
                '91': {
                    'Label': 'Mux DACsIF (RF In 16)',
                    'I': 'RA-RaBO01:RF-LLRF:DACIFI-Mon',
                    'Q': 'RA-RaBO01:RF-LLRF:DACIFQ-Mon',
                    'Amp': 'RA-RaBO01:RF-LLRF:DACIFAmp-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRF:DACIFPhs-Mon',
                    'PwrW': 'RA-RaBO01:RF-LLRF:DACIFPwrW-Mon',
                    'PwrdBm': 'RA-RaBO01:RF-LLRF:DACIFPwrdBm-Mon',
                },
            },
            'Control': {
                'ADC': {
                    'Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaBO01:RF-LLRF:PhShADC'],
                    '2': ['Phase Shift Cavity', 'RA-RaBO01:RF-LLRF:PhShCav'],
                    '3': ['Phase Shift Fwd Cav', 'RA-RaBO01:RF-LLRF:PhShFwdCav'],
                    '8': ['Gain Fwd Cavity', 'RA-RaBO01:RF-LLRF:GainFwdCav'],
                    '4': ['Phase Shift Fwd SSA 1', 'RA-RaBO01:RF-LLRF:PhShFwdSSA1'],
                    '9': ['Gain Fwd SSA 1', 'RA-RaBO01:RF-LLRF:GainFwdSSA1'],
                    '5': ['Phase Shift Fwd SSA 2', 'RA-RaBO01:RF-LLRF:PhShFwdSSA2'],
                    '10': ['Gain Fwd SSA 2', 'RA-RaBO01:RF-LLRF:GainFwdSSA2'],
                    '6': ['Phase Shift Fwd SSA 3', 'RA-RaBO01:RF-LLRF:PhShFwdSSA3'],
                    '11': ['Gain Fwd SSA 3', 'RA-RaBO01:RF-LLRF:GainFwdSSA3'],
                    '7': ['Phase Shift Fwd SSA 4', 'RA-RaBO01:RF-LLRF:PhShFwdSSA4'],
                    '12': ['Gain Fwd SSA 4', 'RA-RaBO01:RF-LLRF:GainFwdSSA4'],
                },
                'DAC': {
                    'Enable': ['102 - DACs Phase Shift Enable', 'RA-RaBO01:RF-LLRF:PhShDAC'],
                    '14': ['Phase Shift Drive SSA 1', 'RA-RaBO01:RF-LLRF:PhShSSA1'],
                    '18': ['Gain Drive SSA 1', 'RA-RaBO01:RF-LLRF:GainSSA1'],
                    '15': ['Phase Shift Drive SSA 2', 'RA-RaBO01:RF-LLRF:PhShSSA2'],
                    '19': ['Gain Drive SSA 2', 'RA-RaBO01:RF-LLRF:GainSSA2'],
                    '16': ['Phase Shift Drive SSA 3', 'RA-RaBO01:RF-LLRF:PhShSSA3'],
                    '20': ['Gain Drive SSA 3', 'RA-RaBO01:RF-LLRF:GainSSA3'],
                    '17': ['Phase Shift Drive SSA 4', 'RA-RaBO01:RF-LLRF:PhShSSA4'],
                    '21': ['Gain Drive SSA 4', 'RA-RaBO01:RF-LLRF:GainSSA4']
                }
            }
        },
        'Hardware': {
            'FPGA': {
                'Temp': 'RA-RaBO01:RF-LLRF:FPGATemp-Mon',
                'Temp Max': 'RA-RaBO01:RF-LLRF:FPGATempMax-Mon',
                'Temp Min': 'RA-RaBO01:RF-LLRF:FPGATempMin-Mon',
                'Vint': 'RA-RaBO01:RF-LLRF:FPGAVint-Mon',
                'Vint Max': 'RA-RaBO01:RF-LLRF:FPGAVintMax-Mon',
                'Vint Min': 'RA-RaBO01:RF-LLRF:FPGAVintMin-Mon',
                'Vaux': 'RA-RaBO01:RF-LLRF:FPGAVaux-Mon',
                'Vaux Max': 'RA-RaBO01:RF-LLRF:FPGAVauxMax-Mon',
                'Vaux Min': 'RA-RaBO01:RF-LLRF:FPGAVauxMin-Mon'
            },
            'Mo1000': {
                'Temp': 'RA-RaBO01:RF-LLRF:MO1000Temp-Mon',
                'Temp DAC 1': 'RA-RaBO01:RF-LLRF:MO1000DAC1Temp-Mon',
                'Temp DAC 2': 'RA-RaBO01:RF-LLRF:MO1000DAC2Temp-Mon'
            },
            'Mi125': {
                'Temp': 'RA-RaBO01:RF-LLRF:M125Temp-Mon',
            },
            'GPIO': {
                'ADC 0': 'RA-RaBO01:RF-LLRF:GPIOADC0-Mon',
                'ADC 3': 'RA-RaBO01:RF-LLRF:GPIOADC3-Mon'
            },
            'Clock Src': 'RA-RaBO01:RF-LLRF:MO1000ClkSrc-Sel',
            'Loop Trigger': 'RA-RaBO01:RF-LLRF:LoopTrigProc-Cmd',
            'PLL': 'RA-RaBO01:RF-LLRF:MO1000PLL-Mon',
            'FPGA Init': 'RA-RaBO01:RF-LLRF:FPGAInit-Cmd',
            'Cav Type': 'RA-RaBO01:RF-LLRF:CavType-Mon',
            'Errors': 'RA-RaBO01:RF-LLRF:InitErrors-Mon',
            'Int. Errors': 'RA-RaBO01:RF-LLRF:InternalErr-Mon',
            'Int. Err. Clear': 'RA-RaBO01:RF-LLRF:ResetIntError-Cmd',
            'Init': 'RA-RaBO01:RF-LLRF:InitStatus-Mon',
            'Versions': {
                'Firmware': 'RA-RaBO01:RF-LLRF:FPGAVersion-Mon',
                'IOC': 'RA-RaBO01:RF-LLRF:Version-Mon'
            },
        },
        'Loops': {
            'Control': {
                '24 mV': ['Amp Loop Ref (mV)', 'RA-RaBO01:RF-LLRF:ALRef'],
                '24 VGap': ['Amp Loop Ref (VGap)', 'RA-RaBO01:RF-LLRF:ALRefVGap'],
                '25': ['Phase Loop Ref', 'RA-RaBO01:RF-LLRF:PLRef'],
                '29': ['Voltage Inc. Rate', 'RA-RaBO01:RF-LLRF:AmpIncRate'],
                '28': ['Phase Inc. Rate', 'RA-RaBO01:RF-LLRF:PhsIncRate'],
                '106': ['Look Reference', 'RA-RaBO01:RF-LLRF:LookRef-Cmd'],
                '114': ['Rect/Polar Mode Select', 'RA-RaBO01:RF-LLRF:LoopMode'],
                '107': ['Quadrant Selection', 'RA-RaBO01:RF-LLRF:Quad'],
                '26 mV': ['Amp Ref Min (mV)', 'RA-RaBO01:RF-LLRF:AmpRefMin'],
                '26 VGap': ['Amp Ref Min (VGap)', 'RA-RaBO01:RF-LLRF:AmpRefMinVGap'],
                '27': ['Phase Ref Min', 'RA-RaBO01:RF-LLRF:PhsRefMin'],
                '30': ['Open Loop Gain', 'RA-RaBO01:RF-LLRF:OLGain'],
                '31': ['Phase Correction Control', 'RA-RaBO01:RF-LLRF:PhsCorrection'],
                '80': ['Phase Correct Error', 'RA-RaBO01:RF-LLRF:PhsCorrErr-Mon'],
                '81': ['Phase Correct Control', 'RA-RaBO01:RF-LLRF:PhsCorrCtrl-Mon'],
                '125': ['Fwd Min Amp & Phs', 'RA-RaBO01:RF-LLRF:LoopFwdMin'],
                'Mode': 'RA-RaBO01:RF-LLRF:LoopMode-Sts',
                'Limits': {
                    '24': ['Amp Loop Ref', 'RA-RaBO01:RF-LLRF:ALRef'],
                    '30': ['Open Loop Gain', 'RA-RaBO01:RF-LLRF:OLGain'],
                    '0': ['Slow Loop Kp', 'RA-RaBO01:RF-LLRF:SLKP'],
                }
            },
            'General': {
                '0': {
                    'Label': 'Cavity Voltage',
                    'InPhs': 'BO-05D:RF-P5Cav:Cell3I-Mon',
                    'Quad': 'BO-05D:RF-P5Cav:Cell3Q-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:Cell3Amp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell3Phs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:Cell3PwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:Cell3PwrdBm-Mon',
                },
                '2': {
                    'Label': 'Forward Power',
                    'InPhs': 'BO-05D:RF-P5Cav:FwdI-Mon',
                    'Quad': 'BO-05D:RF-P5Cav:FwdQ-Mon',
                    'Amp': 'BO-05D:RF-P5Cav:FwdAmp-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:FwdPhs-Mon',
                    'PwrW': 'BO-05D:RF-P5Cav:FwdPwrW-Mon',
                    'PwrdBm': 'BO-05D:RF-P5Cav:FwdPwrdBm-Mon',
                },
                '20': {
                    'Label': 'Fwd Pwr SSA 1',
                    'InPhs': 'RA-ToBO:RF-SSAmpTower:FwdOutI-Mon',
                    'Quad': 'RA-ToBO:RF-SSAmpTower:FwdOutQ-Mon',
                    'Amp': 'RA-ToBO:RF-SSAmpTower:FwdOutAmp-Mon',
                    'Phs': 'RA-ToBO:RF-SSAmpTower:FwdOutPhs-Mon',
                    'PwrW': 'RA-ToBO:RF-SSAmpTower:FwdOutPwrW-Mon',
                    'PwrdBm': 'RA-ToBO:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                },
                '32': {
                    'Label': 'Ang Cav Fwd',
                    'InPhs': '-',
                    'Quad': '-',
                    'Amp': '-',
                    'Phs': 'RA-RaBO01:RF-LLRF:Dephase-Mon',
                    'PwrW': '-',
                    'PwrdBm': '-',
                },
            },
            'Rect': {
                'Slow': {
                    'Control': {
                        '100': ['Enable', 'RA-RaBO01:RF-LLRF:SL'],
                        '110': ['Input Selection', 'RA-RaBO01:RF-LLRF:SLInp'],
                        '13': ['PI Limit', 'RA-RaBO01:RF-LLRF:SLPILim'],
                        '1': ['Ki', 'RA-RaBO01:RF-LLRF:SLKI'],
                        '0': ['Kp', 'RA-RaBO01:RF-LLRF:SLKP']
                    },
                    '512': {
                        'Label': 'Reference',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SLRefI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SLRefQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SLRefAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SLRefPhs-Mon'
                    },
                    '120': {
                        'Label': 'Input',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SLInpI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SLInpQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SLInpAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SLInpPhs-Mon'
                    },
                    '14': {
                        'Label': 'Error',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SLErrorI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SLErrorQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SLErrorAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SLErrorPhs-Mon'
                    },
                    '16': {
                        'Label': 'Error Accum',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SLErrAccI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SLErrAccQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SLErrAccAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SLErrAccPhs-Mon'
                    },
                    '71': {
                        'Label': 'Slow Control Output',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SLCtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SLCtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SLCtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SLCtrlPhs-Mon'
                    },
                },
                'Fast': {
                    'Control': {
                        '115': ['Enable', 'RA-RaBO01:RF-LLRF:FL'],
                        '111': ['Input Selection', 'RA-RaBO01:RF-LLRF:FLInp'],
                        '124': ['PI Limit', 'RA-RaBO01:RF-LLRF:FLPILim'],
                        '119': ['Ki', 'RA-RaBO01:RF-LLRF:FLKI'],
                        '118': ['Kp', 'RA-RaBO01:RF-LLRF:FLKP']
                    },
                    '124': {
                        'Label': 'Reference',
                        'InPhs': 'RA-RaBO01:RF-LLRF:FLRefI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:FLRefQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:FLRefAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:FLRefPhs-Mon'
                    },
                    '112': {
                        'Label': 'Input',
                        'InPhs': 'RA-RaBO01:RF-LLRF:FLInpI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:FLInpQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:FLInpAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:FLInpPhs-Mon'
                    },
                    '118': {
                        'Label': 'Fast Control Output',
                        'InPhs': 'RA-RaBO01:RF-LLRF:FLCtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:FLCtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:FLCtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:FLCtrlPhs-Mon'
                    },
                    '6': {
                        'Label': 'SSA 1 Control Signal',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SSACtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SSACtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SSACtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SSACtrlPhs-Mon'
                    },
                }
            },
            'Polar': {
                '527': {
                    'Label': 'Amp Ref',
                    'InPhs': '-',
                    'Quad': '-',
                    'Amp': 'RA-RaBO01:RF-LLRF:AmpRefOld-Mon',
                    'Phs': '-',
                    'PwrW': '-',
                    'PwrdBm': '-',
                },
                'Amp': {
                    'Control': {
                        '116': ['Enable', 'RA-RaBO01:RF-LLRF:AL'],
                        '112': ['Input Selection', 'RA-RaBO01:RF-LLRF:ALInp'],
                        '121': ['Ki', 'RA-RaBO01:RF-LLRF:ALKI'],
                        '120': ['Kp', 'RA-RaBO01:RF-LLRF:ALKP']
                    },
                    '100': {
                        'Label': 'Amp Loop Input',
                        'InPhs': 'RA-RaBO01:RF-LLRF:ALInpI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:ALInpQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:ALInpAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:ALInpPhs-Mon'
                    },
                    '104': {
                        'Label': 'Amp of Input',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': 'RA-RaBO01:RF-LLRF:ALAmpInp-Mon',
                        'Phs': '-'
                    },
                    '105': {
                        'Label': 'Phase of Input',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:ALPhsInp-Mon'
                    },
                    '109': {
                        'Label': 'Error',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': 'RA-RaBO01:RF-LLRF:ALErr-Mon',
                        'Phs': '-'
                    },
                    '110': {
                        'Label': 'Error Accum',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': 'RA-RaBO01:RF-LLRF:ALErrAcc-Mon',
                        'Phs': '-'
                    },
                    '528': {
                        'Label': 'Phase Ref',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:PhsRefOld-Mon'
                    }
                },
                'Phase': {
                    'Control': {
                        '117': ['Enable', 'RA-RaBO01:RF-LLRF:PL'],
                        '113': ['Input Selection', 'RA-RaBO01:RF-LLRF:PLInp'],
                        '123': ['Ki', 'RA-RaBO01:RF-LLRF:PLKI'],
                        '122': ['Kp', 'RA-RaBO01:RF-LLRF:PLKP']
                    },
                    '102': {
                        'Label': 'Phase Loop Input',
                        'InPhs': 'RA-RaBO01:RF-LLRF:PLInpI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:PLInpQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:PLInpAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:PLInpPhs-Mon'
                    },
                    '106': {
                        'Label': 'Amp of Input',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': 'RA-RaBO01:RF-LLRF:PLAmpInp-Mon',
                        'Phs': '-'
                    },
                    '107': {
                        'Label': 'Phase of Input',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:PLPhsInp-Mon'
                    },
                    '112': {
                        'Label': 'Error',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:PLErr-Mon'
                    },
                    '113': {
                        'Label': 'Error Accum',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:PLErrAcc-Mon'
                    },
                    '114': {
                        'Label': 'Polar Control Output',
                        'InPhs': 'RA-RaBO01:RF-LLRF:POCtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:POCtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:POCtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:POCtrlPhs-Mon'
                    },
                    '6': {
                        'Label': 'SSA 1 Control Signal',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SSACtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SSACtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SSACtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SSACtrlPhs-Mon'
                    },
                }
            }
        },
        'RampDtls': {
            'Control': {
                'Ramp Enable': 'RA-RaBO01:RF-LLRF:RmpEnbl',
                'Ramp Down Disable': 'RA-RaBO01:RF-LLRF:RmpDownDsbl',
                '356': ['T1 Ramp Delay After Trig', 'RA-RaBO01:RF-LLRF:RmpTs1'],
                '357': ['T2 Ramp Up', 'RA-RaBO01:RF-LLRF:RmpTs2'],
                '358': ['T3 Ramp Top', 'RA-RaBO01:RF-LLRF:RmpTs3'],
                '359': ['T4 Ramp Down', 'RA-RaBO01:RF-LLRF:RmpTs4'],
                '360': ['Ramp Increase Rate', 'RA-RaBO01:RF-LLRF:RmpIncTime'],
                '164': ['Ref Top', 'RA-RaBO01:RF-LLRF:RefTopAmp-Mon', 'red'],
                '362 mV': ['Amp Ramp Top (mV)', 'RA-RaBO01:RF-LLRF:RmpAmpTop'],
                '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-RaBO01:RF-LLRF:RmpAmpTopVGap'],
                '364': ['Phase Ramp Top', 'RA-RaBO01:RF-LLRF:RmpPhsTop'],
                '184': ['Ref Bot', 'RA-RaBO01:RF-LLRF:RefBotAmp-Mon', 'blue'],
                '361 mV': ['Amp Ramp Bot (mV)', 'RA-RaBO01:RF-LLRF:RmpAmpBot'],
                '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-RaBO01:RF-LLRF:RmpAmpBotVGap'],
                '363': ['Phase Ramp Bot', 'RA-RaBO01:RF-LLRF:RmpPhsBot'],
                '536': ['Ramp Top', 'RA-RaBO01:RF-LLRF:RmpTop-Mon', 'green'],
                '533': ['Ramp Ready', 'RA-RaBO01:RF-LLRF:RmpRdy-Mon'],
                '365': ['Amp Ramp Up Slope', 'RA-RaBO01:RF-LLRF:RmpAmpUpCnt'],
                '366': ['Amp Ramp Down Slope', 'RA-RaBO01:RF-LLRF:RmpAmpDownCnt'],
                '367': ['Phase Ramp Up Slope', 'RA-RaBO01:RF-LLRF:RmpPhsUpCnt'],
                '368': ['Phase Ramp Down Slope', 'RA-RaBO01:RF-LLRF:RmpPhsDownCnt'],
                'Limits': {
                    '362': ['Top Reference', 'RA-RaBO01:RF-LLRF:RmpAmpTop'],
                    '361': ['Bot Reference', 'RA-RaBO01:RF-LLRF:RmpAmpBot']
                }
            },
            'Diagnostics': {
                'Top': {
                    '164': {
                        'Label': 'Ref',
                        'InPhs': 'RA-RaBO01:RF-LLRF:RefTopI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:RefTopQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:RefTopAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:RefTopPhs-Mon',
                        'PwrW': 'RA-RaBO01:RF-LLRF:RefTopPwrW-Mon',
                        'PwrdBm': 'RA-RaBO01:RF-LLRF:RefTopPwrdBm-Mon',
                    },
                    '150': {
                        'Label': 'Cell 3',
                        'InPhs': 'BO-05D:RF-P5Cav:TopI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:TopQ-Mon',
                        'Amp': 'BO-05D:RF-P5Cav:TopAmp-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:TopPhs-Mon',
                        'PwrW': 'BO-05D:RF-P5Cav:TopPwrW-Mon',
                        'PwrdBm': 'BO-05D:RF-P5Cav:TopPwrdBm-Mon',
                    },
                    '152': {
                        'Label': 'Cell 2',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:FwdTopI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:FwdTopQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:FwdTopAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:FwdTopPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:FwdTopPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:FwdTopPwrdBm-Mon',
                    },
                    '154': {
                        'Label': 'Cell 4',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:RevTopI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:RevTopQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:RevTopAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:RevTopPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:RevTopPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:RevTopPwrdBm-Mon',
                    },
                    '190': {
                        'Label': 'Fwd Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:FwdTopI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:FwdTopQ-Mon',
                        'Amp': 'BO-05D:RF-P5Cav:FwdTopAmp-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:FwdTopPhs-Mon',
                        'PwrW': 'BO-05D:RF-P5Cav:FwdTopPwrW-Mon',
                        'PwrdBm': 'BO-05D:RF-P5Cav:FwdTopPwrdBm-Mon',
                    },
                    '156': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:FwdTopI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:FwdTopQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:FwdTopAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:FwdTopPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:FwdTopPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:FwdTopPwrdBm-Mon',
                    },
                    '158': {
                        'Label': 'Rev Pwr SSA 1',
                        'InPhs':  'RA-ToBO:RF-SSAmpTower:RevTopI-Mon',
                        'Quad':  'RA-ToBO:RF-SSAmpTower:RevTopQ-Mon',
                        'Amp':  'RA-ToBO:RF-SSAmpTower:RevTopAmp-Mon',
                        'Phs':  'RA-ToBO:RF-SSAmpTower:RevTopPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:RevTopPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:RevTopPwrdBm-Mon',
                    },
                    '160': {
                        'Label': 'Rev Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:RevTopI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:RevTopQ-Mon',
                        'Amp': 'BO-05D:RF-P5Cav:RevTopAmp-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:RevTopPhs-Mon',
                        'PwrW': 'BO-05D:RF-P5Cav:RevTopPwrW-Mon',
                        'PwrdBm': 'BO-05D:RF-P5Cav:RevTopPwrdBm-Mon',
                    },
                    '168': {
                        'Label': 'Loop Error',
                        'InPhs': 'RA-RaBO01:RF-LLRF:ErrTopI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:ErrTopQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:ErrTopAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:ErrTopPhs-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    '166': {
                        'Label': 'Control',
                        'InPhs': 'RA-RaBO01:RF-LLRF:CtrlTopI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:CtrlTopQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:CtrlTopAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:CtrlTopPhs-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    '162': {
                        'Label': 'Tuning Dephase',
                        'PV': 'RA-RaBO01:RF-LLRF:TuneDephsTop-Mon'
                    },
                    '163': {
                        'Label': 'FF Error',
                        'PV': 'RA-RaBO01:RF-LLRF:FFErrTop-Mon'
                    },
                    '531': {
                        'Label': 'Ramp Trigger',
                        'PV': 'RA-RaBO01:RF-LLRF:RmpTrigger-Mon'
                    }
                },
                'Bot': {
                    '184': {
                        'Label': 'Ref',
                        'InPhs': 'RA-RaBO01:RF-LLRF:RefBotI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:RefBotQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:RefBotAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:RefBotPhs-Mon',
                        'PwrW': 'RA-RaBO01:RF-LLRF:RefBotPwrW-Mon',
                        'PwrdBm': 'RA-RaBO01:RF-LLRF:RefBotPwrdBm-Mon',
                    },
                    '170': {
                        'Label': 'Cell 3',
                        'InPhs': 'BO-05D:RF-P5Cav:BotI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:BotQ-Mon',
                        'Amp': 'BO-05D:RF-P5Cav:BotAmp-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:BotPhs-Mon',
                        'PwrW': 'BO-05D:RF-P5Cav:BotPwrW-Mon',
                        'PwrdBm': 'BO-05D:RF-P5Cav:BotPwrdBm-Mon',
                    },
                    '172': {
                        'Label': 'Cell 2',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:FwdBotI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:FwdBotQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:FwdBotAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:FwdBotPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:FwdBotPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:FwdBotPwrdBm-Mon',
                    },
                    '174': {
                        'Label': 'Cell 4',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:RevBotI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:RevBotQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:RevBotAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:RevBotPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:RevBotPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:RevBotPwrdBm-Mon',
                    },
                    '192': {
                        'Label': 'Fwd Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:FwdBotI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:FwdBotQ-Mon',
                        'Amp': 'BO-05D:RF-P5Cav:FwdBotAmp-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:FwdBotPhs-Mon',
                        'PwrW': 'BO-05D:RF-P5Cav:FwdBotPwrW-Mon',
                        'PwrdBm': 'BO-05D:RF-P5Cav:FwdBotPwrdBm-Mon',
                    },
                    '176': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:FwdBotI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:FwdBotQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:FwdBotAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:FwdBotPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:FwdBotPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:FwdBotPwrdBm-Mon',
                    },
                    '178': {
                        'Label': 'Rev Pwr SSA 1',
                        'InPhs': 'RA-ToBO:RF-SSAmpTower:RevBotI-Mon',
                        'Quad': 'RA-ToBO:RF-SSAmpTower:RevBotQ-Mon',
                        'Amp': 'RA-ToBO:RF-SSAmpTower:RevBotAmp-Mon',
                        'Phs': 'RA-ToBO:RF-SSAmpTower:RevBotPhs-Mon',
                        'PwrW': 'RA-ToBO:RF-SSAmpTower:RevBotPwrW-Mon',
                        'PwrdBm': 'RA-ToBO:RF-SSAmpTower:RevBotPwrdBm-Mon',
                    },
                    '180': {
                        'Label': 'Rev Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:RevBotI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:RevBotQ-Mon',
                        'Amp': 'BO-05D:RF-P5Cav:RevBotAmp-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:RevBotPhs-Mon',
                        'PwrW': 'BO-05D:RF-P5Cav:RevBotPwrW-Mon',
                        'PwrdBm': 'BO-05D:RF-P5Cav:RevBotPwrdBm-Mon',
                    },
                    '188': {
                        'Label': 'Loop Error',
                        'InPhs': 'RA-RaBO01:RF-LLRF:ErrBotI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:ErrBotQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:ErrBotAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:ErrBotPhs-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    '186': {
                        'Label': 'Control',
                        'InPhs': 'RA-RaBO01:RF-LLRF:CtrlBotI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:CtrlBotQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:CtrlBotAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:CtrlBotPhs-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    '183': {
                        'Label': 'FF Error',
                        'PV': 'RA-RaBO01:RF-LLRF:FFErrBot-Mon'
                    },
                    '531': {
                        'Label': 'Ramp Trigger',
                        'PV': 'RA-RaBO01:RF-LLRF:RmpTrigger-Mon'
                    }
                }
            }
        },
        'AutoStart': {
            '22': ['Automatic Startup Enable', 'RA-RaBO01:RF-LLRF:AutoStartupEnbl'],
            '23': ['Command Start', 'RA-RaBO01:RF-LLRF:AutoStartupCmdStart'],
            '400': ['EPS Interlock', 'RA-RaBO01:RF-LLRF:EPSEnbl'],
            '401': ['Interlock Bypass', 'RA-RaBO01:RF-LLRF:FIMEnbl'],
            'Diag': {
                '500': ['State Start', 'RA-RaBO01:RF-LLRF:AutoStartState-Mon'],
                '400': ['Tx Ready', 'RA-RaBO01:RF-LLRF:SSARdy-Mon'],
                '401': ['Fast Interlock', 'RA-RaBO01:RF-LLRF:IntlkAll-Mon'],
                '308': ['Slow Loop Fwd Min', 'RA-RaBO01:RF-LLRF:SLFwdMin-Mon'],
                '309': ['Fast Loop Fwd Min', 'RA-RaBO01:RF-LLRF:FLFwdMin-Mon'],
                '310': ['Amp Loop Fwd Min', 'RA-RaBO01:RF-LLRF:ALFwdMin-Mon'],
                '311': ['Phase Loop Fwd Min', 'RA-RaBO01:RF-LLRF:PLFwdMin-Mon'],
                '307': ['Tuning Fwd Min', 'RA-RaBO01:RF-LLRF:TuneFwdMin-Mon']
            }
        },
        'Conditioning': {
            '200': ['Pulse Mode Enable', 'RA-RaBO01:RF-LLRF:CondEnbl'],
            '201': ['Auto Conditioning Enable', 'RA-RaBO01:RF-LLRF:CondAuto'],
            '204': ['Conditioning Freq', 'RA-RaBO01:RF-LLRF:CondFreq'],
            '540': ['Cond Freq Diag', 'RA-RaBO01:RF-LLRF:CondFreq-Mon'],
            '205': ['Duty Cycle', 'RA-RaBO01:RF-LLRF:CondDuty2'],
            '530': ['Duty Cycle RB', 'RA-RaBO01:RF-LLRF:CondDutyCycle-Mon'],
            '79': ['Vacuum', 'RA-RaBO01:RF-LLRF:VacuumFastRly-Mon'],
            'Relay': {
                'CGC Fast Relay': 'BO-05D:VA-CCG-RFC:FastRelay',
                'Relay Setpoint RB': 'BO-RA02:VA-VGC-01:Relay1:Setpoint',
                'Relay Hysteria RB': 'BO-RA02:VA-VGC-01:Relay1:Hyst'
            }
        },
        'TunDtls': {
            'General': {
                '34': ['Fwd Pwr Amplitude', 'RA-RaBO01:RF-LLRF:CavFwdAmp-Mon'],
                '19': ['Fwd Pwr Phase Angle', 'RA-RaBO01:RF-LLRF:CavFwdPhs-Mon'],
                '33': ['Cavity Amplitude', 'RA-RaBO01:RF-LLRF:CavAmp-Mon'],
                '18': ['Cavity Phase Angle', 'RA-RaBO01:RF-LLRF:CavPhs-Mon'],
                '307': ['Tuning Fwd Min', 'RA-RaBO01:RF-LLRF:TuneFwdMin-Mon'],
                '303': ['Pulses Frequency', 'RA-RaBO01:RF-LLRF:TuneFreq'],
            },
            'Manual': {
                '302': ['Number of Pulses', 'RA-RaBO01:RF-LLRF:TuneStep'],
                '306': ['Plunger 1 Move Dir', 'RA-RaBO01:RF-LLRF:PLG1Dir'],
                '305': ['Plunger 1 Move', 'RA-RaBO01:RF-LLRF:PLG1Move'],
                '315': ['Plunger 2 Move Dir', 'RA-RaBO01:RF-LLRF:PLG2Dir'],
                '314': ['Plunger 2 Move', 'RA-RaBO01:RF-LLRF:PLG2Move'],
                '307': ['Tuning Reset', 'RA-RaBO01:RF-LLRF:PLGMove-Cmd'],
                '302 Man': ['Plunger 1 Manual Dn', 'BO-05D:RF-P5Cav:Plg1ManDown-Mon'],
                '303 Man': ['Plunger 1 Manual Up', 'BO-05D:RF-P5Cav:Plg1ManUp-Mon'],
                '315 Man': ['Plunger 2 Manual Dn', 'BO-05D:RF-P5Cav:Plg2ManDown-Mon'],
                '316 Man': ['Plunger 2 Manual Up', 'BO-05D:RF-P5Cav:Plg2ManUp-Mon'],
            },
            'Auto': {
                '301': ['Tuning Pos Enable', 'RA-RaBO01:RF-LLRF:TuneDir'],
                '309': ['Tuning Margin High', 'RA-RaBO01:RF-LLRF:TuneMarginHI'],
                '310': ['Tuning Margin Low', 'RA-RaBO01:RF-LLRF:TuneMarginLO'],
                '308': ['Tuning Forward Min', 'RA-RaBO01:RF-LLRF:TuneFwdMin'],
                '311': ['Tuning Delay', 'RA-RaBO01:RF-LLRF:TuneDly'],
                '312': ['Tuning Filter Enable', 'RA-RaBO01:RF-LLRF:TuneFilt'],
                '313': ['Tuning Trigger Enable', 'RA-RaBO01:RF-LLRF:TuneTrig'],
                '316': ['Tuning/FF On Top Ramp', 'RA-RaBO01:RF-LLRF:RmpTuneTop'],
            },
            'Drivers': {
                '5V': ['RA-RaBO01:RF-CavPlDrivers:VoltPos5V-Mon', 'RA-RaBO01:RF-CavPlDrivers:Current5V-Mon'],
                '48V': ['RA-RaBO01:RF-CavPlDrivers:VoltPos48V-Mon', 'RA-RaBO01:RF-CavPlDrivers:Current48V-Mon'],
                'Enable': 'RA-RaBO01:RF-CavPlDrivers:DrEnbl',
                '1': ['RA-RaBO01:RF-CavPlDrivers:Dr1Enbl-Sts', 'RA-RaBO01:RF-CavPlDrivers:Dr1Flt-Mon'],
                '2': ['RA-RaBO01:RF-CavPlDrivers:Dr2Enbl-Sts', 'RA-RaBO01:RF-CavPlDrivers:Dr2Flt-Mon']
            }
        },
        'AdvIntlk': {
            'Diagnostics': {
                'General': {
                    'Manual': ['Manual Interlock', 'RA-RaBO01:RF-LLRF:IntlkManual'],
                    'EndSw': ['End Switches', 'RA-RaBO01:RF-LLRF:EndSwLogicInv'],
                    'Delay': 'RA-RaBO01:RF-LLRF:IntlkDly',
                    'HW': 'RA-RaBO01:RF-LLRF:FDLHwTrig-Mon',
                    'Beam Inv': ['Logic Inv. LLRF Beam Trip', 'RA-RaBO01:RF-LLRF:OrbitIntlkLogicInv'],
                    'Vacuum Inv': ['Vacuum Logic Inversion', 'RA-RaBO01:RF-LLRF:VacLogicInv']
                },
                'Levels': {
                    'VCav': 'RA-RaBO01:RF-LLRF:LimCav',
                    'FwdCav': 'RA-RaBO01:RF-LLRF:LimFwdCav',
                    'RevCav': 'RA-RaBO01:RF-LLRF:LimRevCav',
                    'FwdSSA1': 'RA-RaBO01:RF-LLRF:LimFwdSSA1',
                    'RevSSA1': 'RA-RaBO01:RF-LLRF:LimRevSSA1',
                    'RevSSA2': 'RA-RaBO01:RF-LLRF:LimRevSSA2',
                    'RevSSA3': 'RA-RaBO01:RF-LLRF:LimRevSSA3',
                    'RevSSA4': 'RA-RaBO01:RF-LLRF:LimRevSSA4',
                    'VCell2 (RF In 7)': 'RA-RaBO01:RF-LLRF:LimRFIn7',
                    'VCell4 (RF In 8)': 'RA-RaBO01:RF-LLRF:LimRFIn8',
                    'VCell1 (RF In 9)': 'RA-RaBO01:RF-LLRF:LimRFIn9',
                    'VCell5 (RF In 10)': 'RA-RaBO01:RF-LLRF:LimRFIn10',
                    'PreDriveIn (RF In 11)': 'RA-RaBO01:RF-LLRF:LimRFIn11',
                    'FwdPreDrive (RF In 12)': 'RA-RaBO01:RF-LLRF:LimRFIn12',
                    'RevPreDrive(RF In 13)': 'RA-RaBO01:RF-LLRF:LimRFIn13',
                    'FwdCirc (RF In 14)': 'RA-RaBO01:RF-LLRF:LimRFIn14',
                    'RevCirc (RF In 15)': 'RA-RaBO01:RF-LLRF:LimRFIn15'
                },
                'GPIO': {
                    'Inp': 'RA-RaBO01:RF-LLRF:GPIOInp-Mon',
                    'Intlk': 'RA-RaBO01:RF-LLRF:GPIOIntlk-Mon',
                    'Out': 'RA-RaBO01:RF-LLRF:GPIOOut-Mon'
                }
            },
            'Bypass': {
                '806': ['Rev SSA 1', 'RA-RaBO01:RF-LLRF:FIMRevSSA1'],
                '807': ['Rev SSA 2', 'RA-RaBO01:RF-LLRF:FIMRevSSA2'],
                '808': ['Rev SSA 3', 'RA-RaBO01:RF-LLRF:FIMRevSSA3'],
                '809': ['Rev SSA 4', 'RA-RaBO01:RF-LLRF:FIMRevSSA4'],
                '810': ['Rev Cavity', 'RA-RaBO01:RF-LLRF:FIMRevCav'],
                '811': ['Manual Interlock', 'RA-RaBO01:RF-LLRF:FIMManual'],
                '812': ['PLC', 'RA-RaBO01:RF-LLRF:FIMPLC'],
                '813': ['Ext LLRF 1', 'RA-RaBO01:RF-LLRF:FIMLLRF1'],
                '814': ['Ext LLRF 2', 'RA-RaBO01:RF-LLRF:FIMLLRF2'],
                '815': ['Ext LLRF 3', 'RA-RaBO01:RF-LLRF:FIMLLRF3'],
                '816 1': ['End Switch Up 1', 'RA-RaBO01:RF-LLRF:FIMPLG1Up'],
                '817 1': ['End Switch Down 1', 'RA-RaBO01:RF-LLRF:FIMPLG1Down'],
                '816 2': ['End Switch Up 2', 'RA-RaBO01:RF-LLRF:FIMPLG2Up'],
                '817 2': ['End Switch Down 2', 'RA-RaBO01:RF-LLRF:FIMPLG2Down'],
                '835': ['ILK VCav', 'RA-RaBO01:RF-LLRF:FIMCav'],
                '836': ['ILK Fwd Cav', 'RA-RaBO01:RF-LLRF:FIMFwdCav'],
                '837': ['ILK Fw SSA 1', 'RA-RaBO01:RF-LLRF:FIMFwdSSA1'],
                '838': ['ILK RF In 7', 'RA-RaBO01:RF-LLRF:FIMRFIn7'],
                '839': ['ILK RF In 8', 'RA-RaBO01:RF-LLRF:FIMRFIn8'],
                '840': ['ILK RF In 9', 'RA-RaBO01:RF-LLRF:FIMRFIn9'],
                '841': ['ILK RF In 10', 'RA-RaBO01:RF-LLRF:FIMRFIn10'],
                '842': ['ILK RF In 11', 'RA-RaBO01:RF-LLRF:FIMRFIn11'],
                '843': ['ILK RF In 12', 'RA-RaBO01:RF-LLRF:FIMRFIn12'],
                '844': ['ILK RF In 13', 'RA-RaBO01:RF-LLRF:FIMRFIn13'],
                '845': ['ILK RF In 14', 'RA-RaBO01:RF-LLRF:FIMRFIn14'],
                '846': ['ILK RF In 15', 'RA-RaBO01:RF-LLRF:FIMRFIn15'],
                '847': ['ILK LLRF Beam Trip', 'RA-RaBO01:RF-LLRF:FIMOrbitIntlk']
            }
        },
        'CalSys': {
            'Ch1': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm1-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB1-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm1-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm1-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW1-Mon'
                },
                'Color': 'blue'
            },
            'Ch2': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm2-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB2-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm2-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm2-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW2-Mon'
                },
                'Color': 'red'
            },
            'Ch3': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm3-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB3-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm3-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm3-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW3-Mon'
                },
                'Color': 'magenta'
            },
            'Ch4': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm4-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB4-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm4-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm4-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW4-Mon'
                },
                'Color': 'darkGreen'
            },
            'Ch5': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm5-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB5-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm5-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm5-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW5-Mon'
                },
                'Color': 'darkRed'
            },
            'Ch6': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm6-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB6-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm6-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm6-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW6-Mon'
                },
                'Color': 'black'
            },
            'Ch7': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm7-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB7-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm7-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm7-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW7-Mon'
                },
                'Color': 'darkBlue'
            },
            'Ch8': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm8-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB8-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm8-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm8-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW8-Mon'
                },
                'Color': 'darkOrange'
            },
            'Ch9': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm9-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB9-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm9-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm9-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW9-Mon'
                },
                'Color': 'orangered'
            },
            'Ch10': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm10-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB10-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm10-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm10-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW10-Mon'
                },
                'Color': 'darkOliveGreen'
            },
            'Ch11': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm11-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB11-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm11-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm11-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW11-Mon'
                },
                'Color': 'darkMagenta'
            },
            'Ch12': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm12-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB12-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm12-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm12-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW12-Mon'
                },
                'Color': 'chocolate'
            },
            'Ch13': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm13-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB13-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm13-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm13-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW13-Mon'
                },
                'Color': 'fireBrick'
            },
            'Ch14': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm14-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB14-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm14-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm14-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW14-Mon'
                },
                'Color': 'darkCyan'
            },
            'Ch15': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm15-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB15-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm15-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm15-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW15-Mon'
                },
                'Color': 'saddlebrown'
            },
            'Ch16': {
                'Label': 'RA-RaBO01:RF-RFCalSys:PwrdBm16-Mon.DESC',
                'Ofs': 'RA-RaBO01:RF-RFCalSys:OFSdB16-Mon',
                'UnCal': 'RA-RaBO01:RF-RFCalSys:PwrdBm16-Calc',
                'Cal': {
                    'dBm': 'RA-RaBO01:RF-RFCalSys:PwrdBm16-Mon',
                    'W': 'RA-RaBO01:RF-RFCalSys:PwrW16-Mon'
                },
                'Color': 'darkSlateGrey'
            }
        },
        'Equations': {
            'Cav': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:CavSysCal',
                'U-Raw': 'RA-RaBO01:RF-LLRF:CavSysCalInv',
                'OFS': 'RA-RaBO01:RF-LLRF:CavOffset'
            },
            'Fwd Cav': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:FwdCavSysCal',
                'U-Raw': 'RA-RaBO01:RF-LLRF:FwdCavSysCalInv',
                'OFS': 'RA-RaBO01:RF-LLRF:FwdCavOffset'
            },
            'Rev Cav': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:RevCavSysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:RevCavOffset'
            },
            'Fwd SSA 1': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:FwdSSA1SysCal',
                'U-Raw': 'RA-RaBO01:RF-LLRF:FwdSSA1SysCalInv',
                'OFS': 'RA-RaBO01:RF-LLRF:FwdSSA1Offset'
            },
            'Rev SSA 1': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:RevSSA1SysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:RevSSA1Offset'
            },
            'In Pre': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:InPre1AmpSysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:InPre1AmpOffset'
            },
            'Fwd Pre': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:FwdPre1SysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:FwdPre1Offset'
            },
            'Rev Pre': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:RevPreAmpSysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:RevPreAmpOffset'
            },
            'Fwd Circ': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:FwdCircSysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:FwdCircOffset'
            },
            'Rev Circ': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:RevCircSysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:RevCircOffset'
            },
            'MO': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:MOSysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:MOOffset'
            },
            'Cell 1': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:Cell1SysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:Cell1Offset'
            },
            'Cell 2': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:Cell2SysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:Cell2Offset'
            },
            'Cell 4': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:Cell4SysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:Cell4Offset'
            },
            'Cell 5': {
                'Raw-U': 'RA-RaBO01:RF-LLRF:Cell5SysCal',
                'OFS': 'RA-RaBO01:RF-LLRF:Cell5Offset'
            },
            'VGap': {
                'Hw to Amp': 'RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff',
                'Amp to Hw': 'RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff'
            },
            'Rsh': 'BO-05D:RF-P5Cav:Rsh-Cte'
        },
    },
    'SI': {
        'Emergency': 'RA-RaSIA02:RF-IntlkCtrl:EStop-Mon',
        'Sirius Intlk': 'RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon',
        'LLRF Intlk': {
            'A': 'RA-RaSIA01:RF-LLRF:Intlk-Mon',
            'B': 'RA-RaSIB01:RF-LLRF:Intlk-Mon',
        },
        'LLRF Intlk Details': {
            'A': {
                'Inputs': {
                    'Input 1': {
                        'Status': {
                            '0': 'RA-RaSIA01:RF-LLRF:Inp1Intlk0-Mon',
                            '1': 'RA-RaSIA01:RF-LLRF:Inp1Intlk1-Mon',
                            '2': 'RA-RaSIA01:RF-LLRF:Inp1Intlk2-Mon',
                            '3': 'RA-RaSIA01:RF-LLRF:Inp1Intlk3-Mon',
                            '4': 'RA-RaSIA01:RF-LLRF:Inp1Intlk4-Mon',
                            '5': 'RA-RaSIA01:RF-LLRF:Inp1Intlk5-Mon',
                            '6': 'RA-RaSIA01:RF-LLRF:Inp1Intlk6-Mon',
                            '7': 'RA-RaSIA01:RF-LLRF:Inp1Intlk7-Mon',
                            'Mon': 'RA-RaSIA01:RF-LLRF:Inp1Intlk-Mon',
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
                    'Input 2': {
                        'Status': {
                            '0': 'RA-RaSIA01:RF-LLRF:Inp2Intlk0-Mon',
                            '1': 'RA-RaSIA01:RF-LLRF:Inp2Intlk1-Mon',
                            '2': 'RA-RaSIA01:RF-LLRF:Inp2Intlk2-Mon',
                            '3': 'RA-RaSIA01:RF-LLRF:Inp2Intlk3-Mon',
                            '4': 'RA-RaSIA01:RF-LLRF:Inp2Intlk4-Mon',
                            '5': 'RA-RaSIA01:RF-LLRF:Inp2Intlk5-Mon',
                            '6': 'RA-RaSIA01:RF-LLRF:Inp2Intlk6-Mon',
                            '7': 'RA-RaSIA01:RF-LLRF:Inp2Intlk7-Mon',
                            'Mon': 'RA-RaSIA01:RF-LLRF:Inp2Intlk-Mon',
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
                            'Quench Condition 1'
                        ),
                    },
                },
                'Timestamps': {
                    '1': 'RA-RaSIA01:RF-LLRF:IntlkTs1-Mon',
                    '2': 'RA-RaSIA01:RF-LLRF:IntlkTs2-Mon',
                    '3': 'RA-RaSIA01:RF-LLRF:IntlkTs3-Mon',
                    '4': 'RA-RaSIA01:RF-LLRF:IntlkTs4-Mon',
                    '5': 'RA-RaSIA01:RF-LLRF:IntlkTs5-Mon',
                    '6': 'RA-RaSIA01:RF-LLRF:IntlkTs6-Mon',
                    '7': 'RA-RaSIA01:RF-LLRF:IntlkTs7-Mon',
                },
                'Quench1': {
                    'Rv': 'RA-RaSIA01:RF-LLRF:QuenchCond1RvRatio',
                    'Dly': 'RA-RaSIA01:RF-LLRF:QuenchCond1Dly'
                }
            },
            'B': {
                'Inputs': {
                    'Input': {
                        'Status': {
                            '0': 'RA-RaSIB01:RF-LLRF:Inp1Intlk0-Mon',
                            '1': 'RA-RaSIB01:RF-LLRF:Inp1Intlk1-Mon',
                            '2': 'RA-RaSIB01:RF-LLRF:Inp1Intlk2-Mon',
                            '3': 'RA-RaSIB01:RF-LLRF:Inp1Intlk3-Mon',
                            '4': 'RA-RaSIB01:RF-LLRF:Inp1Intlk4-Mon',
                            '5': 'RA-RaSIB01:RF-LLRF:Inp1Intlk5-Mon',
                            '6': 'RA-RaSIB01:RF-LLRF:Inp1Intlk6-Mon',
                            '7': 'RA-RaSIB01:RF-LLRF:Inp1Intlk7-Mon',
                            'Mon': 'RA-RaSIB01:RF-LLRF:Inp1Intlk-Mon',
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
                    'Input 2': {
                        'Status': {
                            '0': 'RA-RaSIB01:RF-LLRF:Inp2Intlk0-Mon',
                            '1': 'RA-RaSIB01:RF-LLRF:Inp2Intlk1-Mon',
                            '2': 'RA-RaSIB01:RF-LLRF:Inp2Intlk2-Mon',
                            '3': 'RA-RaSIB01:RF-LLRF:Inp2Intlk3-Mon',
                            '4': 'RA-RaSIB01:RF-LLRF:Inp2Intlk4-Mon',
                            '5': 'RA-RaSIB01:RF-LLRF:Inp2Intlk5-Mon',
                            '6': 'RA-RaSIB01:RF-LLRF:Inp2Intlk6-Mon',
                            '7': 'RA-RaSIB01:RF-LLRF:Inp2Intlk7-Mon',
                            'Mon': 'RA-RaSIB01:RF-LLRF:Inp2Intlk-Mon',
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
                            'Quench Condition 1'
                        ),
                    },
                },
                'Timestamps': {
                    '1': 'RA-RaSIB01:RF-LLRF:IntlkTs1-Mon',
                    '2': 'RA-RaSIB01:RF-LLRF:IntlkTs2-Mon',
                    '3': 'RA-RaSIB01:RF-LLRF:IntlkTs3-Mon',
                    '4': 'RA-RaSIB01:RF-LLRF:IntlkTs4-Mon',
                    '5': 'RA-RaSIB01:RF-LLRF:IntlkTs5-Mon',
                    '6': 'RA-RaSIB01:RF-LLRF:IntlkTs6-Mon',
                    '7': 'RA-RaSIB01:RF-LLRF:IntlkTs7-Mon',
                },
                'Quench1': {
                    'Rv': 'RA-RaSIB01:RF-LLRF:QuenchCond1RvRatio',
                    'Dly': 'RA-RaSIB01:RF-LLRF:QuenchCond1Dly'
                }
            }
        },
        'Reset': {
            'Global': 'RA-RaSIA02:RF-Intlk:Reset-Cmd',
            'A': 'RA-RaSIA01:RF-LLRF:IntlkReset-Cmd',
            'B': 'RA-RaSIB01:RF-LLRF:IntlkReset-Cmd',
        },
        'Cav Sts': {
            'Geral': 'SI-03SP:RF-P7Cav:Sts-Mon',
            'Temp': {
                'Cells': (
                    ('SI-03SP:RF-P7Cav:Cylin1T-Mon', 'blue'),
                    ('SI-03SP:RF-P7Cav:Cylin2T-Mon', 'red'),
                    ('SI-03SP:RF-P7Cav:Cylin3T-Mon', 'yellow'),
                    ('SI-03SP:RF-P7Cav:Cylin4T-Mon', 'darkGreen'),
                    ('SI-03SP:RF-P7Cav:Cylin5T-Mon', 'magenta'),
                    ('SI-03SP:RF-P7Cav:Cylin6T-Mon', 'darkCyan'),
                    ('SI-03SP:RF-P7Cav:Cylin7T-Mon', 'darkRed'),
                ),
                'Cells Limits PVs': ('SI-03SP:RF-P7Cav:Cylin1TLowerLimit-Cte',
                                     'SI-03SP:RF-P7Cav:Cylin1TUpperLimit-Cte'),
                'Cells Limits': [0.0, 0.0],
                'Coupler': ('SI-03SP:RF-P7Cav:CoupT-Mon', 'black'),
                'Coupler Limits PVs': ('SI-03SP:RF-P7Cav:CoupTLowerLimit-Cte',
                                       'SI-03SP:RF-P7Cav:CoupTUpperLimit-Cte'),
                'Coupler Limits': [0.0, 0.0],
                'Discs': (
                    'SI-03SP:RF-P7Cav:Disc1Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc2Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc3Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc4Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc5Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc6Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc7Tms-Mon',
                    'SI-03SP:RF-P7Cav:Disc8Tms-Mon',
                ),
            },
            'FlwRt': {
                'Flow Switch 1': 'SI-03SP:RF-P7Cav:HDFlwRt1-Mon',
                'Flow Switch 2': 'SI-03SP:RF-P7Cav:HDFlwRt2-Mon',
                'Flow Switch 3': 'SI-03SP:RF-P7Cav:HDFlwRt3-Mon',
            },
            'Vac': {
                'Cells': 'SI-03SP:VA-CCG-CAV:Pressure-Mon',
                'Cond': 'RA-RaSIA01:RF-LLRF:VacuumFastRly-Mon',
                'Cells ok': 'SI-03SP:RF-P7Cav:Pressure-Mon',
                'Coupler ok': 'SI-03SP:RF-P7Cav:CoupPressure-Mon',
            }
        },
        'TL Sts': {
            'A': {
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
                    'Circulator In Reflected Power': 'RA-TLSIA:RF-Circulator:RevIndBm-Mon',
                    'Combiner': 'RA-TLSIA:RF-Combiner:T-Mon'
                },
                'led': {
                    'Circulator Arc Detector': 'RA-TLSIA:RF-Circulator:Arc-Mon',
                    'Circulator Arc Detector Supply Fail': 'RA-RaSIA02:RF-ArcDetec-Circ:Fail-Mon',
                    'Arc Detector Load': 'RA-TLSIA:RF-Load:Arc-Mon',
                    'Arc Detector Load Supply Fail': 'RA-RaSIA02:RF-ArcDetec-Load:Fail-Mon',
                    'Circulator Flow': 'RA-TLSIA:RF-Circulator:FlwRt-Mon',
                    'Load Flow': 'RA-TLSIA:RF-Load:FlwRt-Mon',
                    'TCU Status': 'RA-TLSIA:RF-Circulator:IntlkOp-Mon',
                },
                'Circ Limits': (19.0, 23.0),
            },
            'B': {
                'Geral': 'RA-TLSIB:RF-TrLine:Sts-Mon',
                'Circulator Temp. In': {
                    'label': 'RA-TLSIB:RF-Circulator:Tin-Mon',
                    'led': {
                        'RA-TLSIB:RF-Circulator:TinDown-Mon': 0,
                        'RA-TLSIB:RF-Circulator:TinUp-Mon': 0
                    }
                },
                'label_led': {
                    'Circulator Temp. Drift': {
                        'label': 'RA-TLSIB:RF-Circulator:dT-Mon',
                        'led': 'RA-TLSIB:RF-Circulator:TDrift-Mon'
                    },
                    'Circulator Coil': {
                        'label': 'RA-TLSIB:RF-Circulator:Current-Mon',
                        'led': 'RA-TLSIB:RF-Circulator:Sts-Mon'
                    },
                    'Room Temp.': {
                        'label': 'RA-TLSIB:RF-Circulator:Tamb-Mon',
                        'led': 'RA-TLSIB:RF-Circulator:TEnv-Mon'
                    }
                },
                'label': {
                    'Circulator Temp. Out': 'RA-TLSIB:RF-Circulator:Tout-Mon',
                    'Circulator In Reflected Power': 'RA-TLSIB:RF-Circulator:RevIndBm-Mon',
                    'Combiner': 'RA-TLSIB:RF-Combiner:T-Mon'
                },
                'led': {
                    'Circulator Arc Detector': 'RA-TLSIB:RF-Circulator:Arc-Mon',
                    'Circulator Arc Detector Supply Fail': 'RA-RaSIB02:RF-ArcDetec-Circ:Fail-Mon',
                    'Arc Detector Load': 'RA-TLSIB:RF-Load:Arc-Mon',
                    'Arc Detector Load Supply Fail': 'RA-RaSIB02:RF-ArcDetec-Load:Fail-Mon',
                    'Circulator Flow': 'RA-TLSIB:RF-Circulator:FlwRt-Mon',
                    'Load Flow': 'RA-TLSIB:RF-Load:FlwRt-Mon',
                    'TCU Status': 'RA-TLSIB:RF-Circulator:IntlkOp-Mon',
                },
                'Circ Limits': (19.0, 23.0),
            }
        },
        'SSA': {
            '1': {
                'Name': 'SSA 01',
                'Status': 'RA-ToSIA01:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIA01:RF-SSAmpTower:FwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIA01:RF-ACPanel:ACEnbl-Cmd',
                    'Disable': 'RA-ToSIA01:RF-ACPanel:ACDsbl-Cmd',
                    'Mon': 'RA-ToSIA01:RF-ACPanel:AC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIA01:RF-TDKSource:DCEnbl-Cmd',
                    'Disable': 'RA-ToSIA01:RF-TDKSource:DCDsbl-Cmd',
                    'Mon': 'RA-ToSIA01:RF-TDKSource:DC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIA01:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIA01:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIA01:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:FwdIn1Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'A'
            },
            '2': {
                'Name': 'SSA 02',
                'Status': 'RA-ToSIA02:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIA02:RF-SSAmpTower:FwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIA02:RF-ACPanel:ACEnbl-Cmd',
                    'Disable': 'RA-ToSIA02:RF-ACPanel:ACDsbl-Cmd',
                    'Mon': 'RA-ToSIA02:RF-ACPanel:AC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIA02:RF-TDKSource:DCEnbl-Cmd',
                    'Disable': 'RA-ToSIA02:RF-TDKSource:DCDsbl-Cmd',
                    'Mon': 'RA-ToSIA02:RF-TDKSource:DC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIA02:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIA02:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIA02:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:FwdIn2Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'A'
            },
            '3': {
                'Name': 'SSA 03',
                'Status': 'RA-ToSIB03:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIB03:RF-SSAmpTower:FwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIB03:RF-ACPanel:ACEnbl-Cmd',
                    'Disable': 'RA-ToSIB03:RF-ACPanel:ACDsbl-Cmd',
                    'Mon': 'RA-ToSIB03:RF-ACPanel:AC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIB03:RF-TDKSource:DCEnbl-Cmd',
                    'Disable': 'RA-ToSIB03:RF-TDKSource:DCDsbl-Cmd',
                    'Mon': 'RA-ToSIB03:RF-TDKSource:DC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIB03:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIB03:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIB03:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:FwdIn3Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'B'
            },
            '4': {
                'Name': 'SSA 04',
                'Status': 'RA-ToSIB04:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIB04:RF-SSAmpTower:FwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIB04:RF-ACPanel:ACEnbl-Cmd',
                    'Disable': 'RA-ToSIB04:RF-ACPanel:ACDsbl-Cmd',
                    'Mon': 'RA-ToSIB04:RF-ACPanel:AC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIB04:RF-TDKSource:DCEnbl-Cmd',
                    'Disable': 'RA-ToSIB04:RF-TDKSource:DCDsbl-Cmd',
                    'Mon': 'RA-ToSIB04:RF-TDKSource:DC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIB04:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIB04:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIB04:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:FwdIn4Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'B'
            }
        },
        'SSADtls': {
            'A': {
                'Rack': {
                    'Temp': 'RA-ToSIA0$(NB):RF-HeatSink-H0$(suffix):T-Mon',
                    'Tms': 'RA-ToSIA0$(NB):RF-HeatSink-H0$(suffix):Tms-Mon',
                    'PT-100': [
                        'RA-ToSIA0$(NB):RF-HeatSink-H0$(suffix):TUp-Mon',
                        'RA-ToSIA0$(NB):RF-HeatSink-H0$(suffix):TDown-Mon'
                    ],
                    'Status': 'RA-ToSIA0$(NB):RF-TDKSource-R$(suffix):StsAC-Mon',
                    'Temp A': 'RA-ToSIA0$(NB):RF-SSAMux-$(suffix):TempA-Mon',
                    'Temp B': 'RA-ToSIA0$(NB):RF-SSAMux-$(suffix):TempB-Mon',
                    'Voltage': 'RA-ToSIA0$(NB):RF-SSAMux-$(suffix):VoltPos5V-Mon',
                    'Current': 'RA-ToSIA0$(NB):RF-SSAMux-$(suffix):CurrentPos5V-Mon'
                },
                'Runtime': 'RA-ToSIA0$(NB):RF-SSAmpTower:RunHour-Mon',
                'Pre Amp1': [
                    'RA-RoSIA01:RF-LLRFPreAmp-1:T1-Mon',
                    'RA-RoSIA01:RF-LLRFPreAmp-1:T1Up-Mon',
                ],
                'Pre Amp2': [
                    'RA-RoSIA01:RF-LLRFPreAmp-1:T2-Mon',
                    'RA-RoSIA01:RF-LLRFPreAmp-1:T2Up-Mon',
                ],
                'In Pwr Fwd': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:FwdIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwFwdIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:FwdInSts-Mon'
                ],
                'In Pwr Rev': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:RevIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwRevIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:RevInSts-Mon'
                ],
                'Out Pwr Fwd': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:FwdOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwFwdOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:FwdOutSts-Mon'
                ],
                'Out Pwr Rev': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:RevOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwRevOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:RevOutSts-Mon'
                ],
                'Alerts': {
                    'PhsFlt': ['Phase Fault', 'RA-ToSIA0$(NB):RF-ACPanel:PhsFlt-Mon'],
                    'SSAFlwRt': ['SSA Rotameter Flow', 'RA-ToSIA0$(NB):RF-SSAmpTower:HdFlwRt-Mon'],
                    'LoadFlwRt': ['Load Rotameter Flow', 'RA-ToSIA0$(NB):RF-WaterLoad:HdFlwRt-Mon'],
                    'PnlFeed': ['AC Panel Feedback', 'RA-ToSIA0$(NB):RF-ACPanel:Intlk-Mon'],
                    'PnlIntlk': ['AC Panel Interlock', 'RA-ToSIA0$(NB):RF-Intlk:IntlkACPanel-Mon'],
                    'PnlSts': ['AC Panel Status', 'RA-ToSIA0$(NB):RF-ACPanel:ACOp-Mon'],
                    'ElecFuse': ['Electronic Fuse', 'RA-ToSIA0$(NB):RF-CtrlPanel:Sts-Mon'],
                    'PwrSup': ['24V Power Supply', 'RA-ToSIA0$(NB):RF-ACPanel:StsPos24V-Mon'],
                    'PwrIntlk': ['RF Power Interlock', 'RA-ToSIA0$(NB):RF-SSAmpTower:RFSts-Mon'],
                }
            },
            'B': {
                'Rack': {
                    'Temp': 'RA-ToSIB0$(NB):RF-HeatSink-H0$(suffix):T-Mon',
                    'Tms': 'RA-ToSIB0$(NB):RF-HeatSink-H0$(suffix):Tms-Mon',
                    'PT-100': [
                        'RA-ToSIB0$(NB):RF-HeatSink-H0$(suffix):TUp-Mon',
                        'RA-ToSIB0$(NB):RF-HeatSink-H0$(suffix):TDown-Mon'
                    ],
                    'Status': 'RA-ToSIB0$(NB):RF-TDKSource-R$(suffix):StsAC-Mon',
                    'Temp A': 'RA-ToSIB0$(NB):RF-SSAMux-$(suffix):TempA-Mon',
                    'Temp B': 'RA-ToSIB0$(NB):RF-SSAMux-$(suffix):TempB-Mon',
                    'Voltage': 'RA-ToSIB0$(NB):RF-SSAMux-$(suffix):VoltPos5V-Mon',
                    'Current': 'RA-ToSIB0$(NB):RF-SSAMux-$(suffix):CurrentPos5V-Mon'
                },
                'Runtime': 'RA-ToSIB0$(NB):RF-SSAmpTower:RunHour-Mon',
                'Pre Amp3': [
                    'RA-RaSIB01:RF-LLRFPreAmp-1:T1-Mon',
                    'RA-RaSIB01:RF-LLRFPreAmp-1:T1Up-Mon',
                ],
                'Pre Amp4': [
                    'RA-RaSIB01:RF-LLRFPreAmp-1:T2-Mon',
                    'RA-RaSIB01:RF-LLRFPreAmp-1:T2Up-Mon',
                ],
                'In Pwr Fwd': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:FwdIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwFwdIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:FwdInSts-Mon'
                ],
                'In Pwr Rev': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:RevIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwRevIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:RevInSts-Mon'
                ],
                'Out Pwr Fwd': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:FwdOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwFwdOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:FwdOutSts-Mon'
                ],
                'Out Pwr Rev': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:RevOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwRevOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:RevOutSts-Mon'
                ],
                'Alerts': {
                    'PhsFlt': ['Phase Fault', 'RA-ToSIB0$(NB):RF-ACPanel:PhsFlt-Mon'],
                    'SSAFlwRt': ['SSA Rotameter Flow', 'RA-ToSIB0$(NB):RF-SSAmpTower:HdFlwRt-Mon'],
                    'LoadFlwRt': ['Load Rotameter Flow', 'RA-ToSIB0$(NB):RF-WaterLoad:HdFlwRt-Mon'],
                    'PnlFeed': ['AC Panel Feedback', 'RA-ToSIB0$(NB):RF-ACPanel:Intlk-Mon'],
                    'PnlIntlk': ['AC Panel Interlock', 'RA-ToSIB0$(NB):RF-Intlk:IntlkACPanel-Mon'],
                    'PnlSts': ['AC Panel Status', 'RA-ToSIB0$(NB):RF-ACPanel:ACOp-Mon'],
                    'ElecFuse': ['Electronic Fuse', 'RA-ToSIB0$(NB):RF-CtrlPanel:Sts-Mon'],
                    'PwrSup': ['24V Power Supply', 'RA-ToSIB0$(NB):RF-ACPanel:StsPos24V-Mon'],
                    'PwrIntlk': ['RF Power Interlock', 'RA-ToSIB0$(NB):RF-SSAmpTower:RFSts-Mon'],
                }
            }
        },
        'SSACurr': {
            'A': {
                'HeatSink': {
                    'Curr': 'RA-ToSIA0$(NB):RF-SSAmp-H0$(hs_num)$(letter)M0$(m_num):Current$(curr_num)-Mon',
                    'Fwd Top': 'RA-ToSIA0$(NB):RF-HeatSink-H0$(hs_num):PwrFwdTop-Mon',
                    'Rev Top': 'RA-ToSIA0$(NB):RF-HeatSink-H0$(hs_num):PwrRevTop-Mon',
                    'Fwd Bot': 'RA-ToSIA0$(NB):RF-HeatSink-H0$(hs_num):PwrFwdBot-Mon',
                    'Rev Bot': 'RA-ToSIA0$(NB):RF-HeatSink-H0$(hs_num):PwrRevBot-Mon'
                },
                'PreAmp': {
                    'HS': 'RA-ToSIA0$(NB):RF-SSAmp-H0$(hs_num)PreAmp:Current$(curr_num)-Mon',
                    'PreAmp': 'RA-ToSIA0$(NB):RF-SSAmp-H05PreAmp:Current$(curr_num)-Mon',
                },
                'Offsets': {
                    'FwdPwrTop': ['Forward Power - Top', 'RA-ToSIA0$(NB):OffsetConfig:UpperIncidentPower'],
                    'RevPwrTop': ['Reverse Power - Top', 'RA-ToSIA0$(NB):OffsetConfig:UpperReflectedPower'],
                    'FwdPwrBot': ['Forward Power - Bottom', 'RA-ToSIA0$(NB):OffsetConfig:LowerIncidentPower'],
                    'RevPwrBot': ['Reverse Power - Bottom', 'RA-ToSIA0$(NB):OffsetConfig:LowerReflectedPower'],
                },
                'RacksTotal': 'RA-ToSIA0$(NB):RF-SSAMux-$(rack_num):DCCurrent-Mon',
                'Alarms': {
                    'Inter': {
                        'Label': 'Intermediary Power',
                        'HIHI': 'RA-ToSIA0$(NB):AlarmConfig:InnerPowerLimHiHi',
                        'HIGH': 'RA-ToSIA0$(NB):AlarmConfig:InnerPowerLimHigh',
                        'LOW': 'RA-ToSIA0$(NB):AlarmConfig:InnerPowerLimLow',
                        'LOLO': 'RA-ToSIA0$(NB):AlarmConfig:InnerPowerLimLoLo',
                    },
                    'High': {
                        'Label': 'Current - High Limit',
                        'HIHI': 'RA-ToSIA0$(NB):AlarmConfig:CurrentLimHiHi',
                        'HIGH': 'RA-ToSIA0$(NB):AlarmConfig:CurrentLimHigh',
                        'LOW': 'RA-ToSIA0$(NB):AlarmConfig:CurrentLimLow',
                        'LOLO': 'RA-ToSIA0$(NB):AlarmConfig:CurrentLimLoLo',
                    },
                }
            },
            'B': {
                'HeatSink': {
                    'Curr': 'RA-ToSIB0$(NB):RF-SSAmp-H0$(hs_num)$(letter)M0$(m_num):Current$(curr_num)-Mon',
                    'Fwd Top': 'RA-ToSIB0$(NB):RF-HeatSink-H0$(hs_num):PwrFwdTop-Mon',
                    'Rev Top': 'RA-ToSIB0$(NB):RF-HeatSink-H0$(hs_num):PwrRevTop-Mon',
                    'Fwd Bot': 'RA-ToSIB0$(NB):RF-HeatSink-H0$(hs_num):PwrFwdBot-Mon',
                    'Rev Bot': 'RA-ToSIB0$(NB):RF-HeatSink-H0$(hs_num):PwrRevBot-Mon'
                },
                'PreAmp': {
                    'HS': 'RA-ToSIB0$(NB):RF-SSAmp-H0$(hs_num)PreAmp:Current$(curr_num)-Mon',
                    'PreAmp': 'RA-ToSIB0$(NB):RF-SSAmp-H05PreAmp:Current$(curr_num)-Mon',
                },
                'Offsets': {
                    'FwdPwrTop': ['Forward Power - Top', 'RA-ToSIB0$(NB):OffsetConfig:UpperIncidentPower'],
                    'RevPwrTop': ['Reverse Power - Top', 'RA-ToSIB0$(NB):OffsetConfig:UpperReflectedPower'],
                    'FwdPwrBot': ['Forward Power - Bottom', 'RA-ToSIB0$(NB):OffsetConfig:LowerIncidentPower'],
                    'RevPwrBot': ['Reverse Power - Bottom', 'RA-ToSIB0$(NB):OffsetConfig:LowerReflectedPower'],
                },
                'RacksTotal': 'RA-ToSIB0$(NB):RF-SSAMux-$(rack_num):DCCurrent-Mon',
                'Alarms': {
                    'Inter': {
                        'Label': 'Intermediary Power',
                        'HIHI': 'RA-ToSIB0$(NB):AlarmConfig:InnerPowerLimHiHi',
                        'HIGH': 'RA-ToSIB0$(NB):AlarmConfig:InnerPowerLimHigh',
                        'LOW': 'RA-ToSIB0$(NB):AlarmConfig:InnerPowerLimLow',
                        'LOLO': 'RA-ToSIB0$(NB):AlarmConfig:InnerPowerLimLoLo',
                    },
                    'High': {
                        'Label': 'Current - High Limit',
                        'HIHI': 'RA-ToSIB0$(NB):AlarmConfig:CurrentLimHiHi',
                        'HIGH': 'RA-ToSIB0$(NB):AlarmConfig:CurrentLimHigh',
                        'LOW': 'RA-ToSIB0$(NB):AlarmConfig:CurrentLimLow',
                        'LOLO': 'RA-ToSIB0$(NB):AlarmConfig:CurrentLimLoLo',
                    },
                }
            }
        },
        'SL': {
            'ErrDtls': {
                'A': {
                    'IRef': 'RA-RaSIA01:RF-LLRF:SLRefI-Mon',
                    'QRef': 'RA-RaSIA01:RF-LLRF:SLRefQ-Mon',
                    'IInp': 'RA-RaSIA01:RF-LLRF:SLInpI-Mon',
                    'QInp': 'RA-RaSIA01:RF-LLRF:SLInpQ-Mon',
                    'IErr': 'RA-RaSIA01:RF-LLRF:SLErrorI-Mon',
                    'QErr': 'RA-RaSIA01:RF-LLRF:SLErrorQ-Mon',
                },
                'B': {
                    'IRef': 'RA-RaSIB01:RF-LLRF:SLRefI-Mon',
                    'QRef': 'RA-RaSIB01:RF-LLRF:SLRefQ-Mon',
                    'IInp': 'RA-RaSIB01:RF-LLRF:SLInpI-Mon',
                    'QInp': 'RA-RaSIB01:RF-LLRF:SLInpQ-Mon',
                    'IErr': 'RA-RaSIB01:RF-LLRF:SLErrorI-Mon',
                    'QErr': 'RA-RaSIB01:RF-LLRF:SLErrorQ-Mon',
                },
            },
            'Params': {
                'A': {
                    'Inp': 'RA-RaSIA01:RF-LLRF:SLInp',
                    'PIL': 'RA-RaSIA01:RF-LLRF:SLPILim',
                    'KI': 'RA-RaSIA01:RF-LLRF:SLKI',
                    'KP': 'RA-RaSIA01:RF-LLRF:SLKP',
                },
                'B': {
                    'Inp': 'RA-RaSIB01:RF-LLRF:SLInp',
                    'PIL': 'RA-RaSIB01:RF-LLRF:SLPILim',
                    'KI': 'RA-RaSIB01:RF-LLRF:SLKI',
                    'KP': 'RA-RaSIB01:RF-LLRF:SLKP',
                },
            },
            'Over': {
                'A': {
                    'Enbl': 'RA-RaSIA01:RF-LLRF:SL',
                    'Mode': 'RA-RaSIA01:RF-LLRF:LoopMode',
                    'ASet': 'RA-RaSIA01:RF-LLRF:ALRef',
                    'AInc': 'RA-RaSIA01:RF-LLRF:AmpIncRate',
                    'PSet': 'RA-RaSIA01:RF-LLRF:PLRef',
                    'PInc': 'RA-RaSIA01:RF-LLRF:PhsIncRate',
                    'ARef': 'RA-RaSIA01:RF-LLRF:SLRefAmp-Mon',
                    'PRef': 'RA-RaSIA01:RF-LLRF:SLRefPhs-Mon',
                    'AInp': 'RA-RaSIA01:RF-LLRF:SLInpAmp-Mon',
                    'PInp': 'RA-RaSIA01:RF-LLRF:SLInpPhs-Mon',
                    'AErr': 'RA-RaSIA01:RF-LLRF:SLErrorAmp-Mon',
                    'PErr': 'RA-RaSIA01:RF-LLRF:SLErrorPhs-Mon',
                },
                'B': {
                    'Enbl': 'RA-RaSIB01:RF-LLRF:SL',
                    'Mode': 'RA-RaSIB01:RF-LLRF:LoopMode',
                    'ASet': 'RA-RaSIB01:RF-LLRF:ALRef',
                    'AInc': 'RA-RaSIB01:RF-LLRF:AmpIncRate',
                    'PSet': 'RA-RaSIB01:RF-LLRF:PLRef',
                    'PInc': 'RA-RaSIB01:RF-LLRF:PhsIncRate',
                    'ARef': 'RA-RaSIB01:RF-LLRF:SLRefAmp-Mon',
                    'PRef': 'RA-RaSIB01:RF-LLRF:SLRefPhs-Mon',
                    'AInp': 'RA-RaSIB01:RF-LLRF:SLInpAmp-Mon',
                    'PInp': 'RA-RaSIB01:RF-LLRF:SLInpPhs-Mon',
                    'AErr': 'RA-RaSIB01:RF-LLRF:SLErrorAmp-Mon',
                    'PErr': 'RA-RaSIB01:RF-LLRF:SLErrorPhs-Mon',
                },
            },
            'ASet': {
                'A': 'RA-RaSIA01:RF-LLRF:ALRefVGap',
                'B': 'RA-RaSIB01:RF-LLRF:ALRefVGap',
            },
        },
        'Tun': {
            'A': {
                'Auto': 'RA-RaSIA01:RF-LLRF:Tune',
                'DTune': 'RA-RaSIA01:RF-LLRF:Detune',
                'DPhase': 'RA-RaSIA01:RF-LLRF:TuneDephs-Mon',
                'Acting': 'RA-RaSIA01:RF-LLRF:TuneOut-Mon',
                'Deadbnd': 'RA-RaSIA01:RF-LLRF:TuneMarginHI',
                'Oversht': 'RA-RaSIA01:RF-LLRF:TuneMarginLO',
                'Pl1Down': 'SI-03SP:RF-SRFCav-A:TunerMoveDown-Mon',
                'Pl1Up': 'SI-03SP:RF-SRFCav-A:TunerMoveUp-Mon',
                'PlM1Curr': 'RA-RaSIA01:RF-CavPlDrivers:Dr1Current-Mon',
                'color': 'blue'
            },
            'B': {
                'Auto': 'RA-RaSIB01:RF-LLRF:Tune',
                'DTune': 'RA-RaSIB01:RF-LLRF:Detune',
                'DPhase': 'RA-RaSIB01:RF-LLRF:TuneDephs-Mon',
                'Acting': 'RA-RaSIB01:RF-LLRF:TuneOut-Mon',
                'Deadbnd': 'RA-RaSIB01:RF-LLRF:TuneMarginHI',
                'Oversht': 'RA-RaSIB01:RF-LLRF:TuneMarginLO',
                'Pl1Down': 'SI-03SP:RF-SRFCav-B:TunerMoveDown-Mon',
                'Pl1Up': 'SI-03SP:RF-SRFCav-B:TunerMoveUp-Mon',
                'PlM1Curr': 'RA-RaSIB01:RF-CavPlDrivers:Dr1Current-Mon',
                'color': 'red'
            }
        },
        'PwrMtr': {
            'A - Fwd SSA 1': {
                'mV': 'RA-ToSIA01:RF-SSAmpTower:FwdOutAmp-Mon',
                'dBm': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                'W': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPwrW-Mon',
                'color': 'blue'
            },
            'A - Rev SSA 1': {
                'mV': 'RA-ToSIA01:RF-SSAmpTower:RevOutAmp-Mon',
                'dBm': 'RA-ToSIA01:RF-SSAmpTower:RevOutPwrdBm-Mon',
                'W': 'RA-ToSIA01:RF-SSAmpTower:RevOutPwrW-Mon',
                'color': 'red'
            },
            'A - Fwd SSA 2': {
                'mV': 'RA-ToSIA02:RF-SSAmpTower:FwdOutAmp-Mon',
                'dBm': 'RA-ToSIA02:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                'W': 'RA-ToSIA02:RF-SSAmpTower:FwdOutPwrW-Mon',
                'color': 'magenta'
            },
            'A - Rev SSA 2': {
                'mV': 'RA-ToSIA02:RF-SSAmpTower:RevOutAmp-Mon',
                'dBm': 'RA-ToSIA02:RF-SSAmpTower:RevOutPwrdBm-Mon',
                'W': 'RA-ToSIA02:RF-SSAmpTower:RevOutPwrW-Mon',
                'color': 'darkGreen'
            },
            'A - Cav': {
                'mV': 'SI-03SP:RF-SRFCav-A:Amp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-A:PwrdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-A:PwrW-Mon',
                'color': 'darkRed'
            },
            'A - Fwd Cav': {
                'mV': 'SI-03SP:RF-SRFCav-A:FwdAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-A:FwdPwrdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-A:FwdPwrW-Mon',
                'color': 'black'
            },
            'A - Rev Cav': {
                'mV': 'SI-03SP:RF-SRFCav-A:RevAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-A:RevPwrdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-A:RevPwrW-Mon',
                'color': 'darkBlue'
            },
            'A - Fwd Circulator': {
                'mV': 'RA-TL:RF-Circulator-SIA:FwdOutAmp-Mon',
                'dBm': 'RA-TL:RF-Circulator-SIA:FwdOutPwrdBm-Mon',
                'W': 'RA-TL:RF-Circulator-SIA:FwdOutPwrW-Mon',
                'color': 'yellow'
            },
            'B - Fwd SSA 3': {
                'mV': 'RA-ToSIB03:RF-SSAmpTower:FwdOutAmp-Mon',
                'dBm': 'RA-ToSIB03:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                'W': 'RA-ToSIB03:RF-SSAmpTower:FwdOutPwrW-Mon',
                'color': 'orangered'
            },
            'B - Rev SSA 3': {
                'mV': 'RA-ToSIB03:RF-SSAmpTower:RevOutAmp-Mon',
                'dBm': 'RA-ToSIB03:RF-SSAmpTower:RevOutPwrdBm-Mon',
                'W': 'RA-ToSIB03:RF-SSAmpTower:RevOutPwrW-Mon',
                'color': 'darkOliveGreen'
            },
            'B - Fwd SSA 4': {
                'mV': 'RA-ToSIB04:RF-SSAmpTower:FwdOutAmp-Mon',
                'dBm': 'RA-ToSIB04:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                'W': 'RA-ToSIB04:RF-SSAmpTower:FwdOutPwrW-Mon',
                'color': 'darkMagenta'
            },
            'B - Rev SSA 4': {
                'mV': 'RA-ToSIB04:RF-SSAmpTower:RevOutAmp-Mon',
                'dBm': 'RA-ToSIB04:RF-SSAmpTower:RevOutPwrdBm-Mon',
                'W': 'RA-ToSIB04:RF-SSAmpTower:RevOutPwrW-Mon',
                'color': 'chocolate'
            },
            'B - Cav': {
                'mV': 'SI-03SP:RF-SRFCav-B:Amp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-B:PwrdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-B:PwrW-Mon',
                'color': 'cyan'
            },
            'B - Fwd Cav': {
                'mV': 'SI-03SP:RF-SRFCav-B:FwdAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-B:FwdPwrdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-B:FwdPwrW-Mon',
                'color': 'darkCyan'
            },
            'B - Rev Cav': {
                'mV': 'SI-03SP:RF-SRFCav-B:RevAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-B:RevPwrdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-B:RevPwrW-Mon',
                'color': 'saddlebrown'
            },
            'B - Fwd Circulator': {
                'mV': 'RA-TL:RF-Circulator-SIB:FwdOutAmp-Mon',
                'dBm': 'RA-TL:RF-Circulator-SIB:FwdOutPwrdBm-Mon',
                'W': 'RA-TL:RF-Circulator-SIB:FwdOutPwrW-Mon',
                'color': 'darkSlateGrey'
            },
        },
        'CavVGap': {
            'A': 'SI-03SP:RF-SRFCav-A:VGap-Mon',
            'B': 'SI-03SP:RF-SRFCav-B:VGap-Mon'
        },
        'TempMon': {
            'Temp.': {
                'Cells': {
                    'Cell 1': 'SI-03SP:RF-P7Cav:Cylin1T-Mon',
                    'Cell 2': 'SI-03SP:RF-P7Cav:Cylin2T-Mon',
                    'Cell 3': 'SI-03SP:RF-P7Cav:Cylin3T-Mon',
                    'Cell 4': 'SI-03SP:RF-P7Cav:Cylin4T-Mon',
                    'Cell 5': 'SI-03SP:RF-P7Cav:Cylin5T-Mon',
                    'Cell 6': 'SI-03SP:RF-P7Cav:Cylin6T-Mon',
                    'Cell 7': 'SI-03SP:RF-P7Cav:Cylin7T-Mon',
                },
            },
            'Water Temp.': {
                'Cells': {
                    'Cell 1': 'SI-03SP:RF-P7Cav:Cylin1WT-Mon',
                    'Cell 2': 'SI-03SP:RF-P7Cav:Cylin2WT-Mon',
                    'Cell 3': 'SI-03SP:RF-P7Cav:Cylin3WT-Mon',
                    'Cell 4': 'SI-03SP:RF-P7Cav:Cylin4WT-Mon',
                    'Cell 5': 'SI-03SP:RF-P7Cav:Cylin5WT-Mon',
                    'Cell 6': 'SI-03SP:RF-P7Cav:Cylin6WT-Mon',
                    'Cell 7': 'SI-03SP:RF-P7Cav:Cylin7WT-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-03SP:RF-P7Cav:Disc1WT-Mon',
                    'Disc 2': 'SI-03SP:RF-P7Cav:Disc2WT-Mon',
                    'Disc 3': 'SI-03SP:RF-P7Cav:Disc3WT-Mon',
                    'Disc 4': 'SI-03SP:RF-P7Cav:Disc4WT-Mon',
                    'Disc 5': 'SI-03SP:RF-P7Cav:Disc5WT-Mon',
                    'Disc 6': 'SI-03SP:RF-P7Cav:Disc6WT-Mon',
                    'Disc 7': 'SI-03SP:RF-P7Cav:Disc7WT-Mon',
                    'Disc 8': 'SI-03SP:RF-P7Cav:Disc8WT-Mon',
                },
                'Input + Plungers + Coupler': {
                    'Input': 'SI-03SP:RF-P7Cav:WInT-Mon',
                    'Plunger 1': 'SI-03SP:RF-P7Cav:Pl1WT-Mon',
                    'Plunger 2': 'SI-03SP:RF-P7Cav:Pl2WT-Mon',
                    'Coupler': 'SI-03SP:RF-P7Cav:CoupWT-Mon',
                },
            },
            'Water dTemp.': {
                'Cells': {
                    'Cell 1': 'SI-03SP:RF-P7Cav:Cylin1WdT-Mon',
                    'Cell 2': 'SI-03SP:RF-P7Cav:Cylin2WdT-Mon',
                    'Cell 3': 'SI-03SP:RF-P7Cav:Cylin3WdT-Mon',
                    'Cell 4': 'SI-03SP:RF-P7Cav:Cylin4WdT-Mon',
                    'Cell 5': 'SI-03SP:RF-P7Cav:Cylin5WdT-Mon',
                    'Cell 6': 'SI-03SP:RF-P7Cav:Cylin6WdT-Mon',
                    'Cell 7': 'SI-03SP:RF-P7Cav:Cylin7WdT-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-03SP:RF-P7Cav:Disc1WdT-Mon',
                    'Disc 2': 'SI-03SP:RF-P7Cav:Disc2WdT-Mon',
                    'Disc 3': 'SI-03SP:RF-P7Cav:Disc3WdT-Mon',
                    'Disc 4': 'SI-03SP:RF-P7Cav:Disc4WdT-Mon',
                    'Disc 5': 'SI-03SP:RF-P7Cav:Disc5WdT-Mon',
                    'Disc 6': 'SI-03SP:RF-P7Cav:Disc6WdT-Mon',
                    'Disc 7': 'SI-03SP:RF-P7Cav:Disc7WdT-Mon',
                    'Disc 8': 'SI-03SP:RF-P7Cav:Disc8WdT-Mon',
                },
            },
            'Dissip. Power (Water)': {
                'Cells': {
                    'Cell 1': 'SI-03SP:RF-P7Cav:DissCell1-Mon',
                    'Cell 2': 'SI-03SP:RF-P7Cav:DissCell2-Mon',
                    'Cell 3': 'SI-03SP:RF-P7Cav:DissCell3-Mon',
                    'Cell 4': 'SI-03SP:RF-P7Cav:DissCell4-Mon',
                    'Cell 5': 'SI-03SP:RF-P7Cav:DissCell5-Mon',
                    'Cell 6': 'SI-03SP:RF-P7Cav:DissCell6-Mon',
                    'Cell 7': 'SI-03SP:RF-P7Cav:DissCell7-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-03SP:RF-P7Cav:DissDisc1-Mon',
                    'Disc 2': 'SI-03SP:RF-P7Cav:DissDisc2-Mon',
                    'Disc 3': 'SI-03SP:RF-P7Cav:DissDisc3-Mon',
                    'Disc 4': 'SI-03SP:RF-P7Cav:DissDisc4-Mon',
                    'Disc 5': 'SI-03SP:RF-P7Cav:DissDisc5-Mon',
                    'Disc 6': 'SI-03SP:RF-P7Cav:DissDisc6-Mon',
                    'Disc 7': 'SI-03SP:RF-P7Cav:DissDisc7-Mon',
                    'Disc 8': 'SI-03SP:RF-P7Cav:DissDisc8-Mon',
                },
            },
            'Power (Water)': {
                'Cell 1': 'SI-03SP:RF-P7Cav:WtCell1-Mon',
                'Cell 2': 'SI-03SP:RF-P7Cav:WtCell2-Mon',
                'Cell 3': 'SI-03SP:RF-P7Cav:WtCell3-Mon',
                'Cell 4': 'SI-03SP:RF-P7Cav:WtCell4-Mon',
                'Cell 5': 'SI-03SP:RF-P7Cav:WtCell5-Mon',
                'Cell 6': 'SI-03SP:RF-P7Cav:WtCell6-Mon',
                'Cell 7': 'SI-03SP:RF-P7Cav:WtCell7-Mon',
                # 'Total': 'SI-03SP:RF-P7Cav:WtTotal-Mon',
                # 'Fwd': 'RA-RaSIA01:RF-RFCalSys:W2-Mon',
            },
        },
        'FDL': {
            'A': {
                'Signals': (
                    ('Cav', 'RA-RaSIA01:RF-LLRF:FDLCavAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLCavPhs-Mon', 'blue'),
                    ('Fwd Cav', 'RA-RaSIA01:RF-LLRF:FDLCavFwdAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLCavFwdPhs-Mon', 'red'),
                    ('Rev Cav', 'RA-RaSIA01:RF-LLRF:FDLCavRevAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLCavRevPhs-Mon', 'darkSlateBlue'),
                    ('Fwd Ssa', 'RA-RaSIA01:RF-LLRF:FDLFwdSSAAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLFwdSSAPhs-Mon', 'darkGreen'),
                    ('Rev Ssa', 'RA-RaSIA01:RF-LLRF:FDLRevSSAAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLRevSSAPhs-Mon', 'magenta'),
                    ('Ctrl', 'RA-RaSIA01:RF-LLRF:FDLCtrlAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLCtrlPhs-Mon', 'darkCyan'),
                    ('Ref', 'RA-RaSIA01:RF-LLRF:FDLSLRefAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLSLRefPhs-Mon', 'darkRed'),
                    ('Err', 'RA-RaSIA01:RF-LLRF:FDLSLErrAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLSLErrPhs-Mon', 'purple'),
                    ('Err Acc', 'RA-RaSIA01:RF-LLRF:FDLSLErrAccAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLSLErrAccPhs-Mon', 'saddlebrown'),
                    ('MO', 'RA-RaSIA01:RF-LLRF:FDLMOAmp-Mon', 'RA-RaSIA01:RF-LLRF:FDLMOPhs-Mon', 'darkBlue'),
                    ('Tune', None, 'RA-RaSIA01:RF-LLRF:FDLTuneDephs-Mon', 'orangered'),
                    ('Tune Filt', None, 'RA-RaSIA01:RF-LLRF:FDLTuneDephsFilt-Mon', 'darkOliveGreen')
                ),
                'Time': 'RA-RaSIA01:RF-LLRF:FDLScale32-Mon',
                'Mode': 'RA-RaSIA01:RF-LLRF:FDLMode-Mon',
                'SW Trig': 'RA-RaSIA01:RF-LLRF:FDLSwTrig-Mon',
                'HW Trig': 'RA-RaSIA01:RF-LLRF:FDLHwTrig-Mon',
                'Trig': 'RA-RaSIA01:RF-LLRF:FDLTrig-Cmd',
                'Processing': 'RA-RaSIA01:RF-LLRF:FDLProcessing-Mon',
                'Rearm': 'RA-RaSIA01:RF-LLRF:FDLRearm-Sel',
                'Raw': 'RA-RaSIA01:RF-LLRF:FDLRaw',
                'Qty': 'RA-RaSIA01:RF-LLRF:FDLFrame',
                'Size': 'RA-RaSIA01:RF-LLRF:FDLSize-Mon',
                'Duration': 'RA-RaSIA01:RF-LLRF:FDLDuration-Mon',
                'Delay': 'RA-RaSIA01:RF-LLRF:FDLTrigDly',
                'Name': 'A',
            },
            'B': {
                'Signals': (
                    ('Cav', 'RA-RaSIB01:RF-LLRF:FDLCavAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLCavPhs-Mon', 'blue'),
                    ('Fwd Cav', 'RA-RaSIB01:RF-LLRF:FDLCavFwdAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLCavFwdPhs-Mon', 'red'),
                    ('Rev Cav', 'RA-RaSIB01:RF-LLRF:FDLCavRevAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLCavRevPhs-Mon', 'darkSlateBlue'),
                    ('Fwd Ssa', 'RA-RaSIB01:RF-LLRF:FDLFwdSSAAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLFwdSSAPhs-Mon', 'darkGreen'),
                    ('Rev Ssa', 'RA-RaSIB01:RF-LLRF:FDLRevSSAAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLRevSSAPhs-Mon', 'magenta'),
                    ('Ctrl', 'RA-RaSIB01:RF-LLRF:FDLCtrlAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLCtrlPhs-Mon', 'darkCyan'),
                    ('Ref', 'RA-RaSIB01:RF-LLRF:FDLSLRefAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLSLRefPhs-Mon', 'darkRed'),
                    ('Err', 'RA-RaSIB01:RF-LLRF:FDLSLErrAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLSLErrPhs-Mon', 'purple'),
                    ('Err Acc', 'RA-RaSIB01:RF-LLRF:FDLSLErrAccAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLSLErrAccPhs-Mon', 'saddlebrown'),
                    ('MO', 'RA-RaSIB01:RF-LLRF:FDLMOAmp-Mon', 'RA-RaSIB01:RF-LLRF:FDLMOPhs-Mon', 'darkBlue'),
                    ('Tune', None, 'RA-RaSIB01:RF-LLRF:FDLTuneDephs-Mon', 'orangered'),
                    ('Tune Filt', None, 'RA-RaSIB01:RF-LLRF:FDLTuneDephsFilt-Mon', 'darkOliveGreen')
                ),
                'Time': 'RA-RaSIB01:RF-LLRF:FDLScale32-Mon',
                'Mode': 'RA-RaSIB01:RF-LLRF:FDLMode-Mon',
                'SW Trig': 'RA-RaSIB01:RF-LLRF:FDLSwTrig-Mon',
                'HW Trig': 'RA-RaSIB01:RF-LLRF:FDLHwTrig-Mon',
                'Trig': 'RA-RaSIB01:RF-LLRF:FDLTrig-Cmd',
                'Processing': 'RA-RaSIB01:RF-LLRF:FDLProcessing-Mon',
                'Rearm': 'RA-RaSIB01:RF-LLRF:FDLRearm-Sel',
                'Raw': 'RA-RaSIB01:RF-LLRF:FDLRaw',
                'Qty': 'RA-RaSIB01:RF-LLRF:FDLFrame',
                'Size': 'RA-RaSIB01:RF-LLRF:FDLSize-Mon',
                'Duration': 'RA-RaSIB01:RF-LLRF:FDLDuration-Mon',
                'Delay': 'RA-RaSIB01:RF-LLRF:FDLTrigDly',
                'Name': 'B'
            }
        },
        'ADCs and DACs': {
            'A': {
                'Input': {
                    '0': {
                        'Label': 'V Cav (RF In 1)',
                        'I': 'SI-03SP:RF-SRFCav-A:I-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:Q-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:Amp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:Phs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:PwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:PwrdBm-Mon',
                    },
                    '2': {
                        'Label': 'Fwd Cav (RF In 2)',
                        'I': 'SI-03SP:RF-SRFCav-A:FwdI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:FwdQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:FwdAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:FwdPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:FwdPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:FwdPwrdBm-Mon',
                    },
                    '24': {
                        'Label': 'Rev Cav (RF In 3)',
                        'I': 'SI-03SP:RF-SRFCav-A:RevI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:RevQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:RevAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:RevPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:RevPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:RevPwrdBm-Mon',
                    },
                    '35': {
                        'Label': 'Master Osc (RF In 4)',
                        'I': 'RA-RaMO:RF-Gen:SIALLRFI-Mon',
                        'Q': 'RA-RaMO:RF-Gen:SIALLRFQ-Mon',
                        'Amp': 'RA-RaMO:RF-Gen:SIALLRFAmp-Mon',
                        'Phs': 'RA-RaMO:RF-Gen:SIALLRFPhs-Mon',
                        'PwrW': 'RA-RaMO:RF-Gen:SIALLRFPwrW-Mon',
                        'PwrdBm': 'RA-RaMO:RF-Gen:SIALLRFPwrdBm-Mon',
                    },
                    '20': {
                        'Label': 'Fwd SSA 1 (RF In 5)',
                        'I': 'RA-ToSIA01:RF-SSAmpTower:FwdOutI-Mon',
                        'Q': 'RA-ToSIA01:RF-SSAmpTower:FwdOutQ-Mon',
                        'Amp': 'RA-ToSIA01:RF-SSAmpTower:FwdOutAmp-Mon',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPhs-Mon',
                        'PwrW': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                    },
                    '22': {
                        'Label': 'Rev SSA 1 (RF In 6)',
                        'I': 'RA-ToSIA01:RF-SSAmpTower:RevOutI-Mon',
                        'Q': 'RA-ToSIA01:RF-SSAmpTower:RevOutQ-Mon',
                        'Amp': 'RA-ToSIA01:RF-SSAmpTower:RevOutAmp-Mon',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:RevOutPhs-Mon',
                        'PwrW': 'RA-ToSIA01:RF-SSAmpTower:RevOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:RevOutPwrdBm-Mon',
                    },
                    '37': {
                        'Label': 'Fwd SSA 2 (RF In 7)',
                        'I': 'RA-ToSIA02:RF-SSAmpTower:FwdOutI-Mon',
                        'Q': 'RA-ToSIA02:RF-SSAmpTower:FwdOutQ-Mon',
                        'Amp': 'RA-ToSIA02:RF-SSAmpTower:FwdOutAmp-Mon',
                        'Phs': 'RA-ToSIA02:RF-SSAmpTower:FwdOutPhs-Mon',
                        'PwrW': 'RA-ToSIA02:RF-SSAmpTower:FwdOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                    },
                    '39': {
                        'Label': 'Rev SSA 2 (RF In 8)',
                        'I': 'RA-ToSIA02:RF-SSAmpTower:RevOutI-Mon',
                        'Q': 'RA-ToSIA02:RF-SSAmpTower:RevOutQ-Mon',
                        'Amp': 'RA-ToSIA02:RF-SSAmpTower:RevOutAmp-Mon',
                        'Phs': 'RA-ToSIA02:RF-SSAmpTower:RevOutPhs-Mon',
                        'PwrW': 'RA-ToSIA02:RF-SSAmpTower:RevOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:RevOutPwrdBm-Mon',
                    },
                    '41': {
                        'Label': 'FBTN Top (RF In 9)',
                        'I': 'SI-03SP:RF-SRFCav-A:FBTNTopI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:FBTNTopQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:FBTNTopAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:FBTNTopPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:FBTNTopPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:FBTNTopPwrdBm-Mon',
                    },
                    '43': {
                        'Label': 'Wg Pickup (RF In 10)',
                        'I': 'SI-03SP:RF-SRFCav-A:WgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:WgPkupQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:WgPkupAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:WgPkupPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:WgPkupPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:WgPkupPwrdBm-Mon',
                    },
                    '45': {
                        'Label': 'FBTN Bot (RF In 11)',
                        'I': 'SI-03SP:RF-SRFCav-A:FBTNBotI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:FBTNBotQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:FBTNBotAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:FBTNBotPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:FBTNBotPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:FBTNBotPwrdBm-Mon',
                    },
                    '47': {
                        'Label': 'Inp SSA 1 (RF In 12)',
                        'I': 'RA-ToSIA01:RF-SSAmpTower:FwdInI-Mon',
                        'Q': 'RA-ToSIA01:RF-SSAmpTower:FwdInQ-Mon',
                        'Amp': 'RA-ToSIA01:RF-SSAmpTower:FwdInAmp-Mon',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:FwdInPhs-Mon',
                        'PwrW': 'RA-ToSIA01:RF-SSAmpTower:FwdInPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:FwdInPwrdBm-Mon',
                    },
                    '49': {
                        'Label': 'Inp SSA 2 (RF In 13)',
                        'I': 'RA-ToSIA02:RF-SSAmpTower:FwdInI-Mon',
                        'Q': 'RA-ToSIA02:RF-SSAmpTower:FwdInQ-Mon',
                        'Amp': 'RA-ToSIA02:RF-SSAmpTower:FwdInAmp-Mon',
                        'Phs': 'RA-ToSIA02:RF-SSAmpTower:FwdInPhs-Mon',
                        'PwrW': 'RA-ToSIA02:RF-SSAmpTower:FwdInPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:FwdInPwrdBm-Mon',
                    },
                    '51': {
                        'Label': 'Fwd Circ (RF In 14)',
                        'I': 'SI-03SP:RF-SRFCav-A:WgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:WgPkupQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:WgPkupAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:WgPkupPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:WgPkupPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:WgPkupPwrdBm-Mon',
                    },
                    '53': {
                        'Label': 'Rev Circ (RF In 15)',
                        'I': 'RA-TL:RF-Circulator-SIA:RevOutI-Mon',
                        'Q': 'RA-TL:RF-Circulator-SIA:RevOutQ-Mon',
                        'Amp': 'RA-TL:RF-Circulator-SIA:RevOutAmp-Mon',
                        'Phs': 'RA-TL:RF-Circulator-SIA:RevOutPhs-Mon',
                        'PwrW': 'RA-TL:RF-Circulator-SIA:RevOutPwrW-Mon',
                        'PwrdBm': 'RA-TL:RF-Circulator-SIA:RevOutPwrdBm-Mon',
                    },
                    '91': {
                        'Label': 'Mux DACsIF (RF In 16)',
                        'I': 'RA-RaSIA01:RF-LLRF:DACIFI-Mon',
                        'Q': 'RA-RaSIA01:RF-LLRF:DACIFQ-Mon',
                        'Amp': 'RA-RaSIA01:RF-LLRF:DACIFAmp-Mon',
                        'Phs': 'RA-RaSIA01:RF-LLRF:DACIFPhs-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'I': '-',
                        'Q': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaSIA01:RF-LLRF:Dephase-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    }
                },
                'Control': {
                    'ADC': {
                        'Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaSIA01:RF-LLRF:PhShADC'],
                        '2': ['Phase Shift Cavity', 'RA-RaSIA01:RF-LLRF:PhShCav'],
                        '3': ['Phase Shift Fwd Cav', 'RA-RaSIA01:RF-LLRF:PhShFwdCav'],
                        '8': ['Gain Fwd Cavity', 'RA-RaSIA01:RF-LLRF:GainFwdCav'],
                        '4': ['Phase Shift Fwd SSA 1', 'RA-RaSIA01:RF-LLRF:PhShFwdSSA1'],
                        '9': ['Gain Fwd SSA 1', 'RA-RaSIA01:RF-LLRF:GainFwdSSA1'],
                        '5': ['Phase Shift Fwd SSA 2', 'RA-RaSIA01:RF-LLRF:PhShFwdSSA2'],
                        '10': ['Gain Fwd SSA 2', 'RA-RaSIA01:RF-LLRF:GainFwdSSA2'],
                        '6': ['Phase Shift Fwd SSA 3', 'RA-RaSIA01:RF-LLRF:PhShFwdSSA3'],
                        '11': ['Gain Fwd SSA 3', 'RA-RaSIA01:RF-LLRF:GainFwdSSA3'],
                        '7': ['Phase Shift Fwd SSA 4', 'RA-RaSIA01:RF-LLRF:PhShFwdSSA4'],
                        '12': ['Gain Fwd SSA 4', 'RA-RaSIA01:RF-LLRF:GainFwdSSA4'],
                    },
                    'DAC': {
                        'Enable': ['102 - DACs Phase Shift Enable', 'RA-RaSIA01:RF-LLRF:PhShDAC'],
                        '14': ['Phase Shift Drive SSA 1', 'RA-RaSIA01:RF-LLRF:PhShSSA1'],
                        '18': ['Gain Drive SSA 1', 'RA-RaSIA01:RF-LLRF:GainSSA1'],
                        '15': ['Phase Shift Drive SSA 2', 'RA-RaSIA01:RF-LLRF:PhShSSA2'],
                        '19': ['Gain Drive SSA 2', 'RA-RaSIA01:RF-LLRF:GainSSA2'],
                        '16': ['Phase Shift Drive SSA 3', 'RA-RaSIA01:RF-LLRF:PhShSSA3'],
                        '20': ['Gain Drive SSA 3', 'RA-RaSIA01:RF-LLRF:GainSSA3'],
                        '17': ['Phase Shift Drive SSA 4', 'RA-RaSIA01:RF-LLRF:PhShSSA4'],
                        '21': ['Gain Drive SSA 4', 'RA-RaSIA01:RF-LLRF:GainSSA4']
                    }
                },
            },
            'B': {
                'Input': {
                    '0': {
                        'Label': 'V Cav (RF In 1)',
                        'I': 'SI-03SP:RF-SRFCav-B:I-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:Q-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:Amp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:Phs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:PwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:PwrdBm-Mon',
                    },
                    '2': {
                        'Label': 'Fwd Cav (RF In 2)',
                        'I': 'SI-03SP:RF-SRFCav-B:FwdI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:FwdQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:FwdAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:FwdPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:FwdPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:FwdPwrdBm-Mon',
                    },
                    '24': {
                        'Label': 'Rev Cav (RF In 3)',
                        'I': 'SI-03SP:RF-SRFCav-B:RevI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:RevQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:RevAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:RevPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:RevPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:RevPwrdBm-Mon',
                    },
                    '35': {
                        'Label': 'Master Osc (RF In 4)',
                        'I': 'RA-RaMO:RF-Gen:SIBLLRFI-Mon',
                        'Q': 'RA-RaMO:RF-Gen:SIBLLRFQ-Mon',
                        'Amp': 'RA-RaMO:RF-Gen:SIBLLRFAmp-Mon',
                        'Phs': 'RA-RaMO:RF-Gen:SIBLLRFPhs-Mon',
                        'PwrW': 'RA-RaMO:RF-Gen:SIBLLRFPwrW-Mon',
                        'PwrdBm': 'RA-RaMO:RF-Gen:SIBLLRFPwrdBm-Mon',
                    },
                    '20': {
                        'Label': 'Fwd SSA 3 (RF In 5)',
                        'I': 'RA-ToSIB03:RF-SSAmpTower:FwdOutI-Mon',
                        'Q': 'RA-ToSIB03:RF-SSAmpTower:FwdOutQ-Mon',
                        'Amp': 'RA-ToSIB03:RF-SSAmpTower:FwdOutAmp-Mon',
                        'Phs': 'RA-ToSIB03:RF-SSAmpTower:FwdOutPhs-Mon',
                        'PwrW': 'RA-ToSIB03:RF-SSAmpTower:FwdOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB03:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                    },
                    '22': {
                        'Label': 'Rev SSA 3 (RF In 6)',
                        'I': 'RA-ToSIB03:RF-SSAmpTower:RevOutI-Mon',
                        'Q': 'RA-ToSIB03:RF-SSAmpTower:RevOutQ-Mon',
                        'Amp': 'RA-ToSIB03:RF-SSAmpTower:RevOutAmp-Mon',
                        'Phs': 'RA-ToSIB03:RF-SSAmpTower:RevOutPhs-Mon',
                        'PwrW': 'RA-ToSIB03:RF-SSAmpTower:RevOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB03:RF-SSAmpTower:RevOutPwrdBm-Mon',
                    },
                    '37': {
                        'Label': 'Fwd SSA 4 (RF In 7)',
                        'I': 'RA-ToSIB04:RF-SSAmpTower:FwdOutI-Mon',
                        'Q': 'RA-ToSIB04:RF-SSAmpTower:FwdOutQ-Mon',
                        'Amp': 'RA-ToSIB04:RF-SSAmpTower:FwdOutAmp-Mon',
                        'Phs': 'RA-ToSIB04:RF-SSAmpTower:FwdOutPhs-Mon',
                        'PwrW': 'RA-ToSIB04:RF-SSAmpTower:FwdOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB04:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                    },
                    '39': {
                        'Label': 'Rev SSA 4 (RF In 8)',
                        'I': 'RA-ToSIB04:RF-SSAmpTower:RevOutI-Mon',
                        'Q': 'RA-ToSIB04:RF-SSAmpTower:RevOutQ-Mon',
                        'Amp': 'RA-ToSIB04:RF-SSAmpTower:RevOutAmp-Mon',
                        'Phs': 'RA-ToSIB04:RF-SSAmpTower:RevOutPhs-Mon',
                        'PwrW': 'RA-ToSIB04:RF-SSAmpTower:RevOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB04:RF-SSAmpTower:RevOutPwrdBm-Mon',
                    },
                    '41': {
                        'Label': 'FBTN Top (RF In 9)',
                        'I': 'SI-03SP:RF-SRFCav-B:FBTNTopI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:FBTNTopQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:FBTNTopAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:FBTNTopPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:FBTNTopPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:FBTNTopPwrdBm-Mon',
                    },
                    '43': {
                        'Label': 'Wg Pickup (RF In 10)',
                        'I': 'SI-03SP:RF-SRFCav-B:WgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:WgPkupQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:WgPkupAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:WgPkupPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:WgPkupPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:WgPkupPwrdBm-Mon',
                    },
                    '45': {
                        'Label': 'FBTN Bot (RF In 11)',
                        'I': 'SI-03SP:RF-SRFCav-B:FBTNBotI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:FBTNBotQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:FBTNBotAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:FBTNBotPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:FBTNBotPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:FBTNBotPwrdBm-Mon',
                    },
                    '47': {
                        'Label': 'Inp SSA 3 (RF In 12)',
                        'I': 'RA-ToSIB03:RF-SSAmpTower:FwdInI-Mon',
                        'Q': 'RA-ToSIB03:RF-SSAmpTower:FwdInQ-Mon',
                        'Amp': 'RA-ToSIB03:RF-SSAmpTower:FwdInAmp-Mon',
                        'Phs': 'RA-ToSIB03:RF-SSAmpTower:FwdInPhs-Mon',
                        'PwrW': 'RA-ToSIB03:RF-SSAmpTower:FwdInPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB03:RF-SSAmpTower:FwdInPwrdBm-Mon',
                    },
                    '49': {
                        'Label': 'Inp SSA 4 (RF In 13)',
                        'I': 'RA-ToSIB04:RF-SSAmpTower:FwdInI-Mon',
                        'Q': 'RA-ToSIB04:RF-SSAmpTower:FwdInQ-Mon',
                        'Amp': 'RA-ToSIB04:RF-SSAmpTower:FwdInAmp-Mon',
                        'Phs': 'RA-ToSIB04:RF-SSAmpTower:FwdInPhs-Mon',
                        'PwrW': 'RA-ToSIB04:RF-SSAmpTower:FwdInPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB04:RF-SSAmpTower:FwdInPwrdBm-Mon',
                    },
                    '51': {
                        'Label': 'Fwd Circ (RF In 14)',
                        'I': 'SI-03SP:RF-SRFCav-B:WgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:WgPkupQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:WgPkupAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:WgPkupPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:WgPkupPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:WgPkupPwrdBm-Mon',
                    },
                    '53': {
                        'Label': 'Rev Circ (RF In 15)',
                        'I': 'RA-TL:RF-Circulator-SIB:RevOutI-Mon',
                        'Q': 'RA-TL:RF-Circulator-SIB:RevOutQ-Mon',
                        'Amp': 'RA-TL:RF-Circulator-SIB:RevOutAmp-Mon',
                        'Phs': 'RA-TL:RF-Circulator-SIB:RevOutPhs-Mon',
                        'PwrW': 'RA-TL:RF-Circulator-SIB:RevOutPwrW-Mon',
                        'PwrdBm': 'RA-TL:RF-Circulator-SIB:RevOutPwrdBm-Mon',
                    },
                    '91': {
                        'Label': 'Mux DACsIF (RF In 16)',
                        'I': 'RA-RaSIB01:RF-LLRF:DACIFI-Mon',
                        'Q': 'RA-RaSIB01:RF-LLRF:DACIFQ-Mon',
                        'Amp': 'RA-RaSIB01:RF-LLRF:DACIFAmp-Mon',
                        'Phs': 'RA-RaSIB01:RF-LLRF:DACIFPhs-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'I': '-',
                        'Q': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaSIB01:RF-LLRF:Dephase-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    }
                },
                'Control': {
                    'ADC': {
                        'Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaSIB01:RF-LLRF:PhShADC'],
                        '2': ['Phase Shift Cavity', 'RA-RaSIB01:RF-LLRF:PhShCav'],
                        '3': ['Phase Shift Fwd Cav', 'RA-RaSIB01:RF-LLRF:PhShFwdCav'],
                        '8': ['Gain Fwd Cavity', 'RA-RaSIB01:RF-LLRF:GainFwdCav'],
                        '4': ['Phase Shift Fwd SSA 1', 'RA-RaSIB01:RF-LLRF:PhShFwdSSA1'],
                        '9': ['Gain Fwd SSA 1', 'RA-RaSIB01:RF-LLRF:GainFwdSSA1'],
                        '5': ['Phase Shift Fwd SSA 2', 'RA-RaSIB01:RF-LLRF:PhShFwdSSA2'],
                        '10': ['Gain Fwd SSA 2', 'RA-RaSIB01:RF-LLRF:GainFwdSSA2'],
                        '6': ['Phase Shift Fwd SSA 3', 'RA-RaSIB01:RF-LLRF:PhShFwdSSA3'],
                        '11': ['Gain Fwd SSA 3', 'RA-RaSIB01:RF-LLRF:GainFwdSSA3'],
                        '7': ['Phase Shift Fwd SSA 4', 'RA-RaSIB01:RF-LLRF:PhShFwdSSA4'],
                        '12': ['Gain Fwd SSA 4', 'RA-RaSIB01:RF-LLRF:GainFwdSSA4'],
                    },
                    'DAC': {
                        'Enable': ['102 - DACs Phase Shift Enable', 'RA-RaSIB01:RF-LLRF:PhShDAC'],
                        '14': ['Phase Shift Drive SSA 1', 'RA-RaSIB01:RF-LLRF:PhShSSA1'],
                        '18': ['Gain Drive SSA 1', 'RA-RaSIB01:RF-LLRF:GainSSA1'],
                        '15': ['Phase Shift Drive SSA 2', 'RA-RaSIB01:RF-LLRF:PhShSSA2'],
                        '19': ['Gain Drive SSA 2', 'RA-RaSIB01:RF-LLRF:GainSSA2'],
                        '16': ['Phase Shift Drive SSA 3', 'RA-RaSIB01:RF-LLRF:PhShSSA3'],
                        '20': ['Gain Drive SSA 3', 'RA-RaSIB01:RF-LLRF:GainSSA3'],
                        '17': ['Phase Shift Drive SSA 4', 'RA-RaSIB01:RF-LLRF:PhShSSA4'],
                        '21': ['Gain Drive SSA 4', 'RA-RaSIB01:RF-LLRF:GainSSA4']
                    }
                }
            }
        },
        'Hardware': {
            'A': {
                'FPGA': {
                    'Temp': 'RA-RaSIA01:RF-LLRF:FPGATemp-Mon',
                    'Temp Max': 'RA-RaSIA01:RF-LLRF:FPGATempMax-Mon',
                    'Temp Min': 'RA-RaSIA01:RF-LLRF:FPGATempMin-Mon',
                    'Vint': 'RA-RaSIA01:RF-LLRF:FPGAVint-Mon',
                    'Vint Max': 'RA-RaSIA01:RF-LLRF:FPGAVintMax-Mon',
                    'Vint Min': 'RA-RaSIA01:RF-LLRF:FPGAVintMin-Mon',
                    'Vaux': 'RA-RaSIA01:RF-LLRF:FPGAVaux-Mon',
                    'Vaux Max': 'RA-RaSIA01:RF-LLRF:FPGAVauxMax-Mon',
                    'Vaux Min': 'RA-RaSIA01:RF-LLRF:FPGAVauxMin-Mon'
                },
                'Mo1000': {
                    'Temp': 'RA-RaSIA01:RF-LLRF:MO1000Temp-Mon',
                    'Temp DAC 1': 'RA-RaSIA01:RF-LLRF:MO1000DAC1Temp-Mon',
                    'Temp DAC 2': 'RA-RaSIA01:RF-LLRF:MO1000DAC2Temp-Mon'
                },
                'Mi125': {
                    'Temp': 'RA-RaSIA01:RF-LLRF:M125Temp-Mon',
                },
                'GPIO': {
                    'ADC 0': 'RA-RaSIA01:RF-LLRF:GPIOADC0-Mon',
                    'ADC 3': 'RA-RaSIA01:RF-LLRF:GPIOADC3-Mon'
                },
                'Clock Src': 'RA-RaSIA01:RF-LLRF:MO1000ClkSrc-Sel',
                'Loop Trigger': 'RA-RaSIA01:RF-LLRF:LoopTrigProc-Cmd',
                'PLL': 'RA-RaSIA01:RF-LLRF:MO1000PLL-Mon',
                'FPGA Init': 'RA-RaSIA01:RF-LLRF:FPGAInit-Cmd',
                'Cav Type': 'RA-RaSIA01:RF-LLRF:CavType-Mon',
                'Errors': 'RA-RaSIA01:RF-LLRF:InitErrors-Mon',
                'Int. Errors': 'RA-RaSIA01:RF-LLRF:InternalErr-Mon',
                'Int. Err. Clear': 'RA-RaSIA01:RF-LLRF:ResetIntError-Cmd',
                'Init': 'RA-RaSIA01:RF-LLRF:InitStatus-Mon',
                'Versions': {
                    'Firmware': 'RA-RaSIA01:RF-LLRF:FPGAVersion-Mon',
                    'IOC': 'RA-RaSIA01:RF-LLRF:Version-Mon'
                },
            },
            'B': {
                'FPGA': {
                    'Temp': 'RA-RaSIB01:RF-LLRF:FPGATemp-Mon',
                    'Temp Max': 'RA-RaSIB01:RF-LLRF:FPGATempMax-Mon',
                    'Temp Min': 'RA-RaSIB01:RF-LLRF:FPGATempMin-Mon',
                    'Vint': 'RA-RaSIB01:RF-LLRF:FPGAVint-Mon',
                    'Vint Max': 'RA-RaSIB01:RF-LLRF:FPGAVintMax-Mon',
                    'Vint Min': 'RA-RaSIB01:RF-LLRF:FPGAVintMin-Mon',
                    'Vaux': 'RA-RaSIB01:RF-LLRF:FPGAVaux-Mon',
                    'Vaux Max': 'RA-RaSIB01:RF-LLRF:FPGAVauxMax-Mon',
                    'Vaux Min': 'RA-RaSIB01:RF-LLRF:FPGAVauxMin-Mon'
                },
                'Mo1000': {
                    'Temp': 'RA-RaSIB01:RF-LLRF:MO1000Temp-Mon',
                    'Temp DAC 1': 'RA-RaSIB01:RF-LLRF:MO1000DAC1Temp-Mon',
                    'Temp DAC 2': 'RA-RaSIB01:RF-LLRF:MO1000DAC2Temp-Mon'
                },
                'Mi125': {
                    'Temp': 'RA-RaSIB01:RF-LLRF:M125Temp-Mon',
                },
                'GPIO': {
                    'ADC 0': 'RA-RaSIB01:RF-LLRF:GPIOADC0-Mon',
                    'ADC 3': 'RA-RaSIB01:RF-LLRF:GPIOADC3-Mon'
                },
                'Clock Src': 'RA-RaSIB01:RF-LLRF:MO1000ClkSrc-Sel',
                'Loop Trigger': 'RA-RaSIB01:RF-LLRF:LoopTrigProc-Cmd',
                'PLL': 'RA-RaSIB01:RF-LLRF:MO1000PLL-Mon',
                'FPGA Init': 'RA-RaSIB01:RF-LLRF:FPGAInit-Cmd',
                'Cav Type': 'RA-RaSIB01:RF-LLRF:CavType-Mon',
                'Errors': 'RA-RaSIB01:RF-LLRF:InitErrors-Mon',
                'Int. Errors': 'RA-RaSIB01:RF-LLRF:InternalErr-Mon',
                'Int. Err. Clear': 'RA-RaSIB01:RF-LLRF:ResetIntError-Cmd',
                'Init': 'RA-RaSIB01:RF-LLRF:InitStatus-Mon',
                'Versions': {
                    'Firmware': 'RA-RaSIB01:RF-LLRF:FPGAVersion-Mon',
                    'IOC': 'RA-RaSIB01:RF-LLRF:Version-Mon'
                },
            }
        },
        'Loops': {
            'A': {
                'Control': {
                    '24 mV': ['Amp Loop Ref (mV)', 'RA-RaSIA01:RF-LLRF:ALRef'],
                    '24 VGap': ['Amp Loop Ref (VGap)', 'RA-RaSIA01:RF-LLRF:ALRefVGap'],
                    '25': ['Phase Loop Ref', 'RA-RaSIA01:RF-LLRF:PLRef'],
                    '29': ['Voltage Inc. Rate', 'RA-RaSIA01:RF-LLRF:AmpIncRate'],
                    '28': ['Phase Inc. Rate', 'RA-RaSIA01:RF-LLRF:PhsIncRate'],
                    '106': ['Look Reference', 'RA-RaSIA01:RF-LLRF:LookRef-Cmd'],
                    '114': ['Rect/Polar Mode Select', 'RA-RaSIA01:RF-LLRF:LoopMode'],
                    '107': ['Quadrant Selection', 'RA-RaSIA01:RF-LLRF:Quad'],
                    '26 mV': ['Amp Ref Min (mV)', 'RA-RaSIA01:RF-LLRF:AmpRefMin'],
                    '26 VGap': ['Amp Ref Min (VGap)', 'RA-RaSIA01:RF-LLRF:AmpRefMinVGap'],
                    '27': ['Phase Ref Min', 'RA-RaSIA01:RF-LLRF:PhsRefMin'],
                    '30': ['Open Loop Gain', 'RA-RaSIA01:RF-LLRF:OLGain'],
                    '31': ['Phase Correction Control', 'RA-RaSIA01:RF-LLRF:PhsCorrection'],
                    '80': ['Phase Correct Error', 'RA-RaSIA01:RF-LLRF:PhsCorrErr-Mon'],
                    '81': ['Phase Correct Control', 'RA-RaSIA01:RF-LLRF:PhsCorrCtrl-Mon'],
                    '125': ['Fwd Min Amp & Phs', 'RA-RaSIA01:RF-LLRF:LoopFwdMin'],
                    'Mode': 'RA-RaSIA01:RF-LLRF:LoopMode-Sts',
                    'Limits': {
                        '24': ['Amp Loop Ref', 'RA-RaSIA01:RF-LLRF:ALRef'],
                        '30': ['Open Loop Gain', 'RA-RaSIA01:RF-LLRF:OLGain'],
                        '0': ['Slow Loop Kp', 'RA-RaSIA01:RF-LLRF:SLKP'],
                    }
                },
                'General': {
                    '0': {
                        'Label': 'Cavity Voltage',
                        'InPhs': 'SI-03SP:RF-SRFCav-A:I-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-A:Q-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:Amp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:Phs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:PwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:PwrdBm-Mon',
                    },
                    '2': {
                        'Label': 'Forward Power',
                        'InPhs': 'SI-03SP:RF-SRFCav-A:FwdI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-A:FwdQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:FwdAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:FwdPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:FwdPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:FwdPwrdBm-Mon',
                    },
                    '20': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToSIA01:RF-SSAmpTower:FwdOutI-Mon',
                        'Quad': 'RA-ToSIA01:RF-SSAmpTower:FwdOutQ-Mon',
                        'Amp': 'RA-ToSIA01:RF-SSAmpTower:FwdOutAmp-Mon',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPhs-Mon',
                        'PwrW': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaSIA01:RF-LLRF:Dephase-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                },
                'Rect': {
                    '30': {
                        'Label': 'Fwd Pwr SSA 2',
                        'InPhs': 'SI-03SP:RF-SRFCav-A:FBTNTopI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-A:FBTNTopQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-A:FBTNTopAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:FBTNTopPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-A:FBTNTopPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-A:FBTNTopPwrdBm-Mon',
                    },
                    'Slow': {
                        'Control': {
                            '100': ['Enable', 'RA-RaSIA01:RF-LLRF:SL'],
                            '110': ['Input Selection', 'RA-RaSIA01:RF-LLRF:SLInp'],
                            '13': ['PI Limit', 'RA-RaSIA01:RF-LLRF:SLPILim'],
                            '1': ['Ki', 'RA-RaSIA01:RF-LLRF:SLKI'],
                            '0': ['Kp', 'RA-RaSIA01:RF-LLRF:SLKP']
                        },
                        '512': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SLRefI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SLRefQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SLRefAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SLRefPhs-Mon'
                        },
                        '120': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SLInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SLInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SLInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SLInpPhs-Mon'
                        },
                        '14': {
                            'Label': 'Error',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SLErrorI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SLErrorQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SLErrorAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SLErrorPhs-Mon'
                        },
                        '16': {
                            'Label': 'Error Accum',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SLErrAccI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SLErrAccQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SLErrAccAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SLErrAccPhs-Mon'
                        },
                        '71': {
                            'Label': 'Slow Control Output',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SLCtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SLCtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SLCtrlPhs-Mon'
                        },
                    },
                    'Fast': {
                        'Control': {
                            '115': ['Enable', 'RA-RaSIA01:RF-LLRF:FL'],
                            '111': ['Input Selection', 'RA-RaSIA01:RF-LLRF:FLInp'],
                            '124': ['PI Limit', 'RA-RaSIA01:RF-LLRF:FLPILim'],
                            '119': ['Ki', 'RA-RaSIA01:RF-LLRF:FLKI'],
                            '118': ['Kp', 'RA-RaSIA01:RF-LLRF:FLKP']
                        },
                        '124': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:FLRefI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:FLRefQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:FLRefAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:FLRefPhs-Mon'
                        },
                        '112': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:FLInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:FLInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:FLInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:FLInpPhs-Mon'
                        },
                        '118': {
                            'Label': 'Fast Control Output',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:FLCtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:FLCtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:FLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:FLCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SSA2CtrlPhs-Mon'
                        }
                    }
                },
                'Polar': {
                    '527': {
                        'Label': 'Amp Ref',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': 'RA-RaSIA01:RF-LLRF:AmpRefOld-Mon',
                        'Phs': '-',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    'Amp': {
                        'Control': {
                            '116': ['Enable', 'RA-RaSIA01:RF-LLRF:AL'],
                            '112': ['Input Selection', 'RA-RaSIA01:RF-LLRF:ALInp'],
                            '121': ['Ki', 'RA-RaSIA01:RF-LLRF:ALKI'],
                            '120': ['Kp', 'RA-RaSIA01:RF-LLRF:ALKP']
                        },
                        '100': {
                            'Label': 'Amp Loop Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:ALInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:ALInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:ALInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:ALInpPhs-Mon'
                        },
                        '104': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF:ALAmpInp-Mon',
                            'Phs': '-'
                        },
                        '105': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF:ALPhsInp-Mon'
                        },
                        '109': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF:ALErr-Mon',
                            'Phs': '-'
                        },
                        '110': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF:ALErrAcc-Mon',
                            'Phs': '-'
                        },
                        '528': {
                            'Label': 'Phase Ref',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF:PhsRefOld-Mon'
                        }
                    },
                    'Phase': {
                        'Control': {
                            '117': ['Enable', 'RA-RaSIA01:RF-LLRF:PL'],
                            '113': ['Input Selection', 'RA-RaSIA01:RF-LLRF:PLInp'],
                            '123': ['Ki', 'RA-RaSIA01:RF-LLRF:PLKI'],
                            '122': ['Kp', 'RA-RaSIA01:RF-LLRF:PLKP']
                        },
                        '102': {
                            'Label': 'Phase Loop Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:PLInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:PLInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:PLInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:PLInpPhs-Mon'
                        },
                        '106': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF:PLAmpInp-Mon',
                            'Phs': '-'
                        },
                        '107': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF:PLPhsInp-Mon'
                        },
                        '112': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF:PLErr-Mon'
                        },
                        '113': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF:PLErrAcc-Mon'
                        },
                        '114': {
                            'Label': 'Polar Control Output',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:POCtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:POCtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:POCtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:POCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:SSA2CtrlPhs-Mon'
                        }
                    }
                }
            },
            'B': {
                'Control': {
                    '24 mV': ['Amp Loop Ref (mV)', 'RA-RaSIB01:RF-LLRF:ALRef'],
                    '24 VGap': ['Amp Loop Ref (VGap)', 'RA-RaSIB01:RF-LLRF:ALRefVGap'],
                    '25': ['Phase Loop Ref', 'RA-RaSIB01:RF-LLRF:PLRef'],
                    '29': ['Voltage Inc. Rate', 'RA-RaSIB01:RF-LLRF:AmpIncRate'],
                    '28': ['Phase Inc. Rate', 'RA-RaSIB01:RF-LLRF:PhsIncRate'],
                    '106': ['Look Reference', 'RA-RaSIB01:RF-LLRF:LookRef-Cmd'],
                    '114': ['Rect/Polar Mode Select', 'RA-RaSIB01:RF-LLRF:LoopMode'],
                    '107': ['Quadrant Selection', 'RA-RaSIB01:RF-LLRF:Quad'],
                    '26 mV': ['Amp Ref Min (mV)', 'RA-RaSIB01:RF-LLRF:AmpRefMin'],
                    '26 VGap': ['Amp Ref Min (VGap)', 'RA-RaSIB01:RF-LLRF:AmpRefMinVGap'],
                    '27': ['Phase Ref Min', 'RA-RaSIB01:RF-LLRF:PhsRefMin'],
                    '30': ['Open Loop Gain', 'RA-RaSIB01:RF-LLRF:OLGain'],
                    '31': ['Phase Correction Control', 'RA-RaSIB01:RF-LLRF:PhsCorrection'],
                    '80': ['Phase Correct Error', 'RA-RaSIB01:RF-LLRF:PhsCorrErr-Mon'],
                    '81': ['Phase Correct Control', 'RA-RaSIB01:RF-LLRF:PhsCorrCtrl-Mon'],
                    '125': ['Fwd Min Amp & Phs', 'RA-RaSIB01:RF-LLRF:LoopFwdMin'],
                    'Mode': 'RA-RaSIB01:RF-LLRF:LoopMode-Sts',
                    'Limits': {
                        '24': ['Amp Loop Ref', 'RA-RaSIB01:RF-LLRF:ALRef'],
                        '30': ['Open Loop Gain', 'RA-RaSIB01:RF-LLRF:OLGain'],
                        '0': ['Slow Loop Kp', 'RA-RaSIB01:RF-LLRF:SLKP'],
                    }
                },
                'General': {
                    '0': {
                        'Label': 'Cavity Voltage',
                        'InPhs': 'SI-03SP:RF-SRFCav-B:I-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-B:Q-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:Amp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:Phs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:PwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:PwrdBm-Mon',
                    },
                    '2': {
                        'Label': 'Forward Power',
                        'InPhs': 'SI-03SP:RF-SRFCav-B:FwdI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-B:FwdQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:FwdAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:FwdPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:FwdPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:FwdPwrdBm-Mon',
                    },
                    '20': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToSIB01:RF-SSAmpTower:FwdOutI-Mon',
                        'Quad': 'RA-ToSIB01:RF-SSAmpTower:FwdOutQ-Mon',
                        'Amp': 'RA-ToSIB01:RF-SSAmpTower:FwdOutAmp-Mon',
                        'Phs': 'RA-ToSIB01:RF-SSAmpTower:FwdOutPhs-Mon',
                        'PwrW': 'RA-ToSIB01:RF-SSAmpTower:FwdOutPwrW-Mon',
                        'PwrdBm': 'RA-ToSIB01:RF-SSAmpTower:FwdOutPwrdBm-Mon',
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': '-',
                        'Phs': 'RA-RaSIB01:RF-LLRF:Dephase-Mon',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                },
                'Rect': {
                    '30': {
                        'Label': 'Fwd Pwr SSA 2',
                        'InPhs': 'SI-03SP:RF-SRFCav-B:FBTNTopI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-B:FBTNTopQ-Mon',
                        'Amp': 'SI-03SP:RF-SRFCav-B:FBTNTopAmp-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:FBTNTopPhs-Mon',
                        'PwrW': 'SI-03SP:RF-SRFCav-B:FBTNTopPwrW-Mon',
                        'PwrdBm': 'SI-03SP:RF-SRFCav-B:FBTNTopPwrdBm-Mon',
                    },
                    'Slow': {
                        'Control': {
                            '100': ['Enable', 'RA-RaSIB01:RF-LLRF:SL'],
                            '110': ['Input Selection', 'RA-RaSIB01:RF-LLRF:SLInp'],
                            '13': ['PI Limit', 'RA-RaSIB01:RF-LLRF:SLPILim'],
                            '1': ['Ki', 'RA-RaSIB01:RF-LLRF:SLKI'],
                            '0': ['Kp', 'RA-RaSIB01:RF-LLRF:SLKP']
                        },
                        '512': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SLRefI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SLRefQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SLRefAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SLRefPhs-Mon'
                        },
                        '120': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SLInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SLInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SLInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SLInpPhs-Mon'
                        },
                        '14': {
                            'Label': 'Error',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SLErrorI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SLErrorQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SLErrorAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SLErrorPhs-Mon'
                        },
                        '16': {
                            'Label': 'Error Accum',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SLErrAccI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SLErrAccQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SLErrAccAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SLErrAccPhs-Mon'
                        },
                        '71': {
                            'Label': 'Slow Control Output',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SLCtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SLCtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SLCtrlPhs-Mon'
                        },
                    },
                    'Fast': {
                        'Control': {
                            '115': ['Enable', 'RA-RaSIB01:RF-LLRF:FL'],
                            '111': ['Input Selection', 'RA-RaSIB01:RF-LLRF:FLInp'],
                            '124': ['PI Limit', 'RA-RaSIB01:RF-LLRF:FLPILim'],
                            '119': ['Ki', 'RA-RaSIB01:RF-LLRF:FLKI'],
                            '118': ['Kp', 'RA-RaSIB01:RF-LLRF:FLKP']
                        },
                        '124': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:FLRefI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:FLRefQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:FLRefAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:FLRefPhs-Mon'
                        },
                        '112': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:FLInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:FLInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:FLInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:FLInpPhs-Mon'
                        },
                        '118': {
                            'Label': 'Fast Control Output',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:FLCtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:FLCtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:FLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:FLCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SSA2CtrlPhs-Mon'
                        }
                    }
                },
                'Polar': {
                    '527': {
                        'Label': 'Amp Ref',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp': 'RA-RaSIB01:RF-LLRF:AmpRefOld-Mon',
                        'Phs': '-',
                        'PwrW': '-',
                        'PwrdBm': '-',
                    },
                    'Amp': {
                        'Control': {
                            '116': ['Enable', 'RA-RaSIB01:RF-LLRF:AL'],
                            '112': ['Input Selection', 'RA-RaSIB01:RF-LLRF:ALInp'],
                            '121': ['Ki', 'RA-RaSIB01:RF-LLRF:ALKI'],
                            '120': ['Kp', 'RA-RaSIB01:RF-LLRF:ALKP']
                        },
                        '100': {
                            'Label': 'Amp Loop Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:ALInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:ALInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:ALInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:ALInpPhs-Mon'
                        },
                        '104': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF:ALAmpInp-Mon',
                            'Phs': '-'
                        },
                        '105': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF:ALPhsInp-Mon'
                        },
                        '109': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF:ALErr-Mon',
                            'Phs': '-'
                        },
                        '110': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF:ALErrAcc-Mon',
                            'Phs': '-'
                        },
                        '528': {
                            'Label': 'Phase Ref',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF:PhsRefOld-Mon'
                        }
                    },
                    'Phase': {
                        'Control': {
                            '117': ['Enable', 'RA-RaSIB01:RF-LLRF:PL'],
                            '113': ['Input Selection', 'RA-RaSIB01:RF-LLRF:PLInp'],
                            '123': ['Ki', 'RA-RaSIB01:RF-LLRF:PLKI'],
                            '122': ['Kp', 'RA-RaSIB01:RF-LLRF:PLKP']
                        },
                        '102': {
                            'Label': 'Phase Loop Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:PLInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:PLInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:PLInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:PLInpPhs-Mon'
                        },
                        '106': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF:PLAmpInp-Mon',
                            'Phs': '-'
                        },
                        '107': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF:PLPhsInp-Mon'
                        },
                        '112': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF:PLErr-Mon'
                        },
                        '113': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF:PLErrAcc-Mon'
                        },
                        '114': {
                            'Label': 'Polar Control Output',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:POCtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:POCtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:POCtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:POCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:SSA2CtrlPhs-Mon'
                        }
                    }
                }
            },
        },
        'RampDtls': {
            'A': {
                'Control': {
                    'Ramp Enable': 'RA-RaSIA01:RF-LLRF:RmpEnbl',
                    'Ramp Down Disable': 'RA-RaSIA01:RF-LLRF:RmpDownDsbl',
                    '356': ['T1 Ramp Delay After Trig', 'RA-RaSIA01:RF-LLRF:RmpTs1'],
                    '357': ['T2 Ramp Up', 'RA-RaSIA01:RF-LLRF:RmpTs2'],
                    '358': ['T3 Ramp Top', 'RA-RaSIA01:RF-LLRF:RmpTs3'],
                    '359': ['T4 Ramp Down', 'RA-RaSIA01:RF-LLRF:RmpTs4'],
                    '360': ['Ramp Increase Rate', 'RA-RaSIA01:RF-LLRF:RmpIncTime'],
                    '164': ['Ref Top', 'RA-RaSIA01:RF-LLRF:RefTopAmp-Mon', 'red'],
                    '362 mV': ['Amp Ramp Top (mV)', 'RA-RaSIA01:RF-LLRF:RmpAmpTop'],
                    '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-RaSIA01:RF-LLRF:RmpAmpTopVGap'],
                    '364': ['Phase Ramp Top', 'RA-RaSIA01:RF-LLRF:RmpPhsTop'],
                    '184': ['Ref Bot', 'RA-RaSIA01:RF-LLRF:RefBotAmp-Mon', 'blue'],
                    '361 mV': ['Amp Ramp Bot (mV)', 'RA-RaSIA01:RF-LLRF:RmpAmpBot'],
                    '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-RaSIA01:RF-LLRF:RmpAmpBotVGap'],
                    '363': ['Phase Ramp Bot', 'RA-RaSIA01:RF-LLRF:RmpPhsBot'],
                    '536': ['Ramp Top', 'RA-RaSIA01:RF-LLRF:RmpTop-Mon', 'green'],
                    '533': ['Ramp Ready', 'RA-RaSIA01:RF-LLRF:RmpRdy-Mon'],
                    '365': ['Amp Ramp Up Slope', 'RA-RaSIA01:RF-LLRF:RmpAmpUpCnt'],
                    '366': ['Amp Ramp Down Slope', 'RA-RaSIA01:RF-LLRF:RmpAmpDownCnt'],
                    '367': ['Phase Ramp Up Slope', 'RA-RaSIA01:RF-LLRF:RmpPhsUpCnt'],
                    '368': ['Phase Ramp Down Slope', 'RA-RaSIA01:RF-LLRF:RmpPhsDownCnt'],
                    'Limits': {
                        '362': ['Top Reference', 'RA-RaSIA01:RF-LLRF:RmpAmpTop'],
                        '361': ['Bot Reference', 'RA-RaSIA01:RF-LLRF:RmpAmpBot']
                    }
                },
                'Diagnostics': {
                    'Top': {
                        '164': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:RefTopI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:RefTopQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:RefTopAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:RefTopPhs-Mon',
                            'PwrW': 'RA-RaSIA01:RF-LLRF:RefTopPwrW-Mon',
                            'PwrdBm': 'RA-RaSIA01:RF-LLRF:RefTopPwrdBm-Mon',
                        },
                        '150': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:TopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:TopQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-A:TopAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:TopPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-A:TopPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-A:TopPwrdBm-Mon',
                        },
                        '152': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:FwdTopI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:FwdTopQ-Mon',
                            'Amp': 'RA-ToSIA02:RF-SSAmpTower:FwdTopAmp-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:FwdTopPhs-Mon',
                            'PwrW': 'RA-ToSIA02:RF-SSAmpTower:FwdTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:FwdTopPwrdBm-Mon',
                        },
                        '154': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:RevTopI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:RevTopQ-Mon',
                            'Amp': 'RA-ToSIA02:RF-SSAmpTower:RevTopAmp-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:RevTopPhs-Mon',
                            'PwrW': 'RA-ToSIA02:RF-SSAmpTower:RevTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:RevTopPwrdBm-Mon',
                        },
                        '190': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:FwdTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:FwdTopQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-A:FwdTopAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:FwdTopPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-A:FwdTopPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-A:FwdTopPwrdBm-Mon',
                        },
                        '156': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIA01:RF-SSAmpTower:FwdTopI-Mon',
                            'Quad': 'RA-ToSIA01:RF-SSAmpTower:FwdTopQ-Mon',
                            'Amp': 'RA-ToSIA01:RF-SSAmpTower:FwdTopAmp-Mon',
                            'Phs': 'RA-ToSIA01:RF-SSAmpTower:FwdTopPhs-Mon',
                            'PwrW': 'RA-ToSIA01:RF-SSAmpTower:FwdTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:FwdTopPwrdBm-Mon',
                        },
                        '158': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs':  'RA-ToSIA01:RF-SSAmpTower:RevTopI-Mon',
                            'Quad':  'RA-ToSIA01:RF-SSAmpTower:RevTopQ-Mon',
                            'Amp':  'RA-ToSIA01:RF-SSAmpTower:RevTopAmp-Mon',
                            'Phs':  'RA-ToSIA01:RF-SSAmpTower:RevTopPhs-Mon',
                            'PwrW': 'RA-ToSIA01:RF-SSAmpTower:RevTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:RevTopPwrdBm-Mon',
                        },
                        '160': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:RevTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:RevTopQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-A:RevTopAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:RevTopPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-A:RevTopPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-A:RevTopPwrdBm-Mon',
                        },
                        '168': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:ErrTopI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:ErrTopQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:ErrTopAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:ErrTopPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '166': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:CtrlTopI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:CtrlTopQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:CtrlTopAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:CtrlTopPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '162': {
                            'Label': 'Tuning Dephase',
                            'PV': 'RA-RaSIA01:RF-LLRF:TuneDephsTop-Mon'
                        },
                        '531': {
                            'Label': 'Ramp Trigger',
                            'PV': 'RA-RaSIA01:RF-LLRF:RmpTrigger-Mon'
                        }
                    },
                    'Bot': {
                        '184': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:RefBotI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:RefBotQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:RefBotAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:RefBotPhs-Mon',
                            'PwrW': 'RA-RaSIA01:RF-LLRF:RefBotPwrW-Mon',
                            'PwrdBm': 'RA-RaSIA01:RF-LLRF:RefBotPwrdBm-Mon',
                        },
                        '170': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:BotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:BotQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-A:BotAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:BotPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-A:BotPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-A:BotPwrdBm-Mon',
                        },
                        '172': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:FwdBotI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:FwdBotQ-Mon',
                            'Amp': 'RA-ToSIA02:RF-SSAmpTower:FwdBotAmp-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:FwdBotPhs-Mon',
                            'PwrW': 'RA-ToSIA02:RF-SSAmpTower:FwdBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:FwdBotPwrdBm-Mon',
                        },
                        '174': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:RevBotI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:RevBotQ-Mon',
                            'Amp': 'RA-ToSIA02:RF-SSAmpTower:RevBotAmp-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:RevBotPhs-Mon',
                            'PwrW': 'RA-ToSIA02:RF-SSAmpTower:RevBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA02:RF-SSAmpTower:RevBotPwrdBm-Mon',
                        },
                        '192': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:FwdBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:FwdBotQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-A:FwdBotAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:FwdBotPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-A:FwdBotPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-A:FwdBotPwrdBm-Mon',
                        },
                        '176': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIA01:RF-SSAmpTower:FwdBotI-Mon',
                            'Quad': 'RA-ToSIA01:RF-SSAmpTower:FwdBotQ-Mon',
                            'Amp': 'RA-ToSIA01:RF-SSAmpTower:FwdBotAmp-Mon',
                            'Phs': 'RA-ToSIA01:RF-SSAmpTower:FwdBotPhs-Mon',
                            'PwrW': 'RA-ToSIA01:RF-SSAmpTower:FwdBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:FwdBotPwrdBm-Mon',
                        },
                        '178': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs': 'RA-ToSIA01:RF-SSAmpTower:RevBotI-Mon',
                            'Quad': 'RA-ToSIA01:RF-SSAmpTower:RevBotQ-Mon',
                            'Amp': 'RA-ToSIA01:RF-SSAmpTower:RevBotAmp-Mon',
                            'Phs': 'RA-ToSIA01:RF-SSAmpTower:RevBotPhs-Mon',
                            'PwrW': 'RA-ToSIA01:RF-SSAmpTower:RevBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIA01:RF-SSAmpTower:RevBotPwrdBm-Mon',
                        },
                        '180': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:RevBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:RevBotQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-A:RevBotAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:RevBotPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-A:RevBotPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-A:RevBotPwrdBm-Mon',
                        },
                        '188': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:ErrBotI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:ErrBotQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:ErrBotAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:ErrBotPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '186': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIA01:RF-LLRF:CtrlBotI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF:CtrlBotQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF:CtrlBotAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF:CtrlBotPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '531': {
                            'Label': 'Ramp Trigger',
                            'PV': 'RA-RaSIA01:RF-LLRF:RmpTrigger-Mon'
                        }
                    }
                },
            },
            'B': {
                'Control': {
                    'Ramp Enable': 'RA-RaSIB01:RF-LLRF:RmpEnbl',
                    'Ramp Down Disable': 'RA-RaSIB01:RF-LLRF:RmpDownDsbl',
                    '356': ['T1 Ramp Delay After Trig', 'RA-RaSIB01:RF-LLRF:RmpTs1'],
                    '357': ['T2 Ramp Up', 'RA-RaSIB01:RF-LLRF:RmpTs2'],
                    '358': ['T3 Ramp Top', 'RA-RaSIB01:RF-LLRF:RmpTs3'],
                    '359': ['T4 Ramp Down', 'RA-RaSIB01:RF-LLRF:RmpTs4'],
                    '360': ['Ramp Increase Rate', 'RA-RaSIB01:RF-LLRF:RmpIncTime'],
                    '164': ['Ref Top', 'RA-RaSIB01:RF-LLRF:RefTopAmp-Mon', 'red'],
                    '362 mV': ['Amp Ramp Top (mV)', 'RA-RaSIB01:RF-LLRF:RmpAmpTop'],
                    '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-RaSIB01:RF-LLRF:RmpAmpTopVGap'],
                    '364': ['Phase Ramp Top', 'RA-RaSIB01:RF-LLRF:RmpPhsTop'],
                    '184': ['Ref Bot', 'RA-RaSIB01:RF-LLRF:RefBotAmp-Mon', 'blue'],
                    '361 mV': ['Amp Ramp Bot (mV)', 'RA-RaSIB01:RF-LLRF:RmpAmpBot'],
                    '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-RaSIB01:RF-LLRF:RmpAmpBotVGap'],
                    '363': ['Phase Ramp Bot', 'RA-RaSIB01:RF-LLRF:RmpPhsBot'],
                    '536': ['Ramp Top', 'RA-RaSIB01:RF-LLRF:RmpTop-Mon', 'green'],
                    '533': ['Ramp Ready', 'RA-RaSIB01:RF-LLRF:RmpRdy-Mon'],
                    '365': ['Amp Ramp Up Slope', 'RA-RaSIB01:RF-LLRF:RmpAmpUpCnt'],
                    '366': ['Amp Ramp Down Slope', 'RA-RaSIB01:RF-LLRF:RmpAmpDownCnt'],
                    '367': ['Phase Ramp Up Slope', 'RA-RaSIB01:RF-LLRF:RmpPhsUpCnt'],
                    '368': ['Phase Ramp Down Slope', 'RA-RaSIB01:RF-LLRF:RmpPhsDownCnt'],
                    'Limits': {
                        '362': ['Top Reference', 'RA-RaSIB01:RF-LLRF:RmpAmpTop'],
                        '361': ['Bot Reference', 'RA-RaSIB01:RF-LLRF:RmpAmpBot']
                    }
                },
                'Diagnostics': {
                    'Top': {
                        '164': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:RefTopI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:RefTopQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:RefTopAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:RefTopPhs-Mon',
                            'PwrW': 'RA-RaSIB01:RF-LLRF:RefTopPwrW-Mon',
                            'PwrdBm': 'RA-RaSIB01:RF-LLRF:RefTopPwrdBm-Mon',
                        },
                        '150': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:TopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:TopQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-B:TopAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:TopPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-B:TopPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-B:TopPwrdBm-Mon',
                        },
                        '152': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:FwdTopI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:FwdTopQ-Mon',
                            'Amp': 'RA-ToSIB02:RF-SSAmpTower:FwdTopAmp-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:FwdTopPhs-Mon',
                            'PwrW': 'RA-ToSIB02:RF-SSAmpTower:FwdTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB02:RF-SSAmpTower:FwdTopPwrdBm-Mon',
                        },
                        '154': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:RevTopI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:RevTopQ-Mon',
                            'Amp': 'RA-ToSIB02:RF-SSAmpTower:RevTopAmp-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:RevTopPhs-Mon',
                            'PwrW': 'RA-ToSIB02:RF-SSAmpTower:RevTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB02:RF-SSAmpTower:RevTopPwrdBm-Mon',
                        },
                        '190': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:FwdTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:FwdTopQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-B:FwdTopAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:FwdTopPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-B:FwdTopPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-B:FwdTopPwrdBm-Mon',
                        },
                        '156': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIB01:RF-SSAmpTower:FwdTopI-Mon',
                            'Quad': 'RA-ToSIB01:RF-SSAmpTower:FwdTopQ-Mon',
                            'Amp': 'RA-ToSIB01:RF-SSAmpTower:FwdTopAmp-Mon',
                            'Phs': 'RA-ToSIB01:RF-SSAmpTower:FwdTopPhs-Mon',
                            'PwrW': 'RA-ToSIB01:RF-SSAmpTower:FwdTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB01:RF-SSAmpTower:FwdTopPwrdBm-Mon',
                        },
                        '158': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs':  'RA-ToSIB01:RF-SSAmpTower:RevTopI-Mon',
                            'Quad':  'RA-ToSIB01:RF-SSAmpTower:RevTopQ-Mon',
                            'Amp':  'RA-ToSIB01:RF-SSAmpTower:RevTopAmp-Mon',
                            'Phs':  'RA-ToSIB01:RF-SSAmpTower:RevTopPhs-Mon',
                            'PwrW': 'RA-ToSIB01:RF-SSAmpTower:RevTopPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB01:RF-SSAmpTower:RevTopPwrdBm-Mon',
                        },
                        '160': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:RevTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:RevTopQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-B:RevTopAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:RevTopPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-B:RevTopPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-B:RevTopPwrdBm-Mon',
                        },
                        '168': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:ErrTopI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:ErrTopQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:ErrTopAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:ErrTopPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '166': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:CtrlTopI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:CtrlTopQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:CtrlTopAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:CtrlTopPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '162': {
                            'Label': 'Tuning Dephase',
                            'PV': 'RA-RaSIB01:RF-LLRF:TuneDephsTop-Mon'
                        },
                        '531': {
                            'Label': 'Ramp Trigger',
                            'PV': 'RA-RaSIB01:RF-LLRF:RmpTrigger-Mon'
                        }
                    },
                    'Bot': {
                        '184': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:RefBotI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:RefBotQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:RefBotAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:RefBotPhs-Mon',
                            'PwrW': 'RA-RaSIB01:RF-LLRF:RefBotPwrW-Mon',
                            'PwrdBm': 'RA-RaSIB01:RF-LLRF:RefBotPwrdBm-Mon',
                        },
                        '170': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:BotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:BotQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-B:BotAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:BotPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-B:BotPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-B:BotPwrdBm-Mon',
                        },
                        '172': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:FwdBotI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:FwdBotQ-Mon',
                            'Amp': 'RA-ToSIB02:RF-SSAmpTower:FwdBotAmp-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:FwdBotPhs-Mon',
                            'PwrW': 'RA-ToSIB02:RF-SSAmpTower:FwdBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB02:RF-SSAmpTower:FwdBotPwrdBm-Mon',
                        },
                        '174': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:RevBotI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:RevBotQ-Mon',
                            'Amp': 'RA-ToSIB02:RF-SSAmpTower:RevBotAmp-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:RevBotPhs-Mon',
                            'PwrW': 'RA-ToSIB02:RF-SSAmpTower:RevBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB02:RF-SSAmpTower:RevBotPwrdBm-Mon',
                        },
                        '192': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:FwdBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:FwdBotQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-B:FwdBotAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:FwdBotPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-B:FwdBotPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-B:FwdBotPwrdBm-Mon',
                        },
                        '176': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIB01:RF-SSAmpTower:FwdBotI-Mon',
                            'Quad': 'RA-ToSIB01:RF-SSAmpTower:FwdBotQ-Mon',
                            'Amp': 'RA-ToSIB01:RF-SSAmpTower:FwdBotAmp-Mon',
                            'Phs': 'RA-ToSIB01:RF-SSAmpTower:FwdBotPhs-Mon',
                            'PwrW': 'RA-ToSIB01:RF-SSAmpTower:FwdBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB01:RF-SSAmpTower:FwdBotPwrdBm-Mon',
                        },
                        '178': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs': 'RA-ToSIB01:RF-SSAmpTower:RevBotI-Mon',
                            'Quad': 'RA-ToSIB01:RF-SSAmpTower:RevBotQ-Mon',
                            'Amp': 'RA-ToSIB01:RF-SSAmpTower:RevBotAmp-Mon',
                            'Phs': 'RA-ToSIB01:RF-SSAmpTower:RevBotPhs-Mon',
                            'PwrW': 'RA-ToSIB01:RF-SSAmpTower:RevBotPwrW-Mon',
                            'PwrdBm': 'RA-ToSIB01:RF-SSAmpTower:RevBotPwrdBm-Mon',
                        },
                        '180': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:RevBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:RevBotQ-Mon',
                            'Amp': 'SI-03SP:RF-SRFCav-B:RevBotAmp-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:RevBotPhs-Mon',
                            'PwrW': 'SI-03SP:RF-SRFCav-B:RevBotPwrW-Mon',
                            'PwrdBm': 'SI-03SP:RF-SRFCav-B:RevBotPwrdBm-Mon',
                        },
                        '188': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:ErrBotI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:ErrBotQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:ErrBotAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:ErrBotPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '186': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIB01:RF-LLRF:CtrlBotI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF:CtrlBotQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF:CtrlBotAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF:CtrlBotPhs-Mon',
                            'PwrW': '-',
                            'PwrdBm': '-',
                        },
                        '531': {
                            'Label': 'Ramp Trigger',
                            'PV': 'RA-RaSIB01:RF-LLRF:RmpTrigger-Mon'
                        }
                    }
                }
            }
        },
        'AutoStart': {
            'A': {
                '22': ['Automatic Startup Enable', 'RA-RaSIA01:RF-LLRF:AutoStartupEnbl'],
                '23': ['Command Start', 'RA-RaSIA01:RF-LLRF:AutoStartupCmdStart'],
                '400': ['EPS Interlock', 'RA-RaSIA01:RF-LLRF:EPSEnbl'],
                '401': ['Interlock Bypass', 'RA-RaSIA01:RF-LLRF:FIMEnbl'],
                'Diag': {
                    '500': ['State Start', 'RA-RaSIA01:RF-LLRF:AutoStartState-Mon'],
                    '400': ['Tx Ready', 'RA-RaSIA01:RF-LLRF:SSARdy-Mon'],
                    '401': ['Fast Interlock', 'RA-RaSIA01:RF-LLRF:IntlkAll-Mon'],
                    '308': ['Slow Loop Fwd Min', 'RA-RaSIA01:RF-LLRF:SLFwdMin-Mon'],
                    '309': ['Fast Loop Fwd Min', 'RA-RaSIA01:RF-LLRF:FLFwdMin-Mon'],
                    '310': ['Amp Loop Fwd Min', 'RA-RaSIA01:RF-LLRF:ALFwdMin-Mon'],
                    '311': ['Phase Loop Fwd Min', 'RA-RaSIA01:RF-LLRF:PLFwdMin-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIA01:RF-LLRF:TuneFwdMin-Mon']
                }
            },
            'B': {
                '22': ['Automatic Startup Enable', 'RA-RaSIB01:RF-LLRF:AutoStartupEnbl'],
                '23': ['Command Start', 'RA-RaSIB01:RF-LLRF:AutoStartupCmdStart'],
                '400': ['EPS Interlock', 'RA-RaSIB01:RF-LLRF:EPSEnbl'],
                '401': ['Interlock Bypass', 'RA-RaSIB01:RF-LLRF:FIMEnbl'],
                'Diag': {
                    '500': ['State Start', 'RA-RaSIB01:RF-LLRF:AutoStartState-Mon'],
                    '400': ['Tx Ready', 'RA-RaSIB01:RF-LLRF:SSARdy-Mon'],
                    '401': ['Fast Interlock', 'RA-RaSIB01:RF-LLRF:IntlkAll-Mon'],
                    '308': ['Slow Loop Fwd Min', 'RA-RaSIB01:RF-LLRF:SLFwdMin-Mon'],
                    '309': ['Fast Loop Fwd Min', 'RA-RaSIB01:RF-LLRF:FLFwdMin-Mon'],
                    '310': ['Amp Loop Fwd Min', 'RA-RaSIB01:RF-LLRF:ALFwdMin-Mon'],
                    '311': ['Phase Loop Fwd Min', 'RA-RaSIB01:RF-LLRF:PLFwdMin-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIB01:RF-LLRF:TuneFwdMin-Mon']
                }
            }
        },
        'Conditioning': {
            'A': {
                '200': ['Pulse Mode Enable', 'RA-RaSIA01:RF-LLRF:CondEnbl'],
                '201': ['Auto Conditioning Enable', 'RA-RaSIA01:RF-LLRF:CondAuto'],
                '204': ['Conditioning Freq', 'RA-RaSIA01:RF-LLRF:CondFreq'],
                '540': ['Cond Freq Diag', 'RA-RaSIA01:RF-LLRF:CondFreq-Mon'],
                '205': ['Duty Cycle', 'RA-RaSIA01:RF-LLRF:CondDuty2'],
                '530': ['Duty Cycle RB', 'RA-RaSIA01:RF-LLRF:CondDutyCycle-Mon'],
                '79': ['Vacuum', 'RA-RaSIA01:RF-LLRF:VacuumFastRly-Mon'],
            },
            'B': {
                '200': ['Pulse Mode Enable', 'RA-RaSIB01:RF-LLRF:CondEnbl'],
                '201': ['Auto Conditioning Enable', 'RA-RaSIB01:RF-LLRF:CondAuto'],
                '204': ['Conditioning Freq', 'RA-RaSIB01:RF-LLRF:CondFreq'],
                '540': ['Cond Freq Diag', 'RA-RaSIB01:RF-LLRF:CondFreq-Mon'],
                '205': ['Duty Cycle', 'RA-RaSIB01:RF-LLRF:CondDuty2'],
                '530': ['Duty Cycle RB', 'RA-RaSIB01:RF-LLRF:CondDutyCycle-Mon'],
                '79': ['Vacuum', 'RA-RaSIB01:RF-LLRF:VacuumFastRly-Mon'],
            }
        },
        'TunDtls': {
            'A': {
                'General': {
                    '34': ['Fwd Pwr Amplitude', 'RA-RaSIA01:RF-LLRF:CavFwdAmp-Mon'],
                    '19': ['Fwd Pwr Phase Angle', 'RA-RaSIA01:RF-LLRF:CavFwdPhs-Mon'],
                    '33': ['Cavity Amplitude', 'RA-RaSIA01:RF-LLRF:CavAmp-Mon'],
                    '18': ['Cavity Phase Angle', 'RA-RaSIA01:RF-LLRF:CavPhs-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIA01:RF-LLRF:TuneFwdMin-Mon'],
                    '303': ['Pulses Frequency', 'RA-RaSIA01:RF-LLRF:TuneFreq'],
                },
                'Manual': {
                    '302': ['Number of Pulses', 'RA-RaSIA01:RF-LLRF:TuneStep'],
                    '306': ['Tuner Move Dir', 'RA-RaSIA01:RF-LLRF:TunerDir'],
                    '305': ['Tuner Move', 'RA-RaSIA01:RF-LLRF:TunerMove'],
                    '307': ['Tuning Reset', 'RA-RaSIA01:RF-LLRF:TunerMove-Cmd'],
                    '302 Man': ['Tuner Manual Dn', 'SI-03SP:RF-SRFCav-A:TunerManDown-Mon'],
                    '303 Man': ['Tuner Manual Up', 'SI-03SP:RF-SRFCav-A:TunerManUp-Mon'],
                },
                'Auto': {
                    '301': ['Tuning Pos Enable', 'RA-RaSIA01:RF-LLRF:TuneDir'],
                    '309': ['Tuning Margin High', 'RA-RaSIA01:RF-LLRF:TuneMarginHI'],
                    '310': ['Tuning Margin Low', 'RA-RaSIA01:RF-LLRF:TuneMarginLO'],
                    '308': ['Tuning Forward Min', 'RA-RaSIA01:RF-LLRF:TuneFwdMin'],
                    '311': ['Tuning Delay', 'RA-RaSIA01:RF-LLRF:TuneDly'],
                    '312': ['Tuning Filter Enable', 'RA-RaSIA01:RF-LLRF:TuneFilt'],
                    '313': ['Tuning Trigger Enable', 'RA-RaSIA01:RF-LLRF:TuneTrig'],
                    '316': ['Tuning/FF On Top Ramp', 'RA-RaSIA01:RF-LLRF:RmpTuneTop'],
                },
                'Drivers': {
                    '5V': ['RA-RaSIA01:RF-CavPlDrivers:VoltPos5V-Mon', 'RA-RaSIA01:RF-CavPlDrivers:Current5V-Mon'],
                    '24V': ['RA-RaSIA01:RF-CavPlDrivers:VoltPos24V-Mon', 'RA-RaSIA01:RF-CavPlDrivers:Current24V-Mon'],
                    'Enable': 'RA-RaSIA01:RF-CavPlDrivers:DrEnbl',
                    '1': ['RA-RaSIA01:RF-CavPlDrivers:Dr1Enbl-Sts', 'RA-RaSIA01:RF-CavPlDrivers:Dr1Flt-Mon'],
                    '2': ['RA-RaSIA01:RF-CavPlDrivers:Dr2Enbl-Sts', 'RA-RaSIA01:RF-CavPlDrivers:Dr2Flt-Mon']
                }
            },
            'B': {
                'General': {
                    '34': ['Fwd Pwr Amplitude', 'RA-RaSIB01:RF-LLRF:CavFwdAmp-Mon'],
                    '19': ['Fwd Pwr Phase Angle', 'RA-RaSIB01:RF-LLRF:CavFwdPhs-Mon'],
                    '33': ['Cavity Amplitude', 'RA-RaSIB01:RF-LLRF:CavAmp-Mon'],
                    '18': ['Cavity Phase Angle', 'RA-RaSIB01:RF-LLRF:CavPhs-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIB01:RF-LLRF:TuneFwdMin-Mon'],
                    '303': ['Pulses Frequency', 'RA-RaSIB01:RF-LLRF:TuneFreq'],
                },
                'Manual': {
                    '302': ['Number of Pulses', 'RA-RaSIB01:RF-LLRF:TuneStep'],
                    '306': ['Tuner Move Dir', 'RA-RaSIB01:RF-LLRF:TunerDir'],
                    '305': ['Tuner Move', 'RA-RaSIB01:RF-LLRF:TunerMove'],
                    '307': ['Tuning Reset', 'RA-RaSIB01:RF-LLRF:TunerMove-Cmd'],
                    '302 Man': ['Tuner Manual Dn', 'SI-03SP:RF-SRFCav-B:TunerManDown-Mon'],
                    '303 Man': ['Tuner Manual Up', 'SI-03SP:RF-SRFCav-B:TunerManUp-Mon'],
                },
                'Auto': {
                    '301': ['Tuning Pos Enable', 'RA-RaSIB01:RF-LLRF:TuneDir'],
                    '309': ['Tuning Margin High', 'RA-RaSIB01:RF-LLRF:TuneMarginHI'],
                    '310': ['Tuning Margin Low', 'RA-RaSIB01:RF-LLRF:TuneMarginLO'],
                    '308': ['Tuning Forward Min', 'RA-RaSIB01:RF-LLRF:TuneFwdMin'],
                    '311': ['Tuning Delay', 'RA-RaSIB01:RF-LLRF:TuneDly'],
                    '312': ['Tuning Filter Enable', 'RA-RaSIB01:RF-LLRF:TuneFilt'],
                    '313': ['Tuning Trigger Enable', 'RA-RaSIB01:RF-LLRF:TuneTrig'],
                    '316': ['Tuning/FF On Top Ramp', 'RA-RaSIB01:RF-LLRF:RmpTuneTop'],
                },
                'Drivers': {
                    '5V': ['RA-RaSIB01:RF-CavPlDrivers:VoltPos5V-Mon', 'RA-RaSIB01:RF-CavPlDrivers:Current5V-Mon'],
                    '24V': ['RA-RaSIB01:RF-CavPlDrivers:VoltPos24V-Mon', 'RA-RaSIB01:RF-CavPlDrivers:Current24V-Mon'],
                    'Enable': 'RA-RaSIB01:RF-CavPlDrivers:DrEnbl',
                    '1': ['RA-RaSIB01:RF-CavPlDrivers:Dr1Enbl-Sts', 'RA-RaSIB01:RF-CavPlDrivers:Dr1Flt-Mon'],
                    '2': ['RA-RaSIB01:RF-CavPlDrivers:Dr2Enbl-Sts', 'RA-RaSIB01:RF-CavPlDrivers:Dr2Flt-Mon']
                }
            }
        },
        'AdvIntlk': {
            'A': {
                'Diagnostics': {
                    'General': {
                        'Manual': ['Manual Interlock', 'RA-RaSIA01:RF-LLRF:IntlkManual'],
                        'EndSw': ['End Switches', 'RA-RaSIA01:RF-LLRF:EndSwLogicInv'],
                        'Delay': 'RA-RaSIA01:RF-LLRF:IntlkDly',
                        'HW': 'RA-RaSIA01:RF-LLRF:FDLHwTrig-Mon',
                        'Beam Inv': ['Logic Inv. LLRF Beam Trip', 'RA-RaSIA01:RF-LLRF:OrbitIntlkLogicInv'],
                        'Vacuum Inv': ['Vacuum Logic Inversion', 'RA-RaSIA01:RF-LLRF:VacLogicInv']
                    },
                    'Levels': {
                        'VCav': 'RA-RaSIA01:RF-LLRF:LimCav',
                        'FwdCav': 'RA-RaSIA01:RF-LLRF:LimFwdCav',
                        'RevCav': 'RA-RaSIA01:RF-LLRF:LimRevCav',
                        'FwdSSA1': 'RA-RaSIA01:RF-LLRF:LimFwdSSA1',
                        'RevSSA1': 'RA-RaSIA01:RF-LLRF:LimRevSSA1',
                        'RevSSA2': 'RA-RaSIA01:RF-LLRF:LimRevSSA2',
                        'RevSSA3': 'RA-RaSIA01:RF-LLRF:LimRevSSA3',
                        'RevSSA4': 'RA-RaSIA01:RF-LLRF:LimRevSSA4',
                        'FwdSSA2 (RF In 7)': 'RA-RaSIA01:RF-LLRF:LimRFIn7',
                        'RevSSA2 (RF In 8)': 'RA-RaSIA01:RF-LLRF:LimRFIn8',
                        'FBTNTop (RF In 9)': 'RA-RaSIA01:RF-LLRF:LimRFIn9',
                        'WgPickup (RF In 10)': 'RA-RaSIA01:RF-LLRF:LimRFIn10',
                        'FBTNBot (RF In 11)': 'RA-RaSIA01:RF-LLRF:LimRFIn11',
                        'InpSSA1 (RF In 12)': 'RA-RaSIA01:RF-LLRF:LimRFIn12',
                        'InpSSA2 (RF In 13)': 'RA-RaSIA01:RF-LLRF:LimRFIn13',
                        'FwdCirc (RF In 14)': 'RA-RaSIA01:RF-LLRF:LimRFIn14',
                        'RevCirc (RF In 15)': 'RA-RaSIA01:RF-LLRF:LimRFIn15'
                    },
                    'GPIO': {
                        'Inp': 'RA-RaSIA01:RF-LLRF:GPIOInp-Mon',
                        'Intlk': 'RA-RaSIA01:RF-LLRF:GPIOIntlk-Mon',
                        'Out': 'RA-RaSIA01:RF-LLRF:GPIOOut-Mon'
                    }
                },
                'Bypass': {
                    '806': ['Rev SSA 1', 'RA-RaSIA01:RF-LLRF:FIMRevSSA1'],
                    '807': ['Rev SSA 2', 'RA-RaSIA01:RF-LLRF:FIMRevSSA2'],
                    '808': ['Rev SSA 3', 'RA-RaSIA01:RF-LLRF:FIMRevSSA3'],
                    '809': ['Rev SSA 4', 'RA-RaSIA01:RF-LLRF:FIMRevSSA4'],
                    '810': ['Rev Cavity', 'RA-RaSIA01:RF-LLRF:FIMRevCav'],
                    '811': ['Manual Interlock', 'RA-RaSIA01:RF-LLRF:FIMManual'],
                    '812': ['PLC', 'RA-RaSIA01:RF-LLRF:FIMPLC'],
                    '813': ['Ext LLRF 1', 'RA-RaSIA01:RF-LLRF:FIMLLRF1'],
                    '814': ['Ext LLRF 2', 'RA-RaSIA01:RF-LLRF:FIMLLRF2'],
                    '815': ['Ext LLRF 3', 'RA-RaSIA01:RF-LLRF:FIMLLRF3'],
                    '816 1': ['End Switch Up 1', 'RA-RaSIA01:RF-LLRF:FIMTunerHigh'],
                    '817 1': ['End Switch Down 1', 'RA-RaSIA01:RF-LLRF:FIMTunerLow'],
                    '816 2': ['End Switch Up 2', 'RA-RaSIA01:RF-LLRF:FIMPLG2Up'],
                    '817 2': ['End Switch Down 2', 'RA-RaSIA01:RF-LLRF:FIMPLG2Down'],
                    '853': ['Quench Condition 1', 'RA-RaSIA01:RF-LLRF:FIMQuenchCond1'],
                    '835': ['ILK VCav', 'RA-RaSIA01:RF-LLRF:FIMCav'],
                    '836': ['ILK Fwd Cav', 'RA-RaSIA01:RF-LLRF:FIMFwdCav'],
                    '837': ['ILK Fw SSA 1', 'RA-RaSIA01:RF-LLRF:FIMFwdSSA1'],
                    '838': ['ILK RF In 7', 'RA-RaSIA01:RF-LLRF:FIMRFIn7'],
                    '839': ['ILK RF In 8', 'RA-RaSIA01:RF-LLRF:FIMRFIn8'],
                    '840': ['ILK RF In 9', 'RA-RaSIA01:RF-LLRF:FIMRFIn9'],
                    '841': ['ILK RF In 10', 'RA-RaSIA01:RF-LLRF:FIMRFIn10'],
                    '842': ['ILK RF In 11', 'RA-RaSIA01:RF-LLRF:FIMRFIn11'],
                    '843': ['ILK RF In 12', 'RA-RaSIA01:RF-LLRF:FIMRFIn12'],
                    '844': ['ILK RF In 13', 'RA-RaSIA01:RF-LLRF:FIMRFIn13'],
                    '845': ['ILK RF In 14', 'RA-RaSIA01:RF-LLRF:FIMRFIn14'],
                    '846': ['ILK RF In 15', 'RA-RaSIA01:RF-LLRF:FIMRFIn15'],
                    '847': ['ILK LLRF Beam Trip', 'RA-RaSIA01:RF-LLRF:FIMOrbitIntlk']
                }
            },
            'B': {
                'Diagnostics': {
                    'General': {
                        'Manual': ['Manual Interlock', 'RA-RaSIB01:RF-LLRF:IntlkManual'],
                        'EndSw': ['End Switches', 'RA-RaSIB01:RF-LLRF:EndSwLogicInv'],
                        'Delay': 'RA-RaSIB01:RF-LLRF:IntlkDly',
                        'HW': 'RA-RaSIB01:RF-LLRF:FDLHwTrig-Mon',
                        'Beam Inv': ['Logic Inv. LLRF Beam Trip', 'RA-RaSIB01:RF-LLRF:OrbitIntlkLogicInv'],
                        'Vacuum Inv': ['Vacuum Logic Inversion', 'RA-RaSIB01:RF-LLRF:VacLogicInv']
                    },
                    'Levels': {
                        'VCav': 'RA-RaSIB01:RF-LLRF:LimCav',
                        'FwdCav': 'RA-RaSIB01:RF-LLRF:LimFwdCav',
                        'RevCav': 'RA-RaSIB01:RF-LLRF:LimRevCav',
                        'FwdSSA1': 'RA-RaSIB01:RF-LLRF:LimFwdSSA1',
                        'RevSSA1': 'RA-RaSIB01:RF-LLRF:LimRevSSA1',
                        'RevSSA2': 'RA-RaSIB01:RF-LLRF:LimRevSSA2',
                        'RevSSA3': 'RA-RaSIB01:RF-LLRF:LimRevSSA3',
                        'RevSSA4': 'RA-RaSIB01:RF-LLRF:LimRevSSA4',
                        'FwdSSA2 (RF In 7)': 'RA-RaSIB01:RF-LLRF:LimRFIn7',
                        'RevSSA2 (RF In 8)': 'RA-RaSIB01:RF-LLRF:LimRFIn8',
                        'FBTNTop (RF In 9)': 'RA-RaSIB01:RF-LLRF:LimRFIn9',
                        'WgPickup (RF In 10)': 'RA-RaSIB01:RF-LLRF:LimRFIn10',
                        'FBTNBot (RF In 11)': 'RA-RaSIB01:RF-LLRF:LimRFIn11',
                        'InpSSA1 (RF In 12)': 'RA-RaSIB01:RF-LLRF:LimRFIn12',
                        'InpSSA2 (RF In 13)': 'RA-RaSIB01:RF-LLRF:LimRFIn13',
                        'FwdCirc (RF In 14)': 'RA-RaSIB01:RF-LLRF:LimRFIn14',
                        'RevCirc (RF In 15)': 'RA-RaSIB01:RF-LLRF:LimRFIn15'
                    },
                    'GPIO': {
                        'Inp': 'RA-RaSIB01:RF-LLRF:GPIOInp-Mon',
                        'Intlk': 'RA-RaSIB01:RF-LLRF:GPIOIntlk-Mon',
                        'Out': 'RA-RaSIB01:RF-LLRF:GPIOOut-Mon'
                    }
                },
                'Bypass': {
                    '806': ['Rev SSA 1', 'RA-RaSIB01:RF-LLRF:FIMRevSSA1'],
                    '807': ['Rev SSA 2', 'RA-RaSIB01:RF-LLRF:FIMRevSSA2'],
                    '808': ['Rev SSA 3', 'RA-RaSIB01:RF-LLRF:FIMRevSSA3'],
                    '809': ['Rev SSA 4', 'RA-RaSIB01:RF-LLRF:FIMRevSSA4'],
                    '810': ['Rev Cavity', 'RA-RaSIB01:RF-LLRF:FIMRevCav'],
                    '811': ['Manual Interlock', 'RA-RaSIB01:RF-LLRF:FIMManual'],
                    '812': ['PLC', 'RA-RaSIB01:RF-LLRF:FIMPLC'],
                    '813': ['Ext LLRF 1', 'RA-RaSIB01:RF-LLRF:FIMLLRF1'],
                    '814': ['Ext LLRF 2', 'RA-RaSIB01:RF-LLRF:FIMLLRF2'],
                    '815': ['Ext LLRF 3', 'RA-RaSIB01:RF-LLRF:FIMLLRF3'],
                    '816 1': ['End Switch Up 1', 'RA-RaSIB01:RF-LLRF:FIMTunerHigh'],
                    '817 1': ['End Switch Down 1', 'RA-RaSIB01:RF-LLRF:FIMTunerLow'],
                    '816 2': ['End Switch Up 2', 'RA-RaSIB01:RF-LLRF:FIMPLG2Up'],
                    '817 2': ['End Switch Down 2', 'RA-RaSIB01:RF-LLRF:FIMPLG2Down'],
                    '853': ['Quench Condition 1', 'RA-RaSIB01:RF-LLRF:FIMQuenchCond1'],
                    '835': ['ILK VCav', 'RA-RaSIB01:RF-LLRF:FIMCav'],
                    '836': ['ILK Fwd Cav', 'RA-RaSIB01:RF-LLRF:FIMFwdCav'],
                    '837': ['ILK Fw SSA 1', 'RA-RaSIB01:RF-LLRF:FIMFwdSSA1'],
                    '838': ['ILK RF In 7', 'RA-RaSIB01:RF-LLRF:FIMRFIn7'],
                    '839': ['ILK RF In 8', 'RA-RaSIB01:RF-LLRF:FIMRFIn8'],
                    '840': ['ILK RF In 9', 'RA-RaSIB01:RF-LLRF:FIMRFIn9'],
                    '841': ['ILK RF In 10', 'RA-RaSIB01:RF-LLRF:FIMRFIn10'],
                    '842': ['ILK RF In 11', 'RA-RaSIB01:RF-LLRF:FIMRFIn11'],
                    '843': ['ILK RF In 12', 'RA-RaSIB01:RF-LLRF:FIMRFIn12'],
                    '844': ['ILK RF In 13', 'RA-RaSIB01:RF-LLRF:FIMRFIn13'],
                    '845': ['ILK RF In 14', 'RA-RaSIB01:RF-LLRF:FIMRFIn14'],
                    '846': ['ILK RF In 15', 'RA-RaSIB01:RF-LLRF:FIMRFIn15'],
                    '847': ['ILK LLRF Beam Trip', 'RA-RaSIB01:RF-LLRF:FIMOrbitIntlk']
                }
            }
        },
        'CalSys': {
            'A': {
                'Ch1': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm1-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB1-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm1-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm1-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW1-Mon'
                    },
                    'Color': 'blue'
                },
                'Ch2': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm2-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB2-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm2-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm2-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW2-Mon'
                    },
                    'Color': 'red'
                },
                'Ch3': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm3-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB3-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm3-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm3-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW3-Mon'
                    },
                    'Color': 'magenta'
                },
                'Ch4': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm4-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB4-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm4-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm4-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW4-Mon'
                    },
                    'Color': 'darkGreen'
                },
                'Ch5': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm5-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB5-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm5-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm5-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW5-Mon'
                    },
                    'Color': 'darkRed'
                },
                'Ch6': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm6-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB6-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm6-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm6-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW6-Mon'
                    },
                    'Color': 'black'
                },
                'Ch7': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm7-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB7-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm7-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm7-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW7-Mon'
                    },
                    'Color': 'darkBlue'
                },
                'Ch8': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm8-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB8-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm8-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm8-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW8-Mon'
                    },
                    'Color': 'yellow'
                },
                'Ch9': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm9-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB9-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm9-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm9-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW9-Mon'
                    },
                    'Color': 'orangered'
                },
                'Ch10': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm10-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB10-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm10-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm10-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW10-Mon'
                    },
                    'Color': 'darkOliveGreen'
                },
                'Ch11': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm11-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB11-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm11-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm11-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW11-Mon'
                    },
                    'Color': 'darkMagenta'
                },
                'Ch12': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm12-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB12-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm12-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm12-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW12-Mon'
                    },
                    'Color': 'chocolate'
                },
                'Ch13': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm13-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB13-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm13-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm13-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW13-Mon'
                    },
                    'Color': 'cyan'
                },
                'Ch14': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm14-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB14-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm14-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm14-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW14-Mon'
                    },
                    'Color': 'darkCyan'
                },
                'Ch15': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm15-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB15-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm15-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm15-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW15-Mon'
                    },
                    'Color': 'saddlebrown'
                },
                'Ch16': {
                    'Label': 'RA-RaSIA01:RF-RFCalSys:PwrdBm16-Mon.DESC',
                    'Ofs': 'RA-RaSIA01:RF-RFCalSys:OFSdB16-Mon',
                    'UnCal': 'RA-RaSIA01:RF-RFCalSys:PwrdBm16-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIA01:RF-RFCalSys:PwrdBm16-Mon',
                        'W': 'RA-RaSIA01:RF-RFCalSys:PwrW16-Mon'
                    },
                    'Color': 'darkSlateGrey'
                }
            },
            'B': {
                'Ch1': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm1-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB1-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm1-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm1-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW1-Mon'
                    },
                    'Color': 'blue'
                },
                'Ch2': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm2-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB2-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm2-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm2-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW2-Mon'
                    },
                    'Color': 'red'
                },
                'Ch3': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm3-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB3-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm3-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm3-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW3-Mon'
                    },
                    'Color': 'magenta'
                },
                'Ch4': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm4-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB4-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm4-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm4-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW4-Mon'
                    },
                    'Color': 'darkGreen'
                },
                'Ch5': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm5-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB5-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm5-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm5-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW5-Mon'
                    },
                    'Color': 'darkRed'
                },
                'Ch6': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm6-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB6-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm6-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm6-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW6-Mon'
                    },
                    'Color': 'black'
                },
                'Ch7': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm7-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB7-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm7-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm7-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW7-Mon'
                    },
                    'Color': 'darkBlue'
                },
                'Ch8': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm8-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB8-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm8-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm8-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW8-Mon'
                    },
                    'Color': 'yellow'
                },
                'Ch9': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm9-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB9-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm9-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm9-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW9-Mon'
                    },
                    'Color': 'orangered'
                },
                'Ch10': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm10-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB10-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm10-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm10-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW10-Mon'
                    },
                    'Color': 'darkOliveGreen'
                },
                'Ch11': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm11-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB11-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm11-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm11-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW11-Mon'
                    },
                    'Color': 'darkMagenta'
                },
                'Ch12': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm12-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB12-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm12-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm12-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW12-Mon'
                    },
                    'Color': 'chocolate'
                },
                'Ch13': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm13-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB13-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm13-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm13-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW13-Mon'
                    },
                    'Color': 'cyan'
                },
                'Ch14': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm14-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB14-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm14-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm14-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW14-Mon'
                    },
                    'Color': 'darkCyan'
                },
                'Ch15': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm15-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB15-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm15-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm15-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW15-Mon'
                    },
                    'Color': 'saddlebrown'
                },
                'Ch16': {
                    'Label': 'RA-RaSIB01:RF-RFCalSys:PwrdBm16-Mon.DESC',
                    'Ofs': 'RA-RaSIB01:RF-RFCalSys:OFSdB16-Mon',
                    'UnCal': 'RA-RaSIB01:RF-RFCalSys:PwrdBm16-Calc',
                    'Cal': {
                        'dBm': 'RA-RaSIB01:RF-RFCalSys:PwrdBm16-Mon',
                        'W': 'RA-RaSIB01:RF-RFCalSys:PwrW16-Mon'
                    },
                    'Color': 'darkSlateGrey'
                }
            }
        },
        'Equations': {
            'A': {
                'Cav': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:CavSysCal',
                    'U-Raw': 'RA-RaSIA01:RF-LLRF:CavSysCalInv',
                    'OFS': 'RA-RaSIA01:RF-LLRF:CavOffset'
                },
                'Fwd Cav': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:FwdCavSysCal',
                    'U-Raw': 'RA-RaSIA01:RF-LLRF:FwdCavSysCalInv',
                    'OFS': 'RA-RaSIA01:RF-LLRF:FwdCavOffset'
                },
                'Rev Cav': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:RevCavSysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:RevCavOffset'
                },
                'Fwd SSA 1': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:FwdSSA1SysCal',
                    'U-Raw': 'RA-RaSIA01:RF-LLRF:FwdSSA1SysCalInv',
                    'OFS': 'RA-RaSIA01:RF-LLRF:FwdSSA1Offset'
                },
                'Rev SSA 1': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:RevSSA1SysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:RevSSA1Offset' 
                },
                'Fwd SSA 2': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:FwdSSA2SysCal',
                    'U-Raw': 'RA-RaSIA01:RF-LLRF:FwdSSA2SysCalInv',
                    'OFS': 'RA-RaSIA01:RF-LLRF:FwdSSA2Offset'
                },
                'Rev SSA 2': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:RevSSA2SysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:RevSSA2Offset' 
                },
                'In Pre 1': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:In1PreAmpSysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:In1PreAmpOffset'
                },
                'In Pre 2': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:In2PreAmpSysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:In2PreAmpOffset'
                },
                'Fwd Circ': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:FwdCircSysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:FwdCircOffset'
                },
                'Rev Circ': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:RevCircSysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:RevCircOffset'
                },
                'MO': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:MOSysCal',
                    'OFS': 'RA-RaSIA01:RF-LLRF:MOOffset'
                },
                'Amp Loop Ref': {
                    'Raw-U': 'RA-RaSIA01:RF-LLRF:ALRefSysCal',
                    'U-Raw': 'RA-RaSIA01:RF-LLRF:ALRefSysCalInv',
                    'OFS': 'RA-RaSIA01:RF-LLRF:ALRefOffset'
                },
                'VGap': {
                    'Hw to Amp': 'RA-RaSIA01:RF-LLRF:Hw2AmpVCavCoeff',
                    'Amp to Hw': 'RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff'
                },
                'Rsh': 'SI-03SP:RF-SRFCav-A:Rsh-Cte'
            },
            'B': {
                'Cav': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:CavSysCal',
                    'U-Raw': 'RA-RaSIB01:RF-LLRF:CavSysCalInv',
                    'OFS': 'RA-RaSIB01:RF-LLRF:CavOffset'
                },
                'Fwd Cav': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:FwdCavSysCal',
                    'U-Raw': 'RA-RaSIB01:RF-LLRF:FwdCavSysCalInv',
                    'OFS': 'RA-RaSIB01:RF-LLRF:FwdCavOffset'
                },
                'Rev Cav': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:RevCavSysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:RevCavOffset'
                },
                'Fwd SSA 1': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:FwdSSA1SysCal',
                    'U-Raw': 'RA-RaSIB01:RF-LLRF:FwdSSA1SysCalInv',
                    'OFS': 'RA-RaSIB01:RF-LLRF:FwdSSA1Offset'
                },
                'Rev SSA 1': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:RevSSA1SysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:RevSSA1Offset'
                },
                'Fwd SSA 2': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:FwdSSA2SysCal',
                    'U-Raw': 'RA-RaSIB01:RF-LLRF:FwdSSA2SysCalInv',
                    'OFS': 'RA-RaSIB01:RF-LLRF:FwdSSA2Offset'
                },
                'Rev SSA 2': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:RevSSA2SysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:RevSSA2Offset' 
                },
                'In Pre 1': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:In1PreAmpSysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:In1PreAmpOffset'
                },
                'In Pre 2': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:In2PreAmpSysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:In2PreAmpOffset'
                },
                'Fwd Circ': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:FwdCircSysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:FwdCircOffset'
                },
                'Rev Circ': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:RevCircSysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:RevCircOffset'
                },
                'MO': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:MOSysCal',
                    'OFS': 'RA-RaSIB01:RF-LLRF:MOOffset'
                },
                'Amp Loop Ref': {
                    'Raw-U': 'RA-RaSIB01:RF-LLRF:ALRefSysCal',
                    'U-Raw': 'RA-RaSIB01:RF-LLRF:ALRefSysCalInv',
                    'OFS': 'RA-RaSIB01:RF-LLRF:ALRefOffset'
                },
                'VGap': {
                    'Hw to Amp': 'RA-RaSIB01:RF-LLRF:Hw2AmpVCavCoeff',
                    'Amp to Hw': 'RA-RaSIB01:RF-LLRF:AmpVCav2HwCoeff'
                },
                'Rsh': 'SI-03SP:RF-SRFCav-B:Rsh-Cte'
            }
        }
    },
}
