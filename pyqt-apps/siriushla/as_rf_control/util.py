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
            'PreDrive': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdInAmp-Mon',
            'PreDriveThrs': 4,  # mV
        },
        'SSADtls': {
            'HeatSink': {
                'Temp': 'RA-ToBO:RF-HeatSink-H0$(hs_num):T-Mon',
                'TMS': 'RA-ToBO:RF-HeatSink-H0$(hs_num):Tms-Mon'
            },
            'PreAmp': 'RA-RaBO01:RF-LLRFPreAmp:T1-Mon',
            'AC': {
                'Intlk': 'BO-ToBO:RF-ACDCPanel:Intlk-Mon',
                'Ctrl': 'BO-ToBO:RF-ACDCPanel:CtrlMode-Mon',
                '300Vdc': 'RA-ToBO:RF-ACDCPanel:300VdcEnbl-Mon',
                'Volt': 'BO-ToBO:RF-ACDCPanel:300Vdc-Mon',
                'Curr': 'BO-ToBO:RF-ACDCPanel:CurrentVdc-Mon'
            },
            'Rot': 'RA-ToBo:RF-SSAmpTower:HdFlwRt-Mon',
            'Pwr': 'RA-ToBo:RF-SSAmpTower:PwrFwdOut-Mon'
        },
        'SSACurr': {
            'HeatSink': {
                'Curr': 'RA-ToBO:RF-SSAmp-H0$(hs_num)M0$(m_num):Current$(curr_num)-Mon',
                'Fwd Top': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrFwdTop-Mon',
                'Rev Top': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrRevTop-Mon',
                'Fwd Bot': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrFwdBot-Mon',
                'Rev Bot': 'RA-ToBO:RF-HeatSink-H0$(hs_num):PwrRevBot-Mon'
            },
            'PreAmp': {
                'HS': 'RA-ToBO:RF-SSAmp-H0$(hs_num)M0$(m_num):Current$(curr_num)-Mon',
                'DC': 'RA-ToBO:RF-SSAmpTower:PwrDC-Cmd'
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
                'AInc': 'RA-RaBO01:RF-LLRF:AmpIncRate-Sp',
                'PInc': 'RA-RaBO01:RF-LLRF:PhsIncRate',
                'ARef': 'RA-RaBO01:RF-LLRF:SLRefAmp-Mon',
                'PRef': 'RA-RaBO01:RF-LLRF:SLRefPhs-Mon',
                'AInp': 'RA-RaBO01:RF-LLRF:SLInpAmp-Mon',
                'PInp': 'RA-RaBO01:RF-LLRF:SLInpPhs-Mon',
                'AErr': 'RA-RaBO01:RF-LLRF:SLErrAmp-Mon',
                'PErr': 'RA-RaBO01:RF-LLRF:SLErrPhs-Mon',
            },
            'ASet': 'RA-RaBO01:RF-LLRF:AmpVCav',
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
            'Auto': 'RA-RaBO01:RF-LLRF:FFEn',
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
                'W': 'BO-05D:RF-P5Cav:PwrCell3AmpW-Mon',
                'dBm': 'BO-05D:RF-P5Cav:PwrCell3AmpdBm-Mon',
                'mV': 'BO-05D:RF-P5Cav:PwrCell3Amp-Mon',
                'color': 'blue',
            },
            'Power Forward': {
                'W': 'BO-05D:RF-P5Cav:PwrFwdAmpW-Mon',
                'dBm': 'BO-05D:RF-P5Cav:PwrFwdAmpdBm-Mon',
                'mV': 'BO-05D:RF-P5Cav:PwrFwdAmp-Mon',
                'color': 'darkGreen',
            },
            'Power Reverse': {
                'W': 'BO-05D:RF-P5Cav:PwrRevAmpW-Mon',
                'dBm': 'BO-05D:RF-P5Cav:PwrRevAmpdBm-Mon',
                'mV': 'BO-05D:RF-P5Cav:PwrRevAmp-Mon',
                'color': 'red',
            },
        },
        'CavVGap': 'BO-05D:RF-P5Cav:PwrCell3VCav-Mon',
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
            'Mode': 'RA-RaBO:RF-LLRF:FDLMode-Mon',
            'SW Trig': 'RA-RaBO01:RF-LLRF:FDLSwTrig-Mon',
            'HW Trig': 'RA-RaBO01:RF-LLRF:FDLHwTrig-Mon',
            'Trig': 'RA-RaBO01:RF-LLRF:FDLTrig-Cmd',
            'Processing': 'RA-RaBO:RF-LLRF:FDLProcessing-Mon',
            'Rearm': 'RA-RaBO:RF-LLRF:FDLRearm-Sel',
            'Raw': 'RA-RaBO01:RF-LLRF:FDLRaw',
            'Qty': 'RA-RaBO:RF-LLRF:FDLFrame',
            'Size': 'RA-RaBO:RF-LLRF:FDLSize-Mon',
            'Duration': 'RA-RaBO:RF-LLRF:FDLDuration-Mon',
            'Delay': 'RA-RaBO:RF-LLRF:FDLTrigDly'
        },
        'ADCs and DACs': {
            'Input': {
                '0': {
                    'Label': 'Cavity Voltage (RFin1)',
                    'I': 'BO-05D:RF-P5Cav:PwrCell3I-Mon',
                    'Q': 'BO-05D:RF-P5Cav:PwrCell3Q-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:PwrCell3Amp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:PwrCell3AmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:PwrCell3AmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:PwrCell3AmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:PwrCell3Phs-Mon'
                },
                '2': {
                    'Label': 'Forward Power (RFin2)',
                    'I': 'BO-05D:RF-P5Cav:PwrFwdI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:PwrFwdQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:PwrFwdAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:PwrFwdAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:PwrFwdAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:PwrFwdAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:PwrFwdPhs-Mon'
                },
                '24': {
                    'Label': 'Rev Pwr Cavity (RFin3)',
                    'I': 'BO-05D:RF-P5Cav:PwrRevI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:PwrRevQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:PwrRevAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:PwrRevAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:PwrRevAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:PwrRevAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:PwrRevPhs-Mon'
                },
                '35': {
                    'Label': 'Master Osc (RFin4)',
                    'I': 'RA-RaMO:RF-Gen:PwrBOLLRFI-Mon',
                    'Q': 'RA-RaMO:RF-Gen:PwrBOLLRFQ-Mon',
                    'Amp1': 'RA-RaMO:RF-Gen:PwrBOLLRFAmp-Mon',
                    'Amp2': 'RA-RaMO:RF-Gen:PwrBOLLRFAmpW-Mon',
                    'Amp3': 'RA-RaMO:RF-Gen:PwrBOLLRFAmpdBm-Mon',
                    'Amp4': 'RA-RaMO:RF-Gen:PwrBOLLRFAmpVGap-Mon',
                    'Phs': 'RA-RaMO:RF-Gen:PwrBOLLRFPhs-Mon'
                },
                '20': {
                    'Label': 'Fwd Pwr SSA 1 (RFin5)',
                    'I': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutI-Mon',
                    'Q': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutQ-Mon',
                    'Amp1': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                    'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                    'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                    'Amp4': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmpVGap-Mon',
                    'Phs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                },
                '22': {
                    'Label': 'Rev Pwr SSA 1 (RFin6)',
                    'I': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutI-Mon',
                    'Q': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutQ-Mon',
                    'Amp1': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutAmp-Mon',
                    'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                    'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                    'Amp4': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutAmpVGap-Mon',
                    'Phs': 'RA-ToBO01:RF-SSAmpTower:PwrRevOutPhs-Mon'
                },
                '37': {
                    'Label': 'Cell 2 Voltage (RFin7)',
                    'I': 'BO-05D:RF-P5Cav:Cell2PwrI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell2PwrQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:Cell2PwrAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:Cell2PwrAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:Cell2PwrAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:Cell2PwrAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell2PwrPhs-Mon'
                },
                '39': {
                    'Label': 'Cell 4 Voltage (RFin8)',
                    'I': 'BO-05D:RF-P5Cav:Cell4PwrI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell4PwrQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:Cell4PwrAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:Cell4PwrAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:Cell4PwrAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:Cell4PwrAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell4PwrPhs-Mon'
                },
                '41': {
                    'Label': 'Cell 1 Voltage (RFin9)',
                    'I': 'BO-05D:RF-P5Cav:Cell1PwrI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell1PwrQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:Cell1PwrAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:Cell1PwrAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:Cell1PwrAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:Cell1PwrAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell1PwrPhs-Mon'
                },
                '43': {
                    'Label': 'Cell 5 Voltage (RFin10)',
                    'I': 'BO-05D:RF-P5Cav:Cell5PwrI-Mon',
                    'Q': 'BO-05D:RF-P5Cav:Cell5PwrQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:Cell5PwrAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:Cell5PwrAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:Cell5PwrAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:Cell5PwrAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:Cell5PwrPhs-Mon'
                },
                '45': {
                    'Label': 'Pre-Drive Input (RFin11)',
                    'I': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1I-Mon',
                    'Q': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1Q-Mon',
                    'Amp1': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1Amp-Mon',
                    'Amp2': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1AmpW-Mon',
                    'Amp3': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1AmpdBm-Mon',
                    'Amp4': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1AmpVGap-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdIn1Phs-Mon'
                },
                '47': {
                    'Label': 'Pre-Drive Output Fwd (RFin12)',
                    'I': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1I-Mon',
                    'Q': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1Q-Mon',
                    'Amp1': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1Amp-Mon',
                    'Amp2': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1AmpW-Mon',
                    'Amp3': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1AmpdBm-Mon',
                    'Amp4': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1AmpVGap-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRFPreAmp:PwrFwdOut1Phs-Mon'
                },
                '49': {
                    'Label': 'Pre-Drive Output Rev (RFin13)',
                    'I': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1I-Mon',
                    'Q': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1Q-Mon',
                    'Amp1': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1Amp-Mon',
                    'Amp2': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1AmpW-Mon',
                    'Amp3': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1AmpdBm-Mon',
                    'Amp4': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1AmpVGap-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRFPreAmp:PwrRevOut1Phs-Mon'
                },
                '51': {
                    'Label': 'Circulator Out Fwd (RFin14)',
                    'I': 'RA-TL:RF-Circulator-BO:PwrFwdOutI-Mon',
                    'Q': 'RA-TL:RF-Circulator-BO:PwrFwdOutQ-Mon',
                    'Amp1': 'RA-TL:RF-Circulator-BO:PwrFwdOutAmp-Mon',
                    'Amp2': 'RA-TL:RF-Circulator-BO:PwrFwdOutAmpW-Mon',
                    'Amp3': 'RA-TL:RF-Circulator-BO:PwrFwdOutAmpdBm-Mon',
                    'Amp4': 'RA-TL:RF-Circulator-BO:PwrFwdOutAmpVGap-Mon',
                    'Phs': 'RA-TL:RF-Circulator-BO:PwrFwdOutPhs-Mon'
                },
                '53': {
                    'Label': 'Circulator Out Rev (RFin15)',
                    'I': 'RA-TL:RF-Circulator-BO:PwrRevOutI-Mon',
                    'Q': 'RA-TL:RF-Circulator-BO:PwrRevOutQ-Mon',
                    'Amp1': 'RA-TL:RF-Circulator-BO:PwrRevOutAmp-Mon',
                    'Amp2': 'RA-TL:RF-Circulator-BO:PwrRevOutAmpW-Mon',
                    'Amp3': 'RA-TL:RF-Circulator-BO:PwrRevOutAmpdBm-Mon',
                    'Amp4': 'RA-TL:RF-Circulator-BO:PwrRevOutAmpVGap-Mon',
                    'Phs': 'RA-TL:RF-Circulator-BO:PwrRevOutPhs-Mon'
                },
                '91': {
                    'Label': 'Mux DACsIF (RFin16)',
                    'I': 'RA-RaBO01:RF-LLRF:DACIFI-Mon',
                    'Q': 'RA-RaBO01:RF-LLRF:DACIFQ-Mon',
                    'Amp1': 'RA-RaBO01:RF-LLRF:DACIFAmp-Mon',
                    'Amp2': 'RA-RaBO01:RF-LLRF:DACIFAmpW-Mon',
                    'Amp3': 'RA-RaBO01:RF-LLRF:DACIFAmpdBm-Mon',
                    'Amp4': 'RA-RaBO01:RF-LLRF:DACIFAmpVGap-Mon',
                    'Phs': 'RA-RaBO01:RF-LLRF:DACIFPhs-Mon'
                },
            },
            'Control': {
                'ADC': {
                    'Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaBO01:RF-LLRF:PhShADC'],
                    '2': ['Phase Shift Cavity', 'RA-RaBO01:RF-LLRF:PHSHCav'],
                    '3': ['Phase Shift Fwd Cav', 'RA-RaBO01:RF-LLRF:PHSHFwdCav'],
                    '8': ['Gain Fwd Cavity', 'RA-RaBO01:RF-LLRF:GainFwdCav'],
                    '4': ['Phase Shift Fwd SSA 1', 'RA-RaBO01:RF-LLRF:PHSHFwdSSA1'],
                    '9': ['Gain Fwd SSA 1', 'RA-RaBO01:RF-LLRF:GainFwdSSA1'],
                    '5': ['Phase Shift Fwd SSA 2', 'RA-RaBO01:RF-LLRF:PHSHFwdSSA2'],
                    '10': ['Gain Fwd SSA 2', 'RA-RaBO01:RF-LLRF:GainFwdSSA2'],
                    '6': ['Phase Shift Fwd SSA 3', 'RA-RaBO01:RF-LLRF:PHSHFwdSSA3'],
                    '11': ['Gain Fwd SSA 3', 'RA-RaBO01:RF-LLRF:GainFwdSSA3'],
                    '7': ['Phase Shift Fwd SSA 4', 'RA-RaBO01:RF-LLRF:PHSHFwdSSA4'],
                    '12': ['Gain Fwd SSA 4', 'RA-RaBO01:RF-LLRF:GainFwdSSA4'],
                },
                'DAC': {
                    'Enable': ['102 - DACs Phase Shift Enable', 'RA-RaBO01:RF-LLRF:PhShDAC'],
                    '14': ['Phase Shift Drive SSA 1', 'RA-RaBO01:RF-LLRF:PHSHSSA1'],
                    '18': ['Gain Drive SSA 1', 'RA-RaBO01:RF-LLRF:GainSSA1'],
                    '15': ['Phase Shift Drive SSA 2', 'RA-RaBO01:RF-LLRF:PHSHSSA2'],
                    '19': ['Gain Drive SSA 2', 'RA-RaBO01:RF-LLRF:GainSSA2'],
                    '16': ['Phase Shift Drive SSA 3', 'RA-RaBO01:RF-LLRF:PHSHSSA3'],
                    '20': ['Gain Drive SSA 3', 'RA-RaBO01:RF-LLRF:GainSSA3'],
                    '17': ['Phase Shift Drive SSA 4', 'RA-RaBO01:RF-LLRF:PHSHSSA4'],
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
            'Loop Trigger': 'RA-RaBO01:RF-LLRF:LoopTrigProc-Mon',
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
                    'InPhs': 'BO-05D:RF-P5Cav:PwrI-Mon',
                    'Quad': 'BO-05D:RF-P5Cav:PwrQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:PwrAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:PwrAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:PwrAmpdBm-Mon',
                    'Amp4': 'BO-05D:RF-P5Cav:PwrAmpVGap-Mon',
                    'Phs': 'BO-05D:RF-P5Cav:PwrPhs-Mon'
                },
                '2': {
                    'Label': 'Forward Power',
                    'InPhs': 'BO-05D:RF-P5Cav:PwrFwdI-Mon',
                    'Quad': 'BO-05D:RF-P5Cav:PwrFwdQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:PwrFwdAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:PwrFwdAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:PwrFwdAmpdBm-Mon',
                    'Amp4': '-',
                    'Phs': 'BO-05D:RF-P5Cav:PwrFwdPhs-Mon'
                },
                '20': {
                    'Label': 'Fwd Pwr SSA 1',
                    'InPhs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutI-Mon',
                    'Quad': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutQ-Mon',
                    'Amp1': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                    'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                    'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                    'Amp4': '-',
                    'Phs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                },
                '32': {
                    'Label': 'Ang Cav Fwd',
                    'InPhs': '-',
                    'Quad': '-',
                    'Amp1': '-',
                    'Amp2': '-',
                    'Amp3': '-',
                    'Amp4': '-',
                    'Phs': 'RA-RaBO01:RF-LLRF:Dephase-Mon'
                },
            },
            'Rect': {
                '30': {
                    'Label': 'Fwd Pwr SSA 2',
                    'InPhs': 'BO-05D:RF-P5Cav:PwrFBTNTopI-Mon',
                    'Quad': 'BO-05D:RF-P5Cav:PwrFBTNTopQ-Mon',
                    'Amp1': 'BO-05D:RF-P5Cav:PwrFBTNTopAmp-Mon',
                    'Amp2': 'BO-05D:RF-P5Cav:PwrFBTNTopAmpW-Mon',
                    'Amp3': 'BO-05D:RF-P5Cav:PwrFBTNTopAmpdBm-Mon',
                    'Amp4': '-',
                    'Phs': 'BO-05D:RF-P5Cav:PwrFBTNTopPhs-Mon'
                },
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
                        'InPhs': 'RA-RaBO01:RF-LLRF:SSA1CtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SSA1CtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SSA1CtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SSA1CtrlPhs-Mon'
                    },
                    '8': {
                        'Label': 'SSA 2 Control Signal',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SSA2CtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SSA2CtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SSA2CtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SSA2CtrlPhs-Mon'
                    }
                }
            },
            'Polar': {
                '527': {
                    'Label': 'Amp Ref',
                    'InPhs': '-',
                    'Quad': '-',
                    'Amp1': 'RA-RaBO01:RF-LLRF:AmpRefOld-Mon',
                    'Amp2': '-',
                    'Amp3': '-',
                    'Amp4': '-',
                    'Phs': '-'
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
                        'InPhs': 'RA-RaBO01:RF-LLRF:SSA1CtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SSA1CtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SSA1CtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SSA1CtrlPhs-Mon'
                    },
                    '8': {
                        'Label': 'SSA 2 Control Signal',
                        'InPhs': 'RA-RaBO01:RF-LLRF:SSA2CtrlI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:SSA2CtrlQ-Mon',
                        'Amp': 'RA-RaBO01:RF-LLRF:SSA2CtrlAmp-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:SSA2CtrlPhs-Mon'
                    }
                }
            },
            'Equations': {
                'Cav': {
                    'Raw-U': 'RA-RaBO01:RF-LLRF:CavSysCal',
                    'U-Raw': 'RA-RaBO01:RF-LLRF:CavSysCalInv',
                    'OLG': 'RA-RaBO01:RF-LLRF:CavSysCalOLG',
                    'OFS': 'RA-RaBO01:RF-LLRF:CavOffset'
                },
                'Fwd Cav': {
                    'Raw-U': 'RA-RaBO01:RF-LLRF:FwdCavSysCal',
                    'U-Raw': 'RA-RaBO01:RF-LLRF:FwdCavSysCalInv',
                    'OLG': 'RA-RaBO01:RF-LLRF:FwdCavSysCalOLG',
                    'OFS': 'RA-RaBO01:RF-LLRF:FwdCavOffset'
                },
                'Rev Cav': {
                    'Raw-U': 'RA-RaBO01:RF-LLRF:RevCavSysCal',
                    'OFS': 'RA-RaBO01:RF-LLRF:RevCavOffset'
                },
                'Fwd SSA 1': {
                    'Raw-U': 'RA-RaBO01:RF-LLRF:FwdSSA1SysCal',
                    'U-Raw': 'RA-RaBO01:RF-LLRF:FwdSSA1SysCalInv',
                    'OLG': 'RA-RaBO01:RF-LLRF:FwdSSA1SysCalOLG',
                    'OFS': 'RA-RaBO01:RF-LLRF:FwdSSA1SysCalOffset'
                },
                'Rev SSA 1': {
                    'Raw-U': 'RA-RaBO01:RF-LLRF:RevSSA1SysCal',
                    'OFS': 'RA-RaBO01:RF-LLRF:RevSSA1Offset' 
                },
                'Fwd SSA 2': {
                    'Raw-U': 'RA-RaBO01:RF-LLRF:FwdSSA2SysCal',
                    'U-Raw': 'RA-RaBO01:RF-LLRF:FwdSSA2SysCalInv',
                    'OLG': 'RA-RaBO01:RF-LLRF:FwdSSA2SysCalOLG',
                    'OFS': 'RA-RaBO01:RF-LLRF:FwdSSA2SysCalOffset'
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
                    'Raw-U': 'RA-RaBO01:RF-LLRF:Cell3SysCal',
                    'OFS': 'RA-RaBO01:RF-LLRF:Cell3Offset'
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
        'RampDtls': {
            'Control': {
                'Ramp Enable': 'RA-RaBO01:RF-LLRF:RmpEn',
                'Ramp Down Disable': 'RA-RaBO01:RF-LLRF:RampDownDsbl',
                '356': ['T1 Ramp Delay After Trig', 'RA-RaBO01:RF-LLRF:RmpTs1'],
                '357': ['T2 Ramp Up', 'RA-RaBO01:RF-LLRF:RmpTs2'],
                '358': ['T3 Ramp Top', 'RA-RaBO01:RF-LLRF:RmpTs3'],
                '359': ['T4 Ramp Down', 'RA-RaBO01:RF-LLRF:RmpTs4'],
                '360': ['Ramp Increase Rate', 'RA-RaBO01:RF-LLRF:RmpIncTime'],
                '164': ['Ref Top', 'RA-RaBO01:RF-LLRF:RefTopAmp-Mon', 'red'],
                '362 mV': ['Amp Ramp Top (mV)', 'RA-RaBO01:RF-LLRF:RampAmpTop'],
                '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-RaBO01:RF-LLRF:RampAmpTopVGap'],
                '364': ['Phase Ramp Top', 'RA-RaBO01:RF-LLRF:RampPhsTop'],
                '184': ['Ref Bot', 'RA-RaBO01:RF-LLRF:RefBotAmp-Mon', 'blue'],
                '361 mV': ['Amp Ramp Bot (mV)', 'RA-RaBO01:RF-LLRF:RampAmpBot'],
                '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-RaBO01:RF-LLRF:RampAmpBotVGap'],
                '363': ['Phase Ramp Bot', 'RA-RaBO01:RF-LLRF:RampPhsBot'],
                '536': ['Ramp Top', 'RA-RaBO01:RF-LLRF:RampTop-Mon', 'green'],
                '533': ['Ramp Ready', 'RA-RaBO01:RF-LLRF:RampRdy-Mon'],
                '365': ['Amp Ramp Up Slope', 'RA-RaBO01:RF-LLRF:RampAmpUpCnt'],
                '366': ['Amp Ramp Down Slope', 'RA-RaBO01:RF-LLRF:RampAmpDownCnt'],
                '367': ['Phase Ramp Up Slope', 'RA-RaBO01:RF-LLRF:RampPhsUpCnt'],
                '368': ['Phase Ramp Down Slope', 'RA-RaBO01:RF-LLRF:RampPhsDownCnt'],
                'Limits': {
                    '362': ['Top Reference', 'RA-RaBO01:RF-LLRF:RampAmpTop'],
                    '361': ['Bot Reference', 'RA-RaBO01:RF-LLRF:RampAmpBot']
                }
            },
            'Diagnostics': {
                'Top': {
                    '164': {
                        'Label': 'Ref',
                        'InPhs': 'RA-RaBO01:RF-LLRF:RefTopI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:RefTopQ-Mon',
                        'Amp1': 'RA-RaBO01:RF-LLRF:RefTopAmp-Mon',
                        'Amp2': 'RA-RaBO01:RF-LLRF:RefTopAmpW-Mon',
                        'Amp3': 'RA-RaBO01:RF-LLRF:RefTopAmpdBm-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:RefTopPhs-Mon'
                    },
                    '150': {
                        'Label': 'Cell 3',
                        'InPhs': 'BO-05D:RF-P5Cav:PwrTopI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:PwrTopQ-Mon',
                        'Amp1': 'BO-05D:RF-P5Cav:PwrTopAmp-Mon',
                        'Amp2': 'BO-05D:RF-P5Cav:PwrTopAmpW-Mon',
                        'Amp3': 'BO-05D:RF-P5Cav:PwrTopAmpdBm-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:PwrTopPhs-Mon'
                    },
                    '152': {
                        'Label': 'Cell 2',
                        'InPhs': 'RA-ToBO02:RF-SSAmpTower:PwrFwdTopI-Mon',
                        'Quad': 'RA-ToBO02:RF-SSAmpTower:PwrFwdTopQ-Mon',
                        'Amp1': 'RA-ToBO02:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                        'Amp2': 'RA-ToBO02:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                        'Amp3': 'RA-ToBO02:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                        'Phs': 'RA-ToBO02:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                    },
                    '154': {
                        'Label': 'Cell 4',
                        'InPhs': 'RA-ToBO02:RF-SSAmpTower:PwrRevTopI-Mon',
                        'Quad': 'RA-ToBO02:RF-SSAmpTower:PwrRevTopQ-Mon',
                        'Amp1': 'RA-ToBO02:RF-SSAmpTower:PwrRevTopAmp-Mon',
                        'Amp2': 'RA-ToBO02:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                        'Amp3': 'RA-ToBO02:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                        'Phs': 'RA-ToBO02:RF-SSAmpTower:PwrRevTopPhs-Mon'
                    },
                    '190': {
                        'Label': 'Fwd Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:PwrFwdTopI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:PwrFwdTopQ-Mon',
                        'Amp1': 'BO-05D:RF-P5Cav:PwrFwdTopAmp-Mon',
                        'Amp2': 'BO-05D:RF-P5Cav:PwrFwdTopAmpW-Mon',
                        'Amp3': 'BO-05D:RF-P5Cav:PwrFwdTopAmpdBm-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:PwrFwdTopPhs-Mon'
                    },
                    '156': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdTopI-Mon',
                        'Quad': 'RA-ToBO01:RF-SSAmpTower:PwrFwdTopQ-Mon',
                        'Amp1': 'RA-ToBO01:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                        'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                        'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                        'Phs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                    },
                    '158': {
                        'Label': 'Rev Pwr SSA 1',
                        'InPhs':  'RA-ToBO01:RF-SSAmpTower:PwrRevTopI-Mon',
                        'Quad':  'RA-ToBO01:RF-SSAmpTower:PwrRevTopQ-Mon',
                        'Amp1':  'RA-ToBO01:RF-SSAmpTower:PwrRevTopAmp-Mon',
                        'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                        'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                        'Phs':  'RA-ToBO01:RF-SSAmpTower:PwrRevTopPhs-Mon'
                    },
                    '160': {
                        'Label': 'Rev Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:PwrRevTopI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:PwrRevTopQ-Mon',
                        'Amp1': 'BO-05D:RF-P5Cav:PwrRevTopAmp-Mon',
                        'Amp2': 'BO-05D:RF-P5Cav:PwrRevTopAmpW-Mon',
                        'Amp3': 'BO-05D:RF-P5Cav:PwrRevTopAmpdBm-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:PwrRevTopPhs-Mon'
                    },
                    '168': {
                        'Label': 'Loop Error',
                        'InPhs': 'RA-RaBO01:RF-LLRF:ErrTopI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:ErrTopQ-Mon',
                        'Amp1': 'RA-RaBO01:RF-LLRF:ErrTopAmp-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:ErrTopPhs-Mon'
                    },
                    '166': {
                        'Label': 'Control',
                        'InPhs': 'RA-RaBO01:RF-LLRF:CtrlTopI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:CtrlTopQ-Mon',
                        'Amp1': 'RA-RaBO01:RF-LLRF:CtrlTopAmp-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:CtrlTopPhs-Mon'
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
                        'Label': '5 Hz Trigger',
                        'PV': 'RA-RaBO01:RF-LLRF:RampTrigger-Mon'
                    }
                },
                'Bot': {
                    '184': {
                        'Label': 'Ref',
                        'InPhs': 'RA-RaBO01:RF-LLRF:RefBotI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:RefBotQ-Mon',
                        'Amp1': 'RA-RaBO01:RF-LLRF:RefBotAmp-Mon',
                        'Amp2': 'RA-RaBO01:RF-LLRF:RefBotAmpW-Mon',
                        'Amp3': 'RA-RaBO01:RF-LLRF:RefBotAmpdBm-Mon',
                        'Phs': 'RA-RaBO01:RF-LLRF:RefBotPhs-Mon'
                    },
                    '170': {
                        'Label': 'Cell 3',
                        'InPhs': 'BO-05D:RF-P5Cav:PwrBotI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:PwrBotQ-Mon',
                        'Amp1': 'BO-05D:RF-P5Cav:PwrBotAmp-Mon',
                        'Amp2': 'BO-05D:RF-P5Cav:PwrBotAmpW-Mon',
                        'Amp3': 'BO-05D:RF-P5Cav:PwrBotAmpdBm-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:PwrBotPhs-Mon'
                    },
                    '172': {
                        'Label': 'Cell 2',
                        'InPhs': 'RA-ToBO02:RF-SSAmpTower:PwrFwdBotI-Mon',
                        'Quad': 'RA-ToBO02:RF-SSAmpTower:PwrFwdBotQ-Mon',
                        'Amp1': 'RA-ToBO02:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                        'Amp2': 'RA-ToBO02:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                        'Amp3': 'RA-ToBO02:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                        'Phs': 'RA-ToBO02:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                    },
                    '174': {
                        'Label': 'Cell 4',
                        'InPhs': 'RA-ToBO02:RF-SSAmpTower:PwrRevBotI-Mon',
                        'Quad': 'RA-ToBO02:RF-SSAmpTower:PwrRevBotQ-Mon',
                        'Amp1': 'RA-ToBO02:RF-SSAmpTower:PwrRevBotAmp-Mon',
                        'Amp2': 'RA-ToBO02:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                        'Amp3': 'RA-ToBO02:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                        'Phs': 'RA-ToBO02:RF-SSAmpTower:PwrRevBotPhs-Mon'
                    },
                    '192': {
                        'Label': 'Fwd Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:PwrFwdBotI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:PwrFwdBotQ-Mon',
                        'Amp1': 'BO-05D:RF-P5Cav:PwrFwdBotAmp-Mon',
                        'Amp2': 'BO-05D:RF-P5Cav:PwrFwdBotAmpW-Mon',
                        'Amp3': 'BO-05D:RF-P5Cav:PwrFwdBotAmpdBm-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:PwrFwdBotPhs-Mon'
                    },
                    '176': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdBotI-Mon',
                        'Quad': 'RA-ToBO01:RF-SSAmpTower:PwrFwdBotQ-Mon',
                        'Amp1': 'RA-ToBO01:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                        'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                        'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                        'Phs': 'RA-ToBO01:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                    },
                    '178': {
                        'Label': 'Rev Pwr SSA 1',
                        'InPhs': 'RA-ToBO01:RF-SSAmpTower:PwrRevBotI-Mon',
                        'Quad': 'RA-ToBO01:RF-SSAmpTower:PwrRevBotQ-Mon',
                        'Amp1': 'RA-ToBO01:RF-SSAmpTower:PwrRevBotAmp-Mon',
                        'Amp2': 'RA-ToBO01:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                        'Amp3': 'RA-ToBO01:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                        'Phs': 'RA-ToBO01:RF-SSAmpTower:PwrRevBotPhs-Mon'
                    },
                    '180': {
                        'Label': 'Rev Cavity',
                        'InPhs': 'BO-05D:RF-P5Cav:PwrRevBotI-Mon',
                        'Quad': 'BO-05D:RF-P5Cav:PwrRevBotQ-Mon',
                        'Amp1': 'BO-05D:RF-P5Cav:PwrRevBotAmp-Mon',
                        'Amp2': 'BO-05D:RF-P5Cav:PwrRevBotAmpW-Mon',
                        'Amp3': 'BO-05D:RF-P5Cav:PwrRevBotAmpdBm-Mon',
                        'Phs': 'BO-05D:RF-P5Cav:PwrRevBotPhs-Mon'
                    },
                    '188': {
                        'Label': 'Loop Error',
                        'InPhs': 'RA-RaBO01:RF-LLRF:ErrBotI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:ErrBotQ-Mon',
                        'Amp1': 'RA-RaBO01:RF-LLRF:ErrBotAmp-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:ErrBotPhs-Mon'
                    },
                    '186': {
                        'Label': 'Control',
                        'InPhs': 'RA-RaBO01:RF-LLRF:CtrlBotI-Mon',
                        'Quad': 'RA-RaBO01:RF-LLRF:CtrlBotQ-Mon',
                        'Amp1': 'RA-RaBO01:RF-LLRF:CtrlBotAmp-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Phs': 'RA-RaBO01:RF-LLRF:CtrlBotPhs-Mon'
                    },
                    '183': {
                        'Label': 'FF Error',
                        'PV': 'RA-RaBO01:RF-LLRF:FFErrBot-Mon'
                    },
                    '531': {
                        'Label': '5 Hz Trigger',
                        'PV': 'RA-RaBO01:RF-LLRF:RampTrigger-Mon'
                    }
                }
            }
        },
        'AutoStart': {
            '22': ['Automatic Startup Enable', 'RA-RaBO01:RF-LLRF:AutoStartupEn'],
            '23': ['Command Start', 'RA-RaBO01:RF-LLRF:AutoStartupCmdStart'],
            '400': ['EPS Interlock', 'RA-RaBO01:RF-LLRF:EPSEn'],
            '401': ['Interlock Bypass', 'RA-RaBO01:RF-LLRF:FIMEn'],
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
            '200': ['Pulse Mode Enable', 'RA-RaBO01:RF-LLRF:CondEn'],
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
                '316': ['Tuning/FF On Top Ramp', 'RA-RaBO01:RF-LLRF:RampTuneTop'],
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
                    'RevSSA1': 'RA-RaBO01:RF-LLRF:LimRevSSA1',
                    'RevSSA2': 'RA-RaBO01:RF-LLRF:LimRevSSA2',
                    'RevSSA3': 'RA-RaBO01:RF-LLRF:LimRevSSA3',
                    'RevSSA4': 'RA-RaBO01:RF-LLRF:LimRevSSA4',
                    'RevCav': 'RA-RaBO01:RF-LLRF:LimRevCav',
                    'VCav': 'RA-RaBO01:RF-LLRF:LimCav',
                    'FwCav': 'RA-RaBO01:RF-LLRF:LimFwdCav',
                    'FwSSA1': 'RA-RaBO01:RF-LLRF:LimFwdSSA1',
                    'RF In 7': 'RA-RaBO01:RF-LLRF:LimRefIn7',
                    'RF In 8': 'RA-RaBO01:RF-LLRF:LimRefIn8',
                    'RF In 9': 'RA-RaBO01:RF-LLRF:LimRefIn9',
                    'RF In 10': 'RA-RaBO01:RF-LLRF:LimRefIn10',
                    'RF In 11': 'RA-RaBO01:RF-LLRF:LimRefIn11',
                    'RF In 12': 'RA-RaBO01:RF-LLRF:LimRefIn12',
                    'RF In 13': 'RA-RaBO01:RF-LLRF:LimRefIn13',
                    'RF In 14': 'RA-RaBO01:RF-LLRF:LimRefIn14',
                    'RF In 15': 'RA-RaBO01:RF-LLRF:LimRefIn15'
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
        }
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
                            '0': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk0-Mon',
                            '1': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk1-Mon',
                            '2': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk2-Mon',
                            '3': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk3-Mon',
                            '4': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk4-Mon',
                            '5': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk5-Mon',
                            '6': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk6-Mon',
                            '7': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk7-Mon',
                            'Mon': 'RA-RaSIA01:RF-LLRF-A:Inp1Intlk-Mon',
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
                            '0': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk0-Mon',
                            '1': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk1-Mon',
                            '2': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk2-Mon',
                            '3': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk3-Mon',
                            '4': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk4-Mon',
                            '5': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk5-Mon',
                            '6': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk6-Mon',
                            '7': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk7-Mon',
                            'Mon': 'RA-RaSIA01:RF-LLRF-A:Inp2Intlk-Mon',
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
                    '1': 'RA-RaSIA01:RF-LLRF-A:IntlkTs1-Mon',
                    '2': 'RA-RaSIA01:RF-LLRF-A:IntlkTs2-Mon',
                    '3': 'RA-RaSIA01:RF-LLRF-A:IntlkTs3-Mon',
                    '4': 'RA-RaSIA01:RF-LLRF-A:IntlkTs4-Mon',
                    '5': 'RA-RaSIA01:RF-LLRF-A:IntlkTs5-Mon',
                    '6': 'RA-RaSIA01:RF-LLRF-A:IntlkTs6-Mon',
                    '7': 'RA-RaSIA01:RF-LLRF-A:IntlkTs7-Mon',
                }
            },
            'B': {
                'Inputs': {
                    'Input': {
                        'Status': {
                            '0': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk0-Mon',
                            '1': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk1-Mon',
                            '2': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk2-Mon',
                            '3': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk3-Mon',
                            '4': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk4-Mon',
                            '5': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk5-Mon',
                            '6': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk6-Mon',
                            '7': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk7-Mon',
                            'Mon': 'RA-RaSIB01:RF-LLRF-B:Inp1Intlk-Mon',
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
                            '0': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk0-Mon',
                            '1': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk1-Mon',
                            '2': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk2-Mon',
                            '3': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk3-Mon',
                            '4': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk4-Mon',
                            '5': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk5-Mon',
                            '6': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk6-Mon',
                            '7': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk7-Mon',
                            'Mon': 'RA-RaSIB01:RF-LLRF-B:Inp2Intlk-Mon',
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
                    '1': 'RA-RaSIB01:RF-LLRF-B:IntlkTs1-Mon',
                    '2': 'RA-RaSIB01:RF-LLRF-B:IntlkTs2-Mon',
                    '3': 'RA-RaSIB01:RF-LLRF-B:IntlkTs3-Mon',
                    '4': 'RA-RaSIB01:RF-LLRF-B:IntlkTs4-Mon',
                    '5': 'RA-RaSIB01:RF-LLRF-B:IntlkTs5-Mon',
                    '6': 'RA-RaSIB01:RF-LLRF-B:IntlkTs6-Mon',
                    '7': 'RA-RaSIB01:RF-LLRF-B:IntlkTs7-Mon',
                }
            }
        },
        'Reset': {
            'Global': 'RA-RaSIA02:RF-Intlk:Reset-Cmd',
            'A': 'RA-RaSIA01:RF-LLRF-A:IntlkReset-Cmd',
            'B': 'RA-RaSIB01:RF-LLRF-B:IntlkReset-Cmd',
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
                'Cond': 'RA-RaSIA01:RF-LLRF-A:VacuumFastRly-Mon',
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
                    'Circulator In Reflected Power': 'RA-TLSIB:RF-Circulator:PwrRevIndBm-Mon',
                    'Combiner': 'RA-TLSIB:RF-Combiner:T-Mon'
                },
                'led': {
                    'Circulator Arc Detector': 'RA-TLSIB:RF-Circulator:Arc-Mon',
                    'Circulator Arc Detector Supply Fail': 'RA-RaSIB02:RF-ArcDetec-Circ:PwrFail-Mon',
                    'Arc Detector Load': 'RA-TLSIB:RF-Load:Arc-Mon',
                    'Arc Detector Load Supply Fail': 'RA-RaSIB02:RF-ArcDetec-Load:PwrFail-Mon',
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
                'Power': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIA01:RF-ACPanel:PwrACEnbl-Cmd',
                    'Disable': 'RA-ToSIA01:RF-ACPanel:PwrACDsbl-Cmd',
                    'Mon': 'RA-ToSIA01:RF-ACPanel:PwrAC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIA01:RF-TDKSource:PwrDCEnbl-Cmd',
                    'Disable': 'RA-ToSIA01:RF-TDKSource:PwrDCDsbl-Cmd',
                    'Mon': 'RA-ToSIA01:RF-TDKSource:PwrDC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIA01:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIA01:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIA01:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:PwrFwdIn1Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'A'
            },
            '2': {
                'Name': 'SSA 02',
                'Status': 'RA-ToSIA02:RF-SSAmpTower:Sts-Mon',
                'Power': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOut-Mon',
                'SRC 1': {
                    'Label': 'AC TDK',
                    'Enable': 'RA-ToSIA02:RF-ACPanel:PwrACEnbl-Cmd',
                    'Disable': 'RA-ToSIA02:RF-ACPanel:PwrACDsbl-Cmd',
                    'Mon': 'RA-ToSIA02:RF-ACPanel:PwrAC-Mon'
                },
                'SRC 2': {
                    'Label': 'DC TDK',
                    'Enable': 'RA-ToSIA02:RF-TDKSource:PwrDCEnbl-Cmd',
                    'Disable': 'RA-ToSIA02:RF-TDKSource:PwrDCDsbl-Cmd',
                    'Mon': 'RA-ToSIA02:RF-TDKSource:PwrDC-Mon'
                },
                'PinSw': {
                    'Label': 'PinSw',
                    'Enable': 'RA-ToSIA02:RF-CtrlPanel:PINSwEnbl-Cmd',
                    'Disable': 'RA-ToSIA02:RF-CtrlPanel:PINSwDsbl-Cmd',
                    'Mon': 'RA-ToSIA02:RF-CtrlPanel:PINSwSts-Mon'
                },
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:PwrFwdIn2Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'A'
            },
            '3': {
                'Name': 'SSA 03',
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
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:PwrFwdIn3Amp-Mon',
                'PreDriveThrs': 5,  # mV
                'LLRF': 'B'
            },
            '4': {
                'Name': 'SSA 04',
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
                'PreDrive': 'RA-RaSIA01:RF-LLRFPreAmp:PwrFwdIn4Amp-Mon',
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
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrFwdIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwPwrFwdIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrFwdInSts-Mon'
                ],
                'In Pwr Rev': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrRevIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwPwrRevIn-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrRevInSts-Mon'
                ],
                'Out Pwr Fwd': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrFwdOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwPwrFwdOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrFwdOutSts-Mon'
                ],
                'Out Pwr Rev': [
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrRevOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:HwPwrRevOut-Mon',
                    'RA-ToSIA0$(NB):RF-SSAmpTower:PwrRevOutSts-Mon'
                ],
                'Alerts': {
                    'PhsFlt': ['Phase Fault', 'RA-ToSIA0$(NB):RF-ACPanel:PhsFlt-Mon'],
                    'SSAFlwRt': ['SSA Rotameter Flow', 'RA-ToSIA0$(NB):RF-SSAmpTower:HdFlwRt-Mon'],
                    'LoadFlwRt': ['Load Rotameter Flow', 'RA-ToSIA0$(NB):RF-WaterLoad:HdFlwRt-Mon'],
                    'PnlFeed': ['AC Panel Feedback', 'RA-ToSIA0$(NB):RF-ACPanel:Intlk-Mon'],
                    'PnlIntlk': ['AC Panel Interlock', 'RA-ToSIA0$(NB):RF-Intlk:IntlkACPanel-Mon'],
                    'PnlSts': ['AC Panel Status', 'RA-ToSIA0$(NB):RF-ACPanel:PwrACOp-Mon'],
                    'ElecFuse': ['Electronic Fuse', 'RA-ToSIA0$(NB):RF-CtrlPanel:PwrSts-Mon'],
                    'PwrSup': ['24V Power Supply', 'RA-ToSIA0$(NB):RF-ACPanel:StsPos24V-Mon'],
                    'PwrIntlk': ['RF Power Interlock', 'RA-ToSIA0$(NB):RF-SSAmpTower:RFPwrSts-Mon'],
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
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrFwdIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwPwrFwdIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrFwdInSts-Mon'
                ],
                'In Pwr Rev': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrRevIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwPwrRevIn-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrRevInSts-Mon'
                ],
                'Out Pwr Fwd': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrFwdOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwPwrFwdOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrFwdOutSts-Mon'
                ],
                'Out Pwr Rev': [
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrRevOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:HwPwrRevOut-Mon',
                    'RA-ToSIB0$(NB):RF-SSAmpTower:PwrRevOutSts-Mon'
                ],
                'Alerts': {
                    'PhsFlt': ['Phase Fault', 'RA-ToSIB0$(NB):RF-ACPanel:PhsFlt-Mon'],
                    'SSAFlwRt': ['SSA Rotameter Flow', 'RA-ToSIB0$(NB):RF-SSAmpTower:HdFlwRt-Mon'],
                    'LoadFlwRt': ['Load Rotameter Flow', 'RA-ToSIB0$(NB):RF-WaterLoad:HdFlwRt-Mon'],
                    'PnlFeed': ['AC Panel Feedback', 'RA-ToSIB0$(NB):RF-ACPanel:Intlk-Mon'],
                    'PnlIntlk': ['AC Panel Interlock', 'RA-ToSIB0$(NB):RF-Intlk:IntlkACPanel-Mon'],
                    'PnlSts': ['AC Panel Status', 'RA-ToSIB0$(NB):RF-ACPanel:PwrACOp-Mon'],
                    'ElecFuse': ['Electronic Fuse', 'RA-ToSIB0$(NB):RF-CtrlPanel:PwrSts-Mon'],
                    'PwrSup': ['24V Power Supply', 'RA-ToSIB0$(NB):RF-ACPanel:StsPos24V-Mon'],
                    'PwrIntlk': ['RF Power Interlock', 'RA-ToSIB0$(NB):RF-SSAmpTower:RFPwrSts-Mon'],
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
                    'TDK': 'RA-ToSIA0$(NB):RF-SSAmpTower:PwrDCR1-Mon'
                },
                'Offsets': {
                    'FwdPwrTop': ['Forward Power - Top', 'RA-ToSIA0$(NB):OffsetConfig:UpperIncidentPower'],
                    'RevPwrTop': ['Reverse Power - Top', 'RA-ToSIA0$(NB):OffsetConfig:UpperReflectedPower'],
                    'FwdPwrBot': ['Forward Power - Bottom', 'RA-ToSIA0$(NB):OffsetConfig:LowerIncidentPower'],
                    'RevPwrBot': ['Reverse Power - Bottom', 'RA-ToSIA0$(NB):OffsetConfig:LowerReflectedPower'],
                },
                'RacksTotal': 'RA-ToSIA0$(NB):RF-SSAMux-$(rack_num):DCCurrent-Mon',
                'Alarms': {
                    'General': {
                        'Label': 'General Power',
                        'HIHI': 'RA-ToSIA0$(NB):AlarmConfig:GeneralPowerLimHiHi',
                        'HIGH': 'RA-ToSIA0$(NB):AlarmConfig:GeneralPowerLimHigh',
                        'LOW': 'RA-ToSIA0$(NB):AlarmConfig:GeneralPowerLimLow',
                        'LOLO': 'RA-ToSIA0$(NB):AlarmConfig:GeneralPowerLimLoLo',
                    },
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
                    'TDK': 'RA-ToSIB0$(NB):RF-SSAmpTower:PwrDCR1-Mon'
                },
                'Offsets': {
                    'FwdPwrTop': ['Forward Power - Top', 'RA-ToSIB0$(NB):OffsetConfig:UpperIncidentPower'],
                    'RevPwrTop': ['Reverse Power - Top', 'RA-ToSIB0$(NB):OffsetConfig:UpperReflectedPower'],
                    'FwdPwrBot': ['Forward Power - Bottom', 'RA-ToSIB0$(NB):OffsetConfig:LowerIncidentPower'],
                    'RevPwrBot': ['Reverse Power - Bottom', 'RA-ToSIB0$(NB):OffsetConfig:LowerReflectedPower'],
                },
                'RacksTotal': 'RA-ToSIB0$(NB):RF-SSAMux-$(rack_num):DCCurrent-Mon',
                'Alarms': {
                    'General': {
                        'Label': 'General Power',
                        'HIHI': 'RA-ToSIB0$(NB):AlarmConfig:GeneralPowerLimHiHi',
                        'HIGH': 'RA-ToSIB0$(NB):AlarmConfig:GeneralPowerLimHigh',
                        'LOW': 'RA-ToSIB0$(NB):AlarmConfig:GeneralPowerLimLow',
                        'LOLO': 'RA-ToSIB0$(NB):AlarmConfig:GeneralPowerLimLoLo',
                    },
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
                    'IRef': 'RA-RaSIA01:RF-LLRF-A:SLRefI-Mon',
                    'QRef': 'RA-RaSIA01:RF-LLRF-A:SLRefQ-Mon',
                    'IInp': 'RA-RaSIA01:RF-LLRF-A:SLInpI-Mon',
                    'QInp': 'RA-RaSIA01:RF-LLRF-A:SLInpQ-Mon',
                    'IErr': 'RA-RaSIA01:RF-LLRF-A:SLErrorI-Mon',
                    'QErr': 'RA-RaSIA01:RF-LLRF-A:SLErrorQ-Mon',
                },
                'B': {
                    'IRef': 'RA-RaSIB01:RF-LLRF-B:SLRefI-Mon',
                    'QRef': 'RA-RaSIB01:RF-LLRF-B:SLRefQ-Mon',
                    'IInp': 'RA-RaSIB01:RF-LLRF-B:SLInpI-Mon',
                    'QInp': 'RA-RaSIB01:RF-LLRF-B:SLInpQ-Mon',
                    'IErr': 'RA-RaSIB01:RF-LLRF-B:SLErrorI-Mon',
                    'QErr': 'RA-RaSIB01:RF-LLRF-B:SLErrorQ-Mon',
                },
            },
            'Params': {
                'A': {
                    'Inp': 'RA-RaSIA01:RF-LLRF-A:SLInp',
                    'PIL': 'RA-RaSIA01:RF-LLRF-A:SLPILim',
                    'KI': 'RA-RaSIA01:RF-LLRF-A:SLKI',
                    'KP': 'RA-RaSIA01:RF-LLRF-A:SLKP',
                },
                'B': {
                    'Inp': 'RA-RaSIB01:RF-LLRF-B:SLInp',
                    'PIL': 'RA-RaSIB01:RF-LLRF-B:SLPILim',
                    'KI': 'RA-RaSIB01:RF-LLRF-B:SLKI',
                    'KP': 'RA-RaSIB01:RF-LLRF-B:SLKP',
                },
            },
            'Over': {
                'A': {
                    'Enbl': 'RA-RaSIA01:RF-LLRF-A:SL',
                    'Mode': 'RA-RaSIA01:RF-LLRF-A:LoopMode',
                    'ASet': 'RA-RaSIA01:RF-LLRF-A:ALRef',
                    'AInc': 'RA-RaSIA01:RF-LLRF-A:AmpIncRate',
                    'PSet': 'RA-RaSIA01:RF-LLRF-A:PLRef',
                    'PInc': 'RA-RaSIA01:RF-LLRF-A:PhsIncRate',
                    'ARef': 'RA-RaSIA01:RF-LLRF-A:SLRefAmp-Mon',
                    'PRef': 'RA-RaSIA01:RF-LLRF-A:SLRefPhs-Mon',
                    'AInp': 'RA-RaSIA01:RF-LLRF-A:SLInpAmp-Mon',
                    'PInp': 'RA-RaSIA01:RF-LLRF-A:SLInpPhs-Mon',
                    'AErr': 'RA-RaSIA01:RF-LLRF-A:SLErrAmp-Mon',
                    'PErr': 'RA-RaSIA01:RF-LLRF-A:SLErrPhs-Mon',
                },
                'B': {
                    'Enbl': 'RA-RaSIB01:RF-LLRF-B:SL',
                    'Mode': 'RA-RaSIB01:RF-LLRF-B:LoopMode',
                    'ASet': 'RA-RaSIB01:RF-LLRF-B:ALRef',
                    'AInc': 'RA-RaSIB01:RF-LLRF-B:AmpIncRate',
                    'PSet': 'RA-RaSIB01:RF-LLRF-B:PLRef',
                    'PInc': 'RA-RaSIB01:RF-LLRF-B:PhsIncRate',
                    'ARef': 'RA-RaSIB01:RF-LLRF-B:SLRefAmp-Mon',
                    'PRef': 'RA-RaSIB01:RF-LLRF-B:SLRefPhs-Mon',
                    'AInp': 'RA-RaSIB01:RF-LLRF-B:SLInpAmp-Mon',
                    'PInp': 'RA-RaSIB01:RF-LLRF-B:SLInpPhs-Mon',
                    'AErr': 'RA-RaSIB01:RF-LLRF-B:SLErrAmp-Mon',
                    'PErr': 'RA-RaSIB01:RF-LLRF-B:SLErrPhs-Mon',
                },
            },
            'ASet': {
                'A': 'RA-RaSIA01:RF-LLRF-A:AmpVCav',
                'B': 'RA-RaSIB01:RF-LLRF-B:AmpVCav',
            },
        },
        'Tun': {
            'A': {
                'Auto': 'RA-RaSIA01:RF-LLRF-A:Tune',
                'DTune': 'RA-RaSIA01:RF-LLRF-A:Detune',
                'DPhase': 'RA-RaSIA01:RF-LLRF-A:TuneDephs-Mon',
                'Acting': 'RA-RaSIA01:RF-LLRF-A:TuneOut-Mon',
                'Deadbnd': 'RA-RaSIA01:RF-LLRF-A:TuneMarginHI',
                'Oversht': 'RA-RaSIA01:RF-LLRF-A:TuneMarginLO',
                'Pl1Down': 'SI-03SP:RF-SRFCav-A:TunnerMoveDown-Mon',
                'Pl1Up': 'SI-03SP:RF-SRFCav-A:TunnerMoveUp-Mon',
                'PlM1Curr': 'RA-RaSIA01:RF-CavPlDrivers:Dr1Current-Mon',
                'color': 'blue'
            },
            'B': {
                'Auto': 'RA-RaSIB01:RF-LLRF-B:Tune',
                'DTune': 'RA-RaSIB01:RF-LLRF-B:Detune',
                'DPhase': 'RA-RaSIB01:RF-LLRF-B:TuneDephs-Mon',
                'Acting': 'RA-RaSIB01:RF-LLRF-B:TuneOut-Mon',
                'Deadbnd': 'RA-RaSIB01:RF-LLRF-B:TuneMarginHI',
                'Oversht': 'RA-RaSIB01:RF-LLRF-B:TuneMarginLO',
                'Pl1Down': 'SI-03SP:RF-SRFCav-B:TunnerMoveDown-Mon',
                'Pl1Up': 'SI-03SP:RF-SRFCav-B:TunnerMoveUp-Mon',
                'PlM1Curr': 'RA-RaSIB01:RF-CavPlDrivers:Dr1Current-Mon',
                'color': 'red'
            }
        },
        'PwrMtr': {
            'A - Fwd SSA 1': {
                'mV': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                'dBm': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                'W': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                'color': 'blue'
            },
            'A - Rev SSA 1': {
                'mV': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutAmp-Mon',
                'dBm': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                'W': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                'color': 'red'
            },
            'A - Fwd SSA 2': {
                'mV': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                'dBm': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                'W': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                'color': 'magenta'
            },
            'A - Rev SSA 2': {
                'mV': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutAmp-Mon',
                'dBm': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                'W': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                'color': 'darkGreen'
            },
            'A - Cav': {
                'mV': 'SI-03SP:RF-SRFCav-A:PwrAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-A:PwrAmpdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-A:PwrAmpW-Mon',
                'color': 'darkRed'
            },
            'A - Fwd Cav': {
                'mV': 'SI-03SP:RF-SRFCav-A:PwrFwdAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpW-Mon',
                'color': 'black'
            },
            'A - Rev Cav': {
                'mV': 'SI-03SP:RF-SRFCav-A:PwrRevAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-A:PwrRevAmpdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-A:PwrRevAmpW-Mon',
                'color': 'darkBlue'
            },
            'A - Fwd Circulator': {
                'mV': 'RA-TL:RF-Circulator-SIA:PwrFwdOutAmp-Mon',
                'dBm': 'RA-TL:RF-Circulator-SIA:PwrFwdOutAmpdBm-Mon',
                'W': 'RA-TL:RF-Circulator-SIA:PwrFwdOutAmpW-Mon',
                'color': 'yellow'
            },
            'B - Fwd SSA 3': {
                'mV': 'RA-ToSIA03:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                'dBm': 'RA-ToSIA03:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                'W': 'RA-ToSIA03:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                'color': 'orangered'
            },
            'B - Rev SSA 3': {
                'mV': 'RA-ToSIA03:RF-SSAmpTower:PwrRevOutAmp-Mon',
                'dBm': 'RA-ToSIA03:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                'W': 'RA-ToSIA03:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                'color': 'darkOliveGreen'
            },
            'B - Fwd SSA 4': {
                'mV': 'RA-ToSIA04:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                'dBm': 'RA-ToSIA04:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                'W': 'RA-ToSIA04:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                'color': 'darkMagenta'
            },
            'B - Rev SSA 4': {
                'mV': 'RA-ToSIA04:RF-SSAmpTower:PwrRevOutAmp-Mon',
                'dBm': 'RA-ToSIA04:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                'W': 'RA-ToSIA04:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                'color': 'chocolate'
            },
            'B - Cav': {
                'mV': 'SI-03SP:RF-SRFCav-B:PwrAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-B:PwrAmpdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-B:PwrAmpW-Mon',
                'color': 'cyan'
            },
            'B - Fwd Cav': {
                'mV': 'SI-03SP:RF-SRFCav-B:PwrFwdAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpW-Mon',
                'color': 'darkCyan'
            },
            'B - Rev Cav': {
                'mV': 'SI-03SP:RF-SRFCav-B:PwrRevAmp-Mon',
                'dBm': 'SI-03SP:RF-SRFCav-B:PwrRevAmpdBm-Mon',
                'W': 'SI-03SP:RF-SRFCav-B:PwrRevAmpW-Mon',
                'color': 'saddlebrown'
            },
            'B - Fwd Circulator': {
                'mV': 'RA-TL:RF-Circulator-SIB:PwrFwdOutAmp-Mon',
                'dBm': 'RA-TL:RF-Circulator-SIB:PwrFwdOutAmpdBm-Mon',
                'W': 'RA-TL:RF-Circulator-SIB:PwrFwdOutAmpW-Mon',
                'color': 'darkSlateGrey'
            },
        },
        'CavVGap': {
            'A': 'SI-03SP:RF-SRFCav-A:PwrVCav-Mon',
            'B': 'SI-03SP:RF-SRFCav-B:PwrVCav-Mon'
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
                    'Cell 1': 'SI-03SP:RF-P7Cav:PwrDissCell1-Mon',
                    'Cell 2': 'SI-03SP:RF-P7Cav:PwrDissCell2-Mon',
                    'Cell 3': 'SI-03SP:RF-P7Cav:PwrDissCell3-Mon',
                    'Cell 4': 'SI-03SP:RF-P7Cav:PwrDissCell4-Mon',
                    'Cell 5': 'SI-03SP:RF-P7Cav:PwrDissCell5-Mon',
                    'Cell 6': 'SI-03SP:RF-P7Cav:PwrDissCell6-Mon',
                    'Cell 7': 'SI-03SP:RF-P7Cav:PwrDissCell7-Mon',
                },
                'Discs': {
                    'Disc 1': 'SI-03SP:RF-P7Cav:PwrDissDisc1-Mon',
                    'Disc 2': 'SI-03SP:RF-P7Cav:PwrDissDisc2-Mon',
                    'Disc 3': 'SI-03SP:RF-P7Cav:PwrDissDisc3-Mon',
                    'Disc 4': 'SI-03SP:RF-P7Cav:PwrDissDisc4-Mon',
                    'Disc 5': 'SI-03SP:RF-P7Cav:PwrDissDisc5-Mon',
                    'Disc 6': 'SI-03SP:RF-P7Cav:PwrDissDisc6-Mon',
                    'Disc 7': 'SI-03SP:RF-P7Cav:PwrDissDisc7-Mon',
                    'Disc 8': 'SI-03SP:RF-P7Cav:PwrDissDisc8-Mon',
                },
            },
            'Power (Water)': {
                'Cell 1': 'SI-03SP:RF-P7Cav:PwrWtCell1-Mon',
                'Cell 2': 'SI-03SP:RF-P7Cav:PwrWtCell2-Mon',
                'Cell 3': 'SI-03SP:RF-P7Cav:PwrWtCell3-Mon',
                'Cell 4': 'SI-03SP:RF-P7Cav:PwrWtCell4-Mon',
                'Cell 5': 'SI-03SP:RF-P7Cav:PwrWtCell5-Mon',
                'Cell 6': 'SI-03SP:RF-P7Cav:PwrWtCell6-Mon',
                'Cell 7': 'SI-03SP:RF-P7Cav:PwrWtCell7-Mon',
                # 'Total': 'SI-03SP:RF-P7Cav:PwrWtTotal-Mon',
                # 'Fwd': 'RA-RaSIA01:RF-RFCalSys:PwrW2-Mon',
            },
        },
        'FDL': {
            'A': {
                'Signals': (
                    ('Cav', 'RA-RaSIA01:RF-LLRF-A:FDLCavAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLCavPhs-Mon', 'blue'),
                    ('Fwd Cav', 'RA-RaSIA01:RF-LLRF-A:FDLCavFwdAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLCavFwdPhs-Mon', 'red'),
                    ('Rev Cav', 'RA-RaSIA01:RF-LLRF-A:FDLCavRevAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLCavRevPhs-Mon', 'darkSlateBlue'),
                    ('Fwd Ssa', 'RA-RaSIA01:RF-LLRF-A:FDLFwdSSAAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLFwdSSAPhs-Mon', 'darkGreen'),
                    ('Rev Ssa', 'RA-RaSIA01:RF-LLRF-A:FDLRevSSAAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLRevSSAPhs-Mon', 'magenta'),
                    ('Ctrl', 'RA-RaSIA01:RF-LLRF-A:FDLCtrlAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLCtrlPhs-Mon', 'darkCyan'),
                    ('Ref', 'RA-RaSIA01:RF-LLRF-A:FDLSLRefAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLSLRefPhs-Mon', 'darkRed'),
                    ('Err', 'RA-RaSIA01:RF-LLRF-A:FDLSLErrAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLSLErrPhs-Mon', 'purple'),
                    ('Err Acc', 'RA-RaSIA01:RF-LLRF-A:FDLSLErrAccAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLSLErrAccPhs-Mon', 'saddlebrown'),
                    ('MO', 'RA-RaSIA01:RF-LLRF-A:FDLMOAmp-Mon', 'RA-RaSIA01:RF-LLRF-A:FDLMOPhs-Mon', 'darkBlue'),
                    ('Tune', None, 'RA-RaSIA01:RF-LLRF-A:FDLTuneDephs-Mon', 'orangered'),
                    ('Tune Filt', None, 'RA-RaSIA01:RF-LLRF-A:FDLTuneDephsFilt-Mon', 'darkOliveGreen')
                ),
                'Time': 'RA-RaSIA01:RF-LLRF-A:FDLScale32-Mon',
                'Mode': 'RA-RaSIA01:RF-LLRF-A:FDLMode-Mon',
                'SW Trig': 'RA-RaSIA01:RF-LLRF-A:FDLSwTrig-Mon',
                'HW Trig': 'RA-RaSIA01:RF-LLRF-A:FDLHwTrig-Mon',
                'Trig': 'RA-RaSIA01:RF-LLRF-A:FDLTrig-Cmd',
                'Processing': 'RA-RaSIA01:RF-LLRF-A:FDLProcessing-Mon',
                'Rearm': 'RA-RaSIA01:RF-LLRF-A:FDLRearm-Sel',
                'Raw': 'RA-RaSIA01:RF-LLRF-A:FDLRaw',
                'Qty': 'RA-RaSIA01:RF-LLRF-A:FDLFrame',
                'Size': 'RA-RaSIA01:RF-LLRF-A:FDLSize-Mon',
                'Duration': 'RA-RaSIA01:RF-LLRF-A:FDLDuration-Mon',
                'Delay': 'RA-RaSIA01:RF-LLRF-A:FDLTrigDly',
                'Name': 'A',
            },
            'B': {
                'Signals': (
                    ('Cav', 'RA-RaSIB01:RF-LLRF-B:FDLCavAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLCavPhs-Mon', 'blue'),
                    ('Fwd Cav', 'RA-RaSIB01:RF-LLRF-B:FDLCavFwdAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLCavFwdPhs-Mon', 'red'),
                    ('Rev Cav', 'RA-RaSIB01:RF-LLRF-B:FDLCavRevAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLCavRevPhs-Mon', 'darkSlateBlue'),
                    ('Fwd Ssa', 'RA-RaSIB01:RF-LLRF-B:FDLFwdSSAAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLFwdSSAPhs-Mon', 'darkGreen'),
                    ('Rev Ssa', 'RA-RaSIB01:RF-LLRF-B:FDLRevSSAAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLRevSSAPhs-Mon', 'magenta'),
                    ('Ctrl', 'RA-RaSIB01:RF-LLRF-B:FDLCtrlAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLCtrlPhs-Mon', 'darkCyan'),
                    ('Ref', 'RA-RaSIB01:RF-LLRF-B:FDLSLRefAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLSLRefPhs-Mon', 'darkRed'),
                    ('Err', 'RA-RaSIB01:RF-LLRF-B:FDLSLErrAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLSLErrPhs-Mon', 'purple'),
                    ('Err Acc', 'RA-RaSIB01:RF-LLRF-B:FDLSLErrAccAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLSLErrAccPhs-Mon', 'saddlebrown'),
                    ('MO', 'RA-RaSIB01:RF-LLRF-B:FDLMOAmp-Mon', 'RA-RaSIB01:RF-LLRF-B:FDLMOPhs-Mon', 'darkBlue'),
                    ('Tune', None, 'RA-RaSIB01:RF-LLRF-B:FDLTuneDephs-Mon', 'orangered'),
                    ('Tune Filt', None, 'RA-RaSIB01:RF-LLRF-B:FDLTuneDephsFilt-Mon', 'darkOliveGreen')
                ),
                'Time': 'RA-RaSIB01:RF-LLRF-B:FDLScale32-Mon',
                'Mode': 'RA-RaSIB01:RF-LLRF-B:FDLMode-Mon',
                'SW Trig': 'RA-RaSIB01:RF-LLRF-B:FDLSwTrig-Mon',
                'HW Trig': 'RA-RaSIB01:RF-LLRF-B:FDLHwTrig-Mon',
                'Trig': 'RA-RaSIB01:RF-LLRF-B:FDLTrig-Cmd',
                'Processing': 'RA-RaSIB01:RF-LLRF-B:FDLProcessing-Mon',
                'Rearm': 'RA-RaSIB01:RF-LLRF-B:FDLRearm-Sel',
                'Raw': 'RA-RaSIB01:RF-LLRF-B:FDLRaw',
                'Qty': 'RA-RaSIB01:RF-LLRF-B:FDLFrame',
                'Size': 'RA-RaSIB01:RF-LLRF-B:FDLSize-Mon',
                'Duration': 'RA-RaSIB01:RF-LLRF-B:FDLDuration-Mon',
                'Delay': 'RA-RaSIB01:RF-LLRF-B:FDLTrigDly',
                'Name': 'B'
            }
        },
        'ADCs and DACs': {
            'A': {
                'Input': {
                    '0': {
                        'Label': 'Cavity Voltage (RFin1)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrAmpdBm-Mon',
                        'Amp4': 'SI-03SP:RF-SRFCav-A:PwrAmpVGap-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrPhs-Mon'
                    },
                    '2': {
                        'Label': 'Forward Power (RFin2)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrFwdI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrFwdQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFwdAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpdBm-Mon',
                        'Amp4': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpVGap-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrFwdPhs-Mon'
                    },
                    '24': {
                        'Label': 'Rev Pwr Cavity (RFin3)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrRevI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrRevQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrRevAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrRevAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrRevAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrRevPhs-Mon'
                    },
                    '35': {
                        'Label': 'Master Osc (RFin4)',
                        'I': 'RA-RaMO:RF-Gen:PwrSIALLRFI-Mon',
                        'Q': 'RA-RaMO:RF-Gen:PwrSIALLRFQ-Mon',
                        'Amp1': 'RA-RaMO:RF-Gen:PwrSIALLRFAmp-Mon',
                        'Amp2': 'RA-RaMO:RF-Gen:PwrSIALLRFAmpW-Mon',
                        'Amp3': 'RA-RaMO:RF-Gen:PwrSIALLRFAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-RaMO:RF-Gen:PwrSIALLRFPhs-Mon'
                    },
                    '20': {
                        'Label': 'Fwd Pwr SSA 1 (RFin5)',
                        'I': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutI-Mon',
                        'Q': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutQ-Mon',
                        'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                        'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                        'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                        'Amp4': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpVGap-Mon',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                    },
                    '22': {
                        'Label': 'Rev Pwr SSA 1 (RFin6)',
                        'I': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutI-Mon',
                        'Q': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutQ-Mon',
                        'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutAmp-Mon',
                        'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                        'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrRevOutPhs-Mon'
                    },
                    '37': {
                        'Label': 'Cell 2 Voltage (RFin7)',
                        'I': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutI-Mon',
                        'Q': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutQ-Mon',
                        'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                        'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                        'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                    },
                    '39': {
                        'Label': 'Cell 6 Voltage (RFin8)',
                        'I': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutI-Mon',
                        'Q': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutQ-Mon',
                        'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutAmp-Mon',
                        'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                        'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrRevOutPhs-Mon'
                    },
                    '41': {
                        'Label': 'Fwd Pwr SSA 2 (RFin9)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopPhs-Mon'
                    },
                    '43': {
                        'Label': 'Rev Pwr SSA 2 (RFin10)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrWgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrWgPkupQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrWgPkupAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrWgPkupAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrWgPkupAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrWgPkupPhs-Mon'
                    },
                    '45': {
                        'Label': 'Pre-Drive Input 1 (RFin11)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrFBTNBotI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrFBTNBotQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFBTNBotAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFBTNBotAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFBTNBotAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrFBTNBotPhs-Mon'
                    },
                    '47': {
                        'Label': 'Pre-Drive Out Fwd 1 (RFin12)',
                        'I': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdInI-Mon',
                        'Q': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdInQ-Mon',
                        'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdInAmp-Mon',
                        'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdInAmpW-Mon',
                        'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdInAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdInPhs-Mon'
                    },
                    '49': {
                        'Label': 'Pre-Drive Input 2 (RFin13)',
                        'I': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdInI-Mon',
                        'Q': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdInQ-Mon',
                        'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdInAmp-Mon',
                        'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdInAmpW-Mon',
                        'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdInAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdInPhs-Mon'
                    },
                    '51': {
                        'Label': 'Pre-Drive Out Fwd 2 (RFin14)',
                        'I': 'SI-03SP:RF-SRFCav-A:PwrWgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-A:PwrWgPkupQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrWgPkupAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrWgPkupAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrWgPkupAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrWgPkupPhs-Mon'
                    },
                    '53': {
                        'Label': 'Circulator Out Rev (RFin15)',
                        'I': 'RA-TL:RF-Circulator-SIA:PwrRevOutI-Mon',
                        'Q': 'RA-TL:RF-Circulator-SIA:PwrRevOutQ-Mon',
                        'Amp1': 'RA-TL:RF-Circulator-SIA:PwrRevOutAmp-Mon',
                        'Amp2': 'RA-TL:RF-Circulator-SIA:PwrRevOutAmpW-Mon',
                        'Amp3': 'RA-TL:RF-Circulator-SIA:PwrRevOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-TL:RF-Circulator-SIA:PwrRevOutPhs-Mon'
                    },
                    '91': {
                        'Label': 'Mux DACsIF (RFin16)',
                        'I': 'RA-RaSIA01:RF-LLRF-A:DACIFI-Mon',
                        'Q': 'RA-RaSIA01:RF-LLRF-A:DACIFQ-Mon',
                        'Amp1': 'RA-RaSIA01:RF-LLRF-A:DACIFAmp-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': 'RA-RaSIA01:RF-LLRF-A:DACIFPhs-Mon'
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'I': '-',
                        'Q': '-',
                        'Amp1': '-',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': 'RA-RaSIA01:RF-LLRF-A:Dephase-Mon'
                    }
                },
                'Control': {
                    'ADC': {
                        'Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaSIA01:RF-LLRF-A:PhShADC'],
                        '2': ['Phase Shift Cavity', 'RA-RaSIA01:RF-LLRF-A:PHSHCav'],
                        '3': ['Phase Shift Fwd Cav', 'RA-RaSIA01:RF-LLRF-A:PHSHFwdCav'],
                        '8': ['Gain Fwd Cavity', 'RA-RaSIA01:RF-LLRF-A:GainFwdCav'],
                        '4': ['Phase Shift Fwd SSA 1', 'RA-RaSIA01:RF-LLRF-A:PHSHFwdSSA1'],
                        '9': ['Gain Fwd SSA 1', 'RA-RaSIA01:RF-LLRF-A:GainFwdSSA1'],
                        '5': ['Phase Shift Fwd SSA 2', 'RA-RaSIA01:RF-LLRF-A:PHSHFwdSSA2'],
                        '10': ['Gain Fwd SSA 2', 'RA-RaSIA01:RF-LLRF-A:GainFwdSSA2'],
                        '6': ['Phase Shift Fwd SSA 3', 'RA-RaSIA01:RF-LLRF-A:PHSHFwdSSA3'],
                        '11': ['Gain Fwd SSA 3', 'RA-RaSIA01:RF-LLRF-A:GainFwdSSA3'],
                        '7': ['Phase Shift Fwd SSA 4', 'RA-RaSIA01:RF-LLRF-A:PHSHFwdSSA4'],
                        '12': ['Gain Fwd SSA 4', 'RA-RaSIA01:RF-LLRF-A:GainFwdSSA4'],
                    },
                    'DAC': {
                        'Enable': ['102 - DACs Phase Shift Enable', 'RA-RaSIA01:RF-LLRF-A:PhShDAC'],
                        '14': ['Phase Shift Drive SSA 1', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA1'],
                        '18': ['Gain Drive SSA 1', 'RA-RaSIA01:RF-LLRF-A:GainSSA1'],
                        '15': ['Phase Shift Drive SSA 2', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA2'],
                        '19': ['Gain Drive SSA 2', 'RA-RaSIA01:RF-LLRF-A:GainSSA2'],
                        '16': ['Phase Shift Drive SSA 3', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA3'],
                        '20': ['Gain Drive SSA 3', 'RA-RaSIA01:RF-LLRF-A:GainSSA3'],
                        '17': ['Phase Shift Drive SSA 4', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA4'],
                        '21': ['Gain Drive SSA 4', 'RA-RaSIA01:RF-LLRF-A:GainSSA4']
                    }
                },
            },
            'B': {
                'Input': {
                    '0': {
                        'Label': 'Cavity Voltage (RFin1)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrAmpdBm-Mon',
                        'Amp4': 'SI-03SP:RF-SRFCav-B:PwrAmpVGap-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrPhs-Mon'
                    },
                    '2': {
                        'Label': 'Forward Power (RFin2)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrFwdI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrFwdQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFwdAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpdBm-Mon',
                        'Amp4': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpVGap-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrFwdPhs-Mon'
                    },
                    '24': {
                        'Label': 'Rev Pwr Cavity (RFin3)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrRevI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrRevQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrRevAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrRevAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrRevAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrRevPhs-Mon'
                    },
                    '35': {
                        'Label': 'Master Osc (RFin4)',
                        'I': 'RA-RaMO:RF-Gen:PwrSIBLLRFI-Mon',
                        'Q': 'RA-RaMO:RF-Gen:PwrSIBLLRFQ-Mon',
                        'Amp1': 'RA-RaMO:RF-Gen:PwrSIBLLRFAmp-Mon',
                        'Amp2': 'RA-RaMO:RF-Gen:PwrSIBLLRFAmpW-Mon',
                        'Amp3': 'RA-RaMO:RF-Gen:PwrSIBLLRFAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-RaMO:RF-Gen:PwrSIBLLRFPhs-Mon'
                    },
                    '20': {
                        'Label': 'Fwd Pwr SSA 1 (RFin5)',
                        'I': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutI-Mon',
                        'Q': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutQ-Mon',
                        'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                        'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                        'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                        'Amp4': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmpVGap-Mon',
                        'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                    },
                    '22': {
                        'Label': 'Rev Pwr SSA 1 (RFin6)',
                        'I': 'RA-ToSIB01:RF-SSAmpTower:PwrRevOutI-Mon',
                        'Q': 'RA-ToSIB01:RF-SSAmpTower:PwrRevOutQ-Mon',
                        'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrRevOutAmp-Mon',
                        'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                        'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrRevOutPhs-Mon'
                    },
                    '37': {
                        'Label': 'Cell 2 Voltage (RFin7)',
                        'I': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdOutI-Mon',
                        'Q': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdOutQ-Mon',
                        'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                        'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                        'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                    },
                    '39': {
                        'Label': 'Cell 6 Voltage (RFin8)',
                        'I': 'RA-ToSIB02:RF-SSAmpTower:PwrRevOutI-Mon',
                        'Q': 'RA-ToSIB02:RF-SSAmpTower:PwrRevOutQ-Mon',
                        'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrRevOutAmp-Mon',
                        'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrRevOutAmpW-Mon',
                        'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrRevOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrRevOutPhs-Mon'
                    },
                    '41': {
                        'Label': 'Fwd Pwr SSA 2 (RFin9)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopPhs-Mon'
                    },
                    '43': {
                        'Label': 'Rev Pwr SSA 2 (RFin10)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrWgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrWgPkupQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrWgPkupAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrWgPkupAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrWgPkupAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrWgPkupPhs-Mon'
                    },
                    '45': {
                        'Label': 'Pre-Drive Input 1 (RFin11)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrFBTNBotI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrFBTNBotQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFBTNBotAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFBTNBotAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFBTNBotAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrFBTNBotPhs-Mon'
                    },
                    '47': {
                        'Label': 'Pre-Drive Out Fwd 1 (RFin12)',
                        'I': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdInI-Mon',
                        'Q': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdInQ-Mon',
                        'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdInAmp-Mon',
                        'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdInAmpW-Mon',
                        'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdInAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdInPhs-Mon'
                    },
                    '49': {
                        'Label': 'Pre-Drive Input 2 (RFin13)',
                        'I': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdInI-Mon',
                        'Q': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdInQ-Mon',
                        'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdInAmp-Mon',
                        'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdInAmpW-Mon',
                        'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdInAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdInPhs-Mon'
                    },
                    '51': {
                        'Label': 'Pre-Drive Out Fwd 2 (RFin14)',
                        'I': 'SI-03SP:RF-SRFCav-B:PwrWgPkupI-Mon',
                        'Q': 'SI-03SP:RF-SRFCav-B:PwrWgPkupQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrWgPkupAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrWgPkupAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrWgPkupAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrWgPkupPhs-Mon'
                    },
                    '53': {
                        'Label': 'Circulator Out Rev (RFin15)',
                        'I': 'RA-TL:RF-Circulator-SIB:PwrRevOutI-Mon',
                        'Q': 'RA-TL:RF-Circulator-SIB:PwrRevOutQ-Mon',
                        'Amp1': 'RA-TL:RF-Circulator-SIB:PwrRevOutAmp-Mon',
                        'Amp2': 'RA-TL:RF-Circulator-SIB:PwrRevOutAmpW-Mon',
                        'Amp3': 'RA-TL:RF-Circulator-SIB:PwrRevOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-TL:RF-Circulator-SIB:PwrRevOutPhs-Mon'
                    },
                    '91': {
                        'Label': 'Mux DACsIF (RFin16)',
                        'I': 'RA-RaSIB01:RF-LLRF-B:DACIFI-Mon',
                        'Q': 'RA-RaSIB01:RF-LLRF-B:DACIFQ-Mon',
                        'Amp1': 'RA-RaSIB01:RF-LLRF-B:DACIFAmp-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': 'RA-RaSIB01:RF-LLRF-B:DACIFPhs-Mon'
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'I': '-',
                        'Q': '-',
                        'Amp1': '-',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': 'RA-RaSIB01:RF-LLRF-B:Dephase-Mon'
                    }
                },
                'Control': {
                    'ADC': {
                        'Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaSIB01:RF-LLRF-B:PhShADC'],
                        '2': ['Phase Shift Cavity', 'RA-RaSIB01:RF-LLRF-B:PHSHCav'],
                        '3': ['Phase Shift Fwd Cav', 'RA-RaSIB01:RF-LLRF-B:PHSHFwdCav'],
                        '8': ['Gain Fwd Cavity', 'RA-RaSIB01:RF-LLRF-B:GainFwdCav'],
                        '4': ['Phase Shift Fwd SSA 1', 'RA-RaSIB01:RF-LLRF-B:PHSHFwdSSA1'],
                        '9': ['Gain Fwd SSA 1', 'RA-RaSIB01:RF-LLRF-B:GainFwdSSA1'],
                        '5': ['Phase Shift Fwd SSA 2', 'RA-RaSIB01:RF-LLRF-B:PHSHFwdSSA2'],
                        '10': ['Gain Fwd SSA 2', 'RA-RaSIB01:RF-LLRF-B:GainFwdSSA2'],
                        '6': ['Phase Shift Fwd SSA 3', 'RA-RaSIB01:RF-LLRF-B:PHSHFwdSSA3'],
                        '11': ['Gain Fwd SSA 3', 'RA-RaSIB01:RF-LLRF-B:GainFwdSSA3'],
                        '7': ['Phase Shift Fwd SSA 4', 'RA-RaSIB01:RF-LLRF-B:PHSHFwdSSA4'],
                        '12': ['Gain Fwd SSA 4', 'RA-RaSIB01:RF-LLRF-B:GainFwdSSA4'],
                    },
                    'DAC': {
                        'Enable': ['102 - DACs Phase Shift Enable', 'RA-RaSIB01:RF-LLRF-B:PhShDAC'],
                        '14': ['Phase Shift Drive SSA 1', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA1'],
                        '18': ['Gain Drive SSA 1', 'RA-RaSIB01:RF-LLRF-B:GainSSA1'],
                        '15': ['Phase Shift Drive SSA 2', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA2'],
                        '19': ['Gain Drive SSA 2', 'RA-RaSIB01:RF-LLRF-B:GainSSA2'],
                        '16': ['Phase Shift Drive SSA 3', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA3'],
                        '20': ['Gain Drive SSA 3', 'RA-RaSIB01:RF-LLRF-B:GainSSA3'],
                        '17': ['Phase Shift Drive SSA 4', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA4'],
                        '21': ['Gain Drive SSA 4', 'RA-RaSIB01:RF-LLRF-B:GainSSA4']
                    }
                }
            }
        },
        'Hardware': {
            'A': {
                'FPGA': {
                    'Temp': 'RA-RaSIA01:RF-LLRF-A:FPGATemp-Mon',
                    'Temp Max': 'RA-RaSIA01:RF-LLRF-A:FPGATempMax-Mon',
                    'Temp Min': 'RA-RaSIA01:RF-LLRF-A:FPGATempMin-Mon',
                    'Vint': 'RA-RaSIA01:RF-LLRF-A:FPGAVint-Mon',
                    'Vint Max': 'RA-RaSIA01:RF-LLRF-A:FPGAVintMax-Mon',
                    'Vint Min': 'RA-RaSIA01:RF-LLRF-A:FPGAVintMin-Mon',
                    'Vaux': 'RA-RaSIA01:RF-LLRF-A:FPGAVaux-Mon',
                    'Vaux Max': 'RA-RaSIA01:RF-LLRF-A:FPGAVauxMax-Mon',
                    'Vaux Min': 'RA-RaSIA01:RF-LLRF-A:FPGAVauxMin-Mon'
                },
                'Mo1000': {
                    'Temp': 'RA-RaSIA01:RF-LLRF-A:MO1000Temp-Mon',
                    'Temp DAC 1': 'RA-RaSIA01:RF-LLRF-A:MO1000DAC1Temp-Mon',
                    'Temp DAC 2': 'RA-RaSIA01:RF-LLRF-A:MO1000DAC2Temp-Mon'
                },
                'Mi125': {
                    'Temp': 'RA-RaSIA01:RF-LLRF-A:M125Temp-Mon',
                },
                'GPIO': {
                    'ADC 0': 'RA-RaSIA01:RF-LLRF-A:GPIOADC0-Mon',
                    'ADC 3': 'RA-RaSIA01:RF-LLRF-A:GPIOADC3-Mon'
                },
                'Clock Src': 'RA-RaSIA01:RF-LLRF-A:MO1000ClkSrc-Sel',
                'Loop Trigger': 'RA-RaSIA01:RF-LLRF-A:LoopTrigProc-Mon',
                'PLL': 'RA-RaSIA01:RF-LLRF-A:MO1000PLL-Mon',
                'FPGA Init': 'RA-RaSIA01:RF-LLRF-A:FPGAInit-Cmd',
                'Cav Type': 'RA-RaSIA01:RF-LLRF-A:CavType-Mon',
                'Errors': 'RA-RaSIA01:RF-LLRF-A:InitErrors-Mon',
                'Int. Errors': 'RA-RaSIA01:RF-LLRF-A:InternalErr-Mon',
                'Int. Err. Clear': 'RA-RaSIA01:RF-LLRF-A:ResetIntError-Cmd',
                'Init': 'RA-RaSIA01:RF-LLRF-A:InitStatus-Mon',
                'Versions': {
                    'Firmware': 'RA-RaSIA01:RF-LLRF-A:FPGAVersion-Mon',
                    'IOC': 'RA-RaSIA01:RF-LLRF-A:Version-Mon'
                },
            },
            'B': {
                'FPGA': {
                    'Temp': 'RA-RaSIB01:RF-LLRF-B:FPGATemp-Mon',
                    'Temp Max': 'RA-RaSIB01:RF-LLRF-B:FPGATempMax-Mon',
                    'Temp Min': 'RA-RaSIB01:RF-LLRF-B:FPGATempMin-Mon',
                    'Vint': 'RA-RaSIB01:RF-LLRF-B:FPGAVint-Mon',
                    'Vint Max': 'RA-RaSIB01:RF-LLRF-B:FPGAVintMax-Mon',
                    'Vint Min': 'RA-RaSIB01:RF-LLRF-B:FPGAVintMin-Mon',
                    'Vaux': 'RA-RaSIB01:RF-LLRF-B:FPGAVaux-Mon',
                    'Vaux Max': 'RA-RaSIB01:RF-LLRF-B:FPGAVauxMax-Mon',
                    'Vaux Min': 'RA-RaSIB01:RF-LLRF-B:FPGAVauxMin-Mon'
                },
                'Mo1000': {
                    'Temp': 'RA-RaSIB01:RF-LLRF-B:MO1000Temp-Mon',
                    'Temp DAC 1': 'RA-RaSIB01:RF-LLRF-B:MO1000DAC1Temp-Mon',
                    'Temp DAC 2': 'RA-RaSIB01:RF-LLRF-B:MO1000DAC2Temp-Mon'
                },
                'Mi125': {
                    'Temp': 'RA-RaSIB01:RF-LLRF-B:M125Temp-Mon',
                },
                'GPIO': {
                    'ADC 0': 'RA-RaSIB01:RF-LLRF-B:GPIOADC0-Mon',
                    'ADC 3': 'RA-RaSIB01:RF-LLRF-B:GPIOADC3-Mon'
                },
                'Clock Src': 'RA-RaSIB01:RF-LLRF-B:MO1000ClkSrc-Sel',
                'Loop Trigger': 'RA-RaSIB01:RF-LLRF-B:LoopTrigProc-Mon',
                'PLL': 'RA-RaSIB01:RF-LLRF-B:MO1000PLL-Mon',
                'FPGA Init': 'RA-RaSIB01:RF-LLRF-B:FPGAInit-Cmd',
                'Cav Type': 'RA-RaSIB01:RF-LLRF-B:CavType-Mon',
                'Errors': 'RA-RaSIB01:RF-LLRF-B:InitErrors-Mon',
                'Int. Errors': 'RA-RaSIB01:RF-LLRF-B:InternalErr-Mon',
                'Int. Err. Clear': 'RA-RaSIB01:RF-LLRF-B:ResetIntError-Cmd',
                'Init': 'RA-RaSIB01:RF-LLRF-B:InitStatus-Mon',
                'Versions': {
                    'Firmware': 'RA-RaSIB01:RF-LLRF-B:FPGAVersion-Mon',
                    'IOC': 'RA-RaSIB01:RF-LLRF-B:Version-Mon'
                },
            }
        },
        'Loops': {
            'A': {
                'Control': {
                    '24 mV': ['Amp Loop Ref (mV)', 'RA-RaSIA01:RF-LLRF-A:ALRef'],
                    '24 VGap': ['Amp Loop Ref (VGap)', 'RA-RaSIA01:RF-LLRF-A:ALRefVGap'],
                    '25': ['Phase Loop Ref', 'RA-RaSIA01:RF-LLRF-A:PLRef'],
                    '29': ['Voltage Inc. Rate', 'RA-RaSIA01:RF-LLRF-A:AmpIncRate'],
                    '28': ['Phase Inc. Rate', 'RA-RaSIA01:RF-LLRF-A:PhsIncRate'],
                    '106': ['Look Reference', 'RA-RaSIA01:RF-LLRF-A:LookRef-Cmd'],
                    '114': ['Rect/Polar Mode Select', 'RA-RaSIA01:RF-LLRF-A:LoopMode'],
                    '107': ['Quadrant Selection', 'RA-RaSIA01:RF-LLRF-A:Quad'],
                    '26 mV': ['Amp Ref Min (mV)', 'RA-RaSIA01:RF-LLRF-A:AmpRefMin'],
                    '26 VGap': ['Amp Ref Min (VGap)', 'RA-RaSIA01:RF-LLRF-A:AmpRefMinVGap'],
                    '27': ['Phase Ref Min', 'RA-RaSIA01:RF-LLRF-A:PhsRefMin'],
                    '30': ['Open Loop Gain', 'RA-RaSIA01:RF-LLRF-A:OLGain'],
                    '31': ['Phase Correction Control', 'RA-RaSIA01:RF-LLRF-A:PhsCorrection'],
                    '80': ['Phase Correct Error', 'RA-RaSIA01:RF-LLRF-A:PhsCorrErr-Mon'],
                    '81': ['Phase Correct Control', 'RA-RaSIA01:RF-LLRF-A:PhsCorrCtrl-Mon'],
                    '125': ['Fwd Min Amp & Phs', 'RA-RaSIA01:RF-LLRF-A:LoopFwdMin'],
                    'Mode': 'RA-RaSIA01:RF-LLRF-A:LoopMode-Sts',
                    'Limits': {
                        '24': ['Amp Loop Ref', 'RA-RaSIA01:RF-LLRF-A:ALRef'],
                        '30': ['Open Loop Gain', 'RA-RaSIA01:RF-LLRF-A:OLGain'],
                        '0': ['Slow Loop Kp', 'RA-RaSIA01:RF-LLRF-A:SLKP'],
                    }
                },
                'General': {
                    '0': {
                        'Label': 'Cavity Voltage',
                        'InPhs': 'SI-03SP:RF-SRFCav-A:PwrI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-A:PwrQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrAmpdBm-Mon',
                        'Amp4': 'SI-03SP:RF-SRFCav-A:PwrAmpVGap-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrPhs-Mon'
                    },
                    '2': {
                        'Label': 'Forward Power',
                        'InPhs': 'SI-03SP:RF-SRFCav-A:PwrFwdI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-A:PwrFwdQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFwdAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFwdAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrFwdPhs-Mon'
                    },
                    '20': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutI-Mon',
                        'Quad': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutQ-Mon',
                        'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                        'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                        'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp1': '-',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': 'RA-RaSIA01:RF-LLRF-A:Dephase-Mon'
                    },
                },
                'Rect': {
                    '30': {
                        'Label': 'Fwd Pwr SSA 2',
                        'InPhs': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-A:PwrFBTNTopPhs-Mon'
                    },
                    'Slow': {
                        'Control': {
                            '100': ['Enable', 'RA-RaSIA01:RF-LLRF-A:SL'],
                            '110': ['Input Selection', 'RA-RaSIA01:RF-LLRF-A:SLInp'],
                            '13': ['PI Limit', 'RA-RaSIA01:RF-LLRF-A:SLPILim'],
                            '1': ['Ki', 'RA-RaSIA01:RF-LLRF-A:SLKI'],
                            '0': ['Kp', 'RA-RaSIA01:RF-LLRF-A:SLKP']
                        },
                        '512': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SLRefI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SLRefQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SLRefAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SLRefPhs-Mon'
                        },
                        '120': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SLInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SLInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SLInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SLInpPhs-Mon'
                        },
                        '14': {
                            'Label': 'Error',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SLErrorI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SLErrorQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SLErrorAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SLErrorPhs-Mon'
                        },
                        '16': {
                            'Label': 'Error Accum',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SLErrAccI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SLErrAccQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SLErrAccAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SLErrAccPhs-Mon'
                        },
                        '71': {
                            'Label': 'Slow Control Output',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SLCtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SLCtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SLCtrlPhs-Mon'
                        },
                    },
                    'Fast': {
                        'Control': {
                            '115': ['Enable', 'RA-RaSIA01:RF-LLRF-A:FL'],
                            '111': ['Input Selection', 'RA-RaSIA01:RF-LLRF-A:FLInp'],
                            '124': ['PI Limit', 'RA-RaSIA01:RF-LLRF-A:FLPILim'],
                            '119': ['Ki', 'RA-RaSIA01:RF-LLRF-A:FLKI'],
                            '118': ['Kp', 'RA-RaSIA01:RF-LLRF-A:FLKP']
                        },
                        '124': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:FLRefI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:FLRefQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:FLRefAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:FLRefPhs-Mon'
                        },
                        '112': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:FLInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:FLInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:FLInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:FLInpPhs-Mon'
                        },
                        '118': {
                            'Label': 'Fast Control Output',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:FLCtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:FLCtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:FLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:FLCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlPhs-Mon'
                        }
                    }
                },
                'Polar': {
                    '527': {
                        'Label': 'Amp Ref',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp1': 'RA-RaSIA01:RF-LLRF-A:AmpRefOld-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': '-'
                    },
                    'Amp': {
                        'Control': {
                            '116': ['Enable', 'RA-RaSIA01:RF-LLRF-A:AL'],
                            '112': ['Input Selection', 'RA-RaSIA01:RF-LLRF-A:ALInp'],
                            '121': ['Ki', 'RA-RaSIA01:RF-LLRF-A:ALKI'],
                            '120': ['Kp', 'RA-RaSIA01:RF-LLRF-A:ALKP']
                        },
                        '100': {
                            'Label': 'Amp Loop Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:ALInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:ALInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:ALInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:ALInpPhs-Mon'
                        },
                        '104': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:ALAmpInp-Mon',
                            'Phs': '-'
                        },
                        '105': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:ALPhsInp-Mon'
                        },
                        '109': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:ALErr-Mon',
                            'Phs': '-'
                        },
                        '110': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:ALErrAcc-Mon',
                            'Phs': '-'
                        },
                        '528': {
                            'Label': 'Phase Ref',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:PhsRefOld-Mon'
                        }
                    },
                    'Phase': {
                        'Control': {
                            '117': ['Enable', 'RA-RaSIA01:RF-LLRF-A:PL'],
                            '113': ['Input Selection', 'RA-RaSIA01:RF-LLRF-A:PLInp'],
                            '123': ['Ki', 'RA-RaSIA01:RF-LLRF-A:PLKI'],
                            '122': ['Kp', 'RA-RaSIA01:RF-LLRF-A:PLKP']
                        },
                        '102': {
                            'Label': 'Phase Loop Input',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:PLInpI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:PLInpQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:PLInpAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:PLInpPhs-Mon'
                        },
                        '106': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:PLAmpInp-Mon',
                            'Phs': '-'
                        },
                        '107': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:PLPhsInp-Mon'
                        },
                        '112': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:PLErr-Mon'
                        },
                        '113': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:PLErrAcc-Mon'
                        },
                        '114': {
                            'Label': 'Polar Control Output',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:POCtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:POCtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:POCtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:POCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:SSA2CtrlPhs-Mon'
                        }
                    }
                },
                'Equations': {
                    'Cav': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:CavSysCal',
                        'U-Raw': 'RA-RaSIA01:RF-LLRF-A:CavSysCalInv',
                        'OLG': 'RA-RaSIA01:RF-LLRF-A:CavSysCalOLG',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:CavOffset'
                    },
                    'Fwd Cav': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdCavSysCal',
                        'U-Raw': 'RA-RaSIA01:RF-LLRF-A:FwdCavSysCalInv',
                        'OLG': 'RA-RaSIA01:RF-LLRF-A:FwdCavSysCalOLG',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdCavOffset'
                    },
                    'Rev Cav': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:RevCavSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:RevCavOffset'
                    },
                    'Fwd SSA 1': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdSSA1SysCal',
                        'U-Raw': 'RA-RaSIA01:RF-LLRF-A:FwdSSA1SysCalInv',
                        'OLG': 'RA-RaSIA01:RF-LLRF-A:FwdSSA1SysCalOLG',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdSSA1SysCalOffset'
                    },
                    'Rev SSA 1': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:RevSSA1SysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:RevSSA1Offset' 
                    },
                    'Fwd SSA 2': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdSSA2SysCal',
                        'U-Raw': 'RA-RaSIA01:RF-LLRF-A:FwdSSA2SysCalInv',
                        'OLG': 'RA-RaSIA01:RF-LLRF-A:FwdSSA2SysCalOLG',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdSSA2SysCalOffset'
                    },
                    'Rev SSA 2': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:RevSSA2SysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:RevSSA2Offset' 
                    },
                    'Fwd Pre': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdPreSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdPreOffset'
                    },
                    'Fwd Pre 1': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdPre1SysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdPre1Offset'
                    },
                    'Fwd Pre 2': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdPre2SysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdPre2Offset'
                    },
                    'In Pre 1': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:In1PreAmpSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:In1PreAmpOffset'
                    },
                    'In Pre 2': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:In2PreAmpSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:In2PreAmpOffset'
                    },
                    'Fwd Circ': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:FwdCircSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:FwdCircOffset'
                    },
                    'Rev Circ': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:RevCircSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:RevCircOffset'
                    },
                    'MO': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:MOSysCal',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:MOOffset'
                    },
                    'Amp Loop Ref': {
                        'Raw-U': 'RA-RaSIA01:RF-LLRF-A:ALRefSysCal',
                        'U-Raw': 'RA-RaSIA01:RF-LLRF-A:ALRefSysCalInv',
                        'OFS': 'RA-RaSIA01:RF-LLRF-A:ALRefOffset'
                    },
                    'VGap': {
                        'Hw to Amp': 'RA-RaSIA01:RF-LLRF-A:Hw2AmpVCavCoeff',
                        'Amp to Hw': 'RA-RaSIA01:RF-LLRF-A:AmpVCav2HwCoeff'
                    },
                    'Rsh': 'SI-03SP:RF-SRFCav-A:Rsh-Cte'
                }
            },
            'B': {
                'Control': {
                    '24 mV': ['Amp Loop Ref (mV)', 'RA-RaSIB01:RF-LLRF-B:ALRef'],
                    '24 VGap': ['Amp Loop Ref (VGap)', 'RA-RaSIB01:RF-LLRF-B:ALRefVGap'],
                    '25': ['Phase Loop Ref', 'RA-RaSIB01:RF-LLRF-B:PLRef'],
                    '29': ['Voltage Inc. Rate', 'RA-RaSIB01:RF-LLRF-B:AmpIncRate'],
                    '28': ['Phase Inc. Rate', 'RA-RaSIB01:RF-LLRF-B:PhsIncRate'],
                    '106': ['Look Reference', 'RA-RaSIB01:RF-LLRF-B:LookRef-Cmd'],
                    '114': ['Rect/Polar Mode Select', 'RA-RaSIB01:RF-LLRF-B:LoopMode'],
                    '107': ['Quadrant Selection', 'RA-RaSIB01:RF-LLRF-B:Quad'],
                    '26 mV': ['Amp Ref Min (mV)', 'RA-RaSIB01:RF-LLRF-B:AmpRefMin'],
                    '26 VGap': ['Amp Ref Min (VGap)', 'RA-RaSIB01:RF-LLRF-B:AmpRefMinVGap'],
                    '27': ['Phase Ref Min', 'RA-RaSIB01:RF-LLRF-B:PhsRefMin'],
                    '30': ['Open Loop Gain', 'RA-RaSIB01:RF-LLRF-B:OLGain'],
                    '31': ['Phase Correction Control', 'RA-RaSIB01:RF-LLRF-B:PhsCorrection'],
                    '80': ['Phase Correct Error', 'RA-RaSIB01:RF-LLRF-B:PhsCorrErr-Mon'],
                    '81': ['Phase Correct Control', 'RA-RaSIB01:RF-LLRF-B:PhsCorrCtrl-Mon'],
                    '125': ['Fwd Min Amp & Phs', 'RA-RaSIB01:RF-LLRF-B:LoopFwdMin'],
                    'Mode': 'RA-RaSIB01:RF-LLRF-B:LoopMode-Sts',
                    'Limits': {
                        '24': ['Amp Loop Ref', 'RA-RaSIB01:RF-LLRF-B:ALRef'],
                        '30': ['Open Loop Gain', 'RA-RaSIB01:RF-LLRF-B:OLGain'],
                        '0': ['Slow Loop Kp', 'RA-RaSIB01:RF-LLRF-B:SLKP'],
                    }
                },
                'General': {
                    '0': {
                        'Label': 'Cavity Voltage',
                        'InPhs': 'SI-03SP:RF-SRFCav-B:PwrI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-B:PwrQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrAmpdBm-Mon',
                        'Amp4': 'SI-03SP:RF-SRFCav-B:PwrAmpVGap-Mon',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrPhs-Mon'
                    },
                    '2': {
                        'Label': 'Forward Power',
                        'InPhs': 'SI-03SP:RF-SRFCav-B:PwrFwdI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-B:PwrFwdQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFwdAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFwdAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrFwdPhs-Mon'
                    },
                    '20': {
                        'Label': 'Fwd Pwr SSA 1',
                        'InPhs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutI-Mon',
                        'Quad': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutQ-Mon',
                        'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmp-Mon',
                        'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmpW-Mon',
                        'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdOutPhs-Mon'
                    },
                    '32': {
                        'Label': 'Ang Cav Fwd',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp1': '-',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': 'RA-RaSIB01:RF-LLRF-B:Dephase-Mon'
                    },
                },
                'Rect': {
                    '30': {
                        'Label': 'Fwd Pwr SSA 2',
                        'InPhs': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopI-Mon',
                        'Quad': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopQ-Mon',
                        'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopAmp-Mon',
                        'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopAmpW-Mon',
                        'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopAmpdBm-Mon',
                        'Amp4': '-',
                        'Phs': 'SI-03SP:RF-SRFCav-B:PwrFBTNTopPhs-Mon'
                    },
                    'Slow': {
                        'Control': {
                            '100': ['Enable', 'RA-RaSIB01:RF-LLRF-B:SL'],
                            '110': ['Input Selection', 'RA-RaSIB01:RF-LLRF-B:SLInp'],
                            '13': ['PI Limit', 'RA-RaSIB01:RF-LLRF-B:SLPILim'],
                            '1': ['Ki', 'RA-RaSIB01:RF-LLRF-B:SLKI'],
                            '0': ['Kp', 'RA-RaSIB01:RF-LLRF-B:SLKP']
                        },
                        '512': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SLRefI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SLRefQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SLRefAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SLRefPhs-Mon'
                        },
                        '120': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SLInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SLInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SLInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SLInpPhs-Mon'
                        },
                        '14': {
                            'Label': 'Error',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SLErrorI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SLErrorQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SLErrorAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SLErrorPhs-Mon'
                        },
                        '16': {
                            'Label': 'Error Accum',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SLErrAccI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SLErrAccQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SLErrAccAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SLErrAccPhs-Mon'
                        },
                        '71': {
                            'Label': 'Slow Control Output',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SLCtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SLCtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SLCtrlPhs-Mon'
                        },
                    },
                    'Fast': {
                        'Control': {
                            '115': ['Enable', 'RA-RaSIB01:RF-LLRF-B:FL'],
                            '111': ['Input Selection', 'RA-RaSIB01:RF-LLRF-B:FLInp'],
                            '124': ['PI Limit', 'RA-RaSIB01:RF-LLRF-B:FLPILim'],
                            '119': ['Ki', 'RA-RaSIB01:RF-LLRF-B:FLKI'],
                            '118': ['Kp', 'RA-RaSIB01:RF-LLRF-B:FLKP']
                        },
                        '124': {
                            'Label': 'Reference',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:FLRefI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:FLRefQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:FLRefAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:FLRefPhs-Mon'
                        },
                        '112': {
                            'Label': 'Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:FLInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:FLInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:FLInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:FLInpPhs-Mon'
                        },
                        '118': {
                            'Label': 'Fast Control Output',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:FLCtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:FLCtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:FLCtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:FLCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlPhs-Mon'
                        }
                    }
                },
                'Polar': {
                    '527': {
                        'Label': 'Amp Ref',
                        'InPhs': '-',
                        'Quad': '-',
                        'Amp1': 'RA-RaSIB01:RF-LLRF-B:AmpRefOld-Mon',
                        'Amp2': '-',
                        'Amp3': '-',
                        'Amp4': '-',
                        'Phs': '-'
                    },
                    'Amp': {
                        'Control': {
                            '116': ['Enable', 'RA-RaSIB01:RF-LLRF-B:AL'],
                            '112': ['Input Selection', 'RA-RaSIB01:RF-LLRF-B:ALInp'],
                            '121': ['Ki', 'RA-RaSIB01:RF-LLRF-B:ALKI'],
                            '120': ['Kp', 'RA-RaSIB01:RF-LLRF-B:ALKP']
                        },
                        '100': {
                            'Label': 'Amp Loop Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:ALInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:ALInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:ALInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:ALInpPhs-Mon'
                        },
                        '104': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:ALAmpInp-Mon',
                            'Phs': '-'
                        },
                        '105': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:ALPhsInp-Mon'
                        },
                        '109': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:ALErr-Mon',
                            'Phs': '-'
                        },
                        '110': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:ALErrAcc-Mon',
                            'Phs': '-'
                        },
                        '528': {
                            'Label': 'Phase Ref',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:PhsRefOld-Mon'
                        }
                    },
                    'Phase': {
                        'Control': {
                            '117': ['Enable', 'RA-RaSIB01:RF-LLRF-B:PL'],
                            '113': ['Input Selection', 'RA-RaSIB01:RF-LLRF-B:PLInp'],
                            '123': ['Ki', 'RA-RaSIB01:RF-LLRF-B:PLKI'],
                            '122': ['Kp', 'RA-RaSIB01:RF-LLRF-B:PLKP']
                        },
                        '102': {
                            'Label': 'Phase Loop Input',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:PLInpI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:PLInpQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:PLInpAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:PLInpPhs-Mon'
                        },
                        '106': {
                            'Label': 'Amp of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:PLAmpInp-Mon',
                            'Phs': '-'
                        },
                        '107': {
                            'Label': 'Phase of Input',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:PLPhsInp-Mon'
                        },
                        '112': {
                            'Label': 'Error',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:PLErr-Mon'
                        },
                        '113': {
                            'Label': 'Error Accum',
                            'InPhs': '-',
                            'Quad': '-',
                            'Amp': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:PLErrAcc-Mon'
                        },
                        '114': {
                            'Label': 'Polar Control Output',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:POCtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:POCtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:POCtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:POCtrlPhs-Mon'
                        },
                        '6': {
                            'Label': 'SSA 1 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SSA1CtrlPhs-Mon'
                        },
                        '8': {
                            'Label': 'SSA 2 Control Signal',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlQ-Mon',
                            'Amp': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlAmp-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:SSA2CtrlPhs-Mon'
                        }
                    }
                },
                'Equations': {
                    'Cav': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:CavSysCal',
                        'U-Raw': 'RA-RaSIB01:RF-LLRF-B:CavSysCalInv',
                        'OLG': 'RA-RaSIB01:RF-LLRF-B:CavSysCalOLG',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:CavOffset'
                    },
                    'Fwd Cav': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdCavSysCal',
                        'U-Raw': 'RA-RaSIB01:RF-LLRF-B:FwdCavSysCalInv',
                        'OLG': 'RA-RaSIB01:RF-LLRF-B:FwdCavSysCalOLG',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdCavOffset'
                    },
                    'Rev Cav': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:RevCavSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:RevCavOffset'
                    },
                    'Fwd SSA 1': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdSSA1SysCal',
                        'U-Raw': 'RA-RaSIB01:RF-LLRF-B:FwdSSA1SysCalInv',
                        'OLG': 'RA-RaSIB01:RF-LLRF-B:FwdSSA1SysCalOLG',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdSSA1SysCalOffset'
                    },
                    'Rev SSA 1': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:RevSSA1SysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:RevSSA1Offset' 
                    },
                    'Fwd SSA 2': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdSSA2SysCal',
                        'U-Raw': 'RA-RaSIB01:RF-LLRF-B:FwdSSA2SysCalInv',
                        'OLG': 'RA-RaSIB01:RF-LLRF-B:FwdSSA2SysCalOLG',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdSSA2SysCalOffset'
                    },
                    'Rev SSA 2': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:RevSSA2SysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:RevSSA2Offset' 
                    },
                    'Fwd Pre': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdPreSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdPreOffset'
                    },
                    'Fwd Pre 1': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdPre1SysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdPre1Offset'
                    },
                    'Fwd Pre 2': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdPre2SysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdPre2Offset'
                    },
                    'In Pre 1': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:In1PreAmpSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:In1PreAmpOffset'
                    },
                    'In Pre 2': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:In2PreAmpSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:In2PreAmpOffset'
                    },
                    'Fwd Circ': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:FwdCircSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:FwdCircOffset'
                    },
                    'Rev Circ': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:RevCircSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:RevCircOffset'
                    },
                    'MO': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:MOSysCal',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:MOOffset'
                    },
                    'Amp Loop Ref': {
                        'Raw-U': 'RA-RaSIB01:RF-LLRF-B:ALRefSysCal',
                        'U-Raw': 'RA-RaSIB01:RF-LLRF-B:ALRefSysCalInv',
                        'OFS': 'RA-RaSIB01:RF-LLRF-B:ALRefOffset'
                    },
                    'VGap': {
                        'Hw to Amp': 'RA-RaSIB01:RF-LLRF-B:Hw2AmpVCavCoeff',
                        'Amp to Hw': 'RA-RaSIB01:RF-LLRF-B:AmpVCav2HwCoeff'
                    },
                    'Rsh': 'SI-03SP:RF-SRFCav-B:Rsh-Cte'
                }
            },
        },
        'RampDtls': {
            'A': {
                'Control': {
                    'Ramp Enable': 'RA-RaSIA01:RF-LLRF-A:RmpEn',
                    'Ramp Down Disable': 'RA-RaSIA01:RF-LLRF-A:RampDownDsbl',
                    '356': ['T1 Ramp Delay After Trig', 'RA-RaSIA01:RF-LLRF-A:RmpTs1'],
                    '357': ['T2 Ramp Up', 'RA-RaSIA01:RF-LLRF-A:RmpTs2'],
                    '358': ['T3 Ramp Top', 'RA-RaSIA01:RF-LLRF-A:RmpTs3'],
                    '359': ['T4 Ramp Down', 'RA-RaSIA01:RF-LLRF-A:RmpTs4'],
                    '360': ['Ramp Increase Rate', 'RA-RaSIA01:RF-LLRF-A:RmpIncTime'],
                    '164': ['Ref Top', 'RA-RaSIA01:RF-LLRF-A:RefTopAmp-Mon', 'red'],
                    '362 mV': ['Amp Ramp Top (mV)', 'RA-RaSIA01:RF-LLRF-A:RampAmpTop'],
                    '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-RaSIA01:RF-LLRF-A:RampAmpTopVGap'],
                    '364': ['Phase Ramp Top', 'RA-RaSIA01:RF-LLRF-A:RampPhsTop'],
                    '184': ['Ref Bot', 'RA-RaSIA01:RF-LLRF-A:RefBotAmp-Mon', 'blue'],
                    '361 mV': ['Amp Ramp Bot (mV)', 'RA-RaSIA01:RF-LLRF-A:RampAmpBot'],
                    '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-RaSIA01:RF-LLRF-A:RampAmpBotVGap'],
                    '363': ['Phase Ramp Bot', 'RA-RaSIA01:RF-LLRF-A:RampPhsBot'],
                    '536': ['Ramp Top', 'RA-RaSIA01:RF-LLRF-A:RampTop-Mon', 'green'],
                    '533': ['Ramp Ready', 'RA-RaSIA01:RF-LLRF-A:RampRdy-Mon'],
                    '365': ['Amp Ramp Up Slope', 'RA-RaSIA01:RF-LLRF-A:RampAmpUpCnt'],
                    '366': ['Amp Ramp Down Slope', 'RA-RaSIA01:RF-LLRF-A:RampAmpDownCnt'],
                    '367': ['Phase Ramp Up Slope', 'RA-RaSIA01:RF-LLRF-A:RampPhsUpCnt'],
                    '368': ['Phase Ramp Down Slope', 'RA-RaSIA01:RF-LLRF-A:RampPhsDownCnt'],
                    'Limits': {
                        '362': ['Top Reference', 'RA-RaSIA01:RF-LLRF-A:RampAmpTop'],
                        '361': ['Bot Reference', 'RA-RaSIA01:RF-LLRF-A:RampAmpBot']
                    }
                },
                'Diagnostics': {
                    'Top': {
                        '164': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:RefTopI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:RefTopQ-Mon',
                            'Amp1': 'RA-RaSIA01:RF-LLRF-A:RefTopAmp-Mon',
                            'Amp2': 'RA-RaSIA01:RF-LLRF-A:RefTopAmpW-Mon',
                            'Amp3': 'RA-RaSIA01:RF-LLRF-A:RefTopAmpdBm-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:RefTopPhs-Mon'
                        },
                        '150': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:PwrTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:PwrTopQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-A:PwrTopAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-A:PwrTopAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-A:PwrTopAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:PwrTopPhs-Mon'
                        },
                        '152': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdTopI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdTopQ-Mon',
                            'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                            'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                            'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                        },
                        '154': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:PwrRevTopI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:PwrRevTopQ-Mon',
                            'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrRevTopAmp-Mon',
                            'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                            'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrRevTopPhs-Mon'
                        },
                        '190': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:PwrFwdTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:PwrFwdTopQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFwdTopAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFwdTopAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:PwrFwdTopPhs-Mon'
                        },
                        '156': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdTopI-Mon',
                            'Quad': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdTopQ-Mon',
                            'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                            'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                            'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                        },
                        '158': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs':  'RA-ToSIA01:RF-SSAmpTower:PwrRevTopI-Mon',
                            'Quad':  'RA-ToSIA01:RF-SSAmpTower:PwrRevTopQ-Mon',
                            'Amp1':  'RA-ToSIA01:RF-SSAmpTower:PwrRevTopAmp-Mon',
                            'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                            'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                            'Phs':  'RA-ToSIA01:RF-SSAmpTower:PwrRevTopPhs-Mon'
                        },
                        '160': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:PwrRevTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:PwrRevTopQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-A:PwrRevTopAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-A:PwrRevTopAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-A:PwrRevTopAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:PwrRevTopPhs-Mon'
                        },
                        '168': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:ErrTopI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:ErrTopQ-Mon',
                            'Amp1': 'RA-RaSIA01:RF-LLRF-A:ErrTopAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:ErrTopPhs-Mon'
                        },
                        '166': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:CtrlTopI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:CtrlTopQ-Mon',
                            'Amp1': 'RA-RaSIA01:RF-LLRF-A:CtrlTopAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:CtrlTopPhs-Mon'
                        },
                        '162': {
                            'Label': 'Tuning Dephase',
                            'PV': 'RA-RaSIA01:RF-LLRF-A:TuneDephsTop-Mon'
                        },
                        '163': {
                            'Label': 'FF Error',
                            'PV': 'RA-RaSIA01:RF-LLRF-A:FFErrTop-Mon'
                        },
                        '531': {
                            'Label': '5 Hz Trigger',
                            'PV': 'RA-RaSIA01:RF-LLRF-A:RampTrigger-Mon'
                        }
                    },
                    'Bot': {
                        '184': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:RefBotI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:RefBotQ-Mon',
                            'Amp1': 'RA-RaSIA01:RF-LLRF-A:RefBotAmp-Mon',
                            'Amp2': 'RA-RaSIA01:RF-LLRF-A:RefBotAmpW-Mon',
                            'Amp3': 'RA-RaSIA01:RF-LLRF-A:RefBotAmpdBm-Mon',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:RefBotPhs-Mon'
                        },
                        '170': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:PwrBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:PwrBotQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-A:PwrBotAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-A:PwrBotAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-A:PwrBotAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:PwrBotPhs-Mon'
                        },
                        '172': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdBotI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdBotQ-Mon',
                            'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                            'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                            'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                        },
                        '174': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIA02:RF-SSAmpTower:PwrRevBotI-Mon',
                            'Quad': 'RA-ToSIA02:RF-SSAmpTower:PwrRevBotQ-Mon',
                            'Amp1': 'RA-ToSIA02:RF-SSAmpTower:PwrRevBotAmp-Mon',
                            'Amp2': 'RA-ToSIA02:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                            'Amp3': 'RA-ToSIA02:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIA02:RF-SSAmpTower:PwrRevBotPhs-Mon'
                        },
                        '192': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:PwrFwdBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:PwrFwdBotQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-A:PwrFwdBotAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-A:PwrFwdBotAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-A:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:PwrFwdBotPhs-Mon'
                        },
                        '176': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdBotI-Mon',
                            'Quad': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdBotQ-Mon',
                            'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                            'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                            'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                        },
                        '178': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs': 'RA-ToSIA01:RF-SSAmpTower:PwrRevBotI-Mon',
                            'Quad': 'RA-ToSIA01:RF-SSAmpTower:PwrRevBotQ-Mon',
                            'Amp1': 'RA-ToSIA01:RF-SSAmpTower:PwrRevBotAmp-Mon',
                            'Amp2': 'RA-ToSIA01:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                            'Amp3': 'RA-ToSIA01:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIA01:RF-SSAmpTower:PwrRevBotPhs-Mon'
                        },
                        '180': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-A:PwrRevBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-A:PwrRevBotQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-A:PwrRevBotAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-A:PwrRevBotAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-A:PwrRevBotAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-A:PwrRevBotPhs-Mon'
                        },
                        '188': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:ErrBotI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:ErrBotQ-Mon',
                            'Amp1': 'RA-RaSIA01:RF-LLRF-A:ErrBotAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:ErrBotPhs-Mon'
                        },
                        '186': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIA01:RF-LLRF-A:CtrlBotI-Mon',
                            'Quad': 'RA-RaSIA01:RF-LLRF-A:CtrlBotQ-Mon',
                            'Amp1': 'RA-RaSIA01:RF-LLRF-A:CtrlBotAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIA01:RF-LLRF-A:CtrlBotPhs-Mon'
                        },
                        '183': {
                            'Label': 'FF Error',
                            'PV': 'RA-RaSIA01:RF-LLRF:FFErrBot-Mon'
                        },
                        '531': {
                            'Label': '5 Hz Trigger',
                            'PV': 'RA-RaSIA01:RF-LLRF-A:RampTrigger-Mon'
                        }
                    }
                },
            },
            'B': {
                'Control': {
                    'Ramp Enable': 'RA-RaSIB01:RF-LLRF-B:RmpEn',
                    'Ramp Down Disable': 'RA-RaSIB01:RF-LLRF-B:RampDownDsbl',
                    '356': ['T1 Ramp Delay After Trig', 'RA-RaSIB01:RF-LLRF-B:RmpTs1'],
                    '357': ['T2 Ramp Up', 'RA-RaSIB01:RF-LLRF-B:RmpTs2'],
                    '358': ['T3 Ramp Top', 'RA-RaSIB01:RF-LLRF-B:RmpTs3'],
                    '359': ['T4 Ramp Down', 'RA-RaSIB01:RF-LLRF-B:RmpTs4'],
                    '360': ['Ramp Increase Rate', 'RA-RaSIB01:RF-LLRF-B:RmpIncTime'],
                    '164': ['Ref Top', 'RA-RaSIB01:RF-LLRF-B:RefTopAmp-Mon', 'red'],
                    '362 mV': ['Amp Ramp Top (mV)', 'RA-RaSIB01:RF-LLRF-B:RampAmpTop'],
                    '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-RaSIB01:RF-LLRF-B:RampAmpTopVGap'],
                    '364': ['Phase Ramp Top', 'RA-RaSIB01:RF-LLRF-B:RampPhsTop'],
                    '184': ['Ref Bot', 'RA-RaSIB01:RF-LLRF-B:RefBotAmp-Mon', 'blue'],
                    '361 mV': ['Amp Ramp Bot (mV)', 'RA-RaSIB01:RF-LLRF-B:RampAmpBot'],
                    '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-RaSIB01:RF-LLRF-B:RampAmpBotVGap'],
                    '363': ['Phase Ramp Bot', 'RA-RaSIB01:RF-LLRF-B:RampPhsBot'],
                    '536': ['Ramp Top', 'RA-RaSIB01:RF-LLRF-B:RampTop-Mon', 'green'],
                    '533': ['Ramp Ready', 'RA-RaSIB01:RF-LLRF-B:RampRdy-Mon'],
                    '365': ['Amp Ramp Up Slope', 'RA-RaSIB01:RF-LLRF-B:RampAmpUpCnt'],
                    '366': ['Amp Ramp Down Slope', 'RA-RaSIB01:RF-LLRF-B:RampAmpDownCnt'],
                    '367': ['Phase Ramp Up Slope', 'RA-RaSIB01:RF-LLRF-B:RampPhsUpCnt'],
                    '368': ['Phase Ramp Down Slope', 'RA-RaSIB01:RF-LLRF-B:RampPhsDownCnt'],
                    'Limits': {
                        '362': ['Top Reference', 'RA-RaSIB01:RF-LLRF-B:RampAmpTop'],
                        '361': ['Bot Reference', 'RA-RaSIB01:RF-LLRF-B:RampAmpBot']
                    }
                },
                'Diagnostics': {
                    'Top': {
                        '164': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:RefTopI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:RefTopQ-Mon',
                            'Amp1': 'RA-RaSIB01:RF-LLRF-B:RefTopAmp-Mon',
                            'Amp2': 'RA-RaSIB01:RF-LLRF-B:RefTopAmpW-Mon',
                            'Amp3': 'RA-RaSIB01:RF-LLRF-B:RefTopAmpdBm-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:RefTopPhs-Mon'
                        },
                        '150': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:PwrTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:PwrTopQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-B:PwrTopAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-B:PwrTopAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-B:PwrTopAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:PwrTopPhs-Mon'
                        },
                        '152': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdTopI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdTopQ-Mon',
                            'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                            'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                            'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                        },
                        '154': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:PwrRevTopI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:PwrRevTopQ-Mon',
                            'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrRevTopAmp-Mon',
                            'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                            'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrRevTopPhs-Mon'
                        },
                        '190': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:PwrFwdTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:PwrFwdTopQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFwdTopAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFwdTopAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:PwrFwdTopPhs-Mon'
                        },
                        '156': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdTopI-Mon',
                            'Quad': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdTopQ-Mon',
                            'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                            'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                            'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                        },
                        '158': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs':  'RA-ToSIB01:RF-SSAmpTower:PwrRevTopI-Mon',
                            'Quad':  'RA-ToSIB01:RF-SSAmpTower:PwrRevTopQ-Mon',
                            'Amp1':  'RA-ToSIB01:RF-SSAmpTower:PwrRevTopAmp-Mon',
                            'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                            'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                            'Phs':  'RA-ToSIB01:RF-SSAmpTower:PwrRevTopPhs-Mon'
                        },
                        '160': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:PwrRevTopI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:PwrRevTopQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-B:PwrRevTopAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-B:PwrRevTopAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-B:PwrRevTopAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:PwrRevTopPhs-Mon'
                        },
                        '168': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:ErrTopI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:ErrTopQ-Mon',
                            'Amp1': 'RA-RaSIB01:RF-LLRF-B:ErrTopAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:ErrTopPhs-Mon'
                        },
                        '166': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:CtrlTopI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:CtrlTopQ-Mon',
                            'Amp1': 'RA-RaSIB01:RF-LLRF-B:CtrlTopAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:CtrlTopPhs-Mon'
                        },
                        '162': {
                            'Label': 'Tuning Dephase',
                            'PV': 'RA-RaSIB01:RF-LLRF-B:TuneDephsTop-Mon'
                        },
                        '163': {
                            'Label': 'FF Error',
                            'PV': 'RA-RaSIB01:RF-LLRF-B:FFErrTop-Mon'
                        },
                        '531': {
                            'Label': '5 Hz Trigger',
                            'PV': 'RA-RaSIB01:RF-LLRF-B:RampTrigger-Mon'
                        }
                    },
                    'Bot': {
                        '184': {
                            'Label': 'Ref',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:RefBotI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:RefBotQ-Mon',
                            'Amp1': 'RA-RaSIB01:RF-LLRF-B:RefBotAmp-Mon',
                            'Amp2': 'RA-RaSIB01:RF-LLRF-B:RefBotAmpW-Mon',
                            'Amp3': 'RA-RaSIB01:RF-LLRF-B:RefBotAmpdBm-Mon',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:RefBotPhs-Mon'
                        },
                        '170': {
                            'Label': 'Cell 3',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:PwrBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:PwrBotQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-B:PwrBotAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-B:PwrBotAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-B:PwrBotAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:PwrBotPhs-Mon'
                        },
                        '172': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdBotI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdBotQ-Mon',
                            'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                            'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                            'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                        },
                        '174': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-ToSIB02:RF-SSAmpTower:PwrRevBotI-Mon',
                            'Quad': 'RA-ToSIB02:RF-SSAmpTower:PwrRevBotQ-Mon',
                            'Amp1': 'RA-ToSIB02:RF-SSAmpTower:PwrRevBotAmp-Mon',
                            'Amp2': 'RA-ToSIB02:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                            'Amp3': 'RA-ToSIB02:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIB02:RF-SSAmpTower:PwrRevBotPhs-Mon'
                        },
                        '192': {
                            'Label': 'Fwd Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:PwrFwdBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:PwrFwdBotQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-B:PwrFwdBotAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-B:PwrFwdBotAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-B:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:PwrFwdBotPhs-Mon'
                        },
                        '176': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdBotI-Mon',
                            'Quad': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdBotQ-Mon',
                            'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                            'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                            'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                        },
                        '178': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs': 'RA-ToSIB01:RF-SSAmpTower:PwrRevBotI-Mon',
                            'Quad': 'RA-ToSIB01:RF-SSAmpTower:PwrRevBotQ-Mon',
                            'Amp1': 'RA-ToSIB01:RF-SSAmpTower:PwrRevBotAmp-Mon',
                            'Amp2': 'RA-ToSIB01:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                            'Amp3': 'RA-ToSIB01:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                            'Phs': 'RA-ToSIB01:RF-SSAmpTower:PwrRevBotPhs-Mon'
                        },
                        '180': {
                            'Label': 'Rev Cavity',
                            'InPhs': 'SI-03SP:RF-SRFCav-B:PwrRevBotI-Mon',
                            'Quad': 'SI-03SP:RF-SRFCav-B:PwrRevBotQ-Mon',
                            'Amp1': 'SI-03SP:RF-SRFCav-B:PwrRevBotAmp-Mon',
                            'Amp2': 'SI-03SP:RF-SRFCav-B:PwrRevBotAmpW-Mon',
                            'Amp3': 'SI-03SP:RF-SRFCav-B:PwrRevBotAmpdBm-Mon',
                            'Phs': 'SI-03SP:RF-SRFCav-B:PwrRevBotPhs-Mon'
                        },
                        '188': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:ErrBotI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:ErrBotQ-Mon',
                            'Amp1': 'RA-RaSIB01:RF-LLRF-B:ErrBotAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:ErrBotPhs-Mon'
                        },
                        '186': {
                            'Label': 'Control',
                            'InPhs': 'RA-RaSIB01:RF-LLRF-B:CtrlBotI-Mon',
                            'Quad': 'RA-RaSIB01:RF-LLRF-B:CtrlBotQ-Mon',
                            'Amp1': 'RA-RaSIB01:RF-LLRF-B:CtrlBotAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-RaSIB01:RF-LLRF-B:CtrlBotPhs-Mon'
                        },
                        '183': {
                            'Label': 'FF Error',
                            'PV': 'RA-RaSIB01:RF-LLRF-B:FFErrBot-Mon'
                        },
                        '531': {
                            'Label': '5 Hz Trigger',
                            'PV': 'RA-RaSIB01:RF-LLRF-B:RampTrigger-Mon'
                        }
                    }
                }
            }
        },
        'AutoStart': {
            'A': {
                '22': ['Automatic Startup Enable', 'RA-RaSIA01:RF-LLRF-A:AutoStartupEn'],
                '23': ['Command Start', 'RA-RaSIA01:RF-LLRF-A:AutoStartupCmdStart'],
                '400': ['EPS Interlock', 'RA-RaSIA01:RF-LLRF-A:EPSEn'],
                '401': ['Interlock Bypass', 'RA-RaSIA01:RF-LLRF-A:FIMEn'],
                'Diag': {
                    '500': ['State Start', 'RA-RaSIA01:RF-LLRF-A:AutoStartState-Mon'],
                    '400': ['Tx Ready', 'RA-RaSIA01:RF-LLRF-A:SSARdy-Mon'],
                    '401': ['Fast Interlock', 'RA-RaSIA01:RF-LLRF-A:IntlkAll-Mon'],
                    '308': ['Slow Loop Fwd Min', 'RA-RaSIA01:RF-LLRF-A:SLFwdMin-Mon'],
                    '309': ['Fast Loop Fwd Min', 'RA-RaSIA01:RF-LLRF-A:FLFwdMin-Mon'],
                    '310': ['Amp Loop Fwd Min', 'RA-RaSIA01:RF-LLRF-A:ALFwdMin-Mon'],
                    '311': ['Phase Loop Fwd Min', 'RA-RaSIA01:RF-LLRF-A:PLFwdMin-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIA01:RF-LLRF-A:TuneFwdMin-Mon']
                }
            },
            'B': {
                '22': ['Automatic Startup Enable', 'RA-RaSIB01:RF-LLRF-B:AutoStartupEn'],
                '23': ['Command Start', 'RA-RaSIB01:RF-LLRF-B:AutoStartupCmdStart'],
                '400': ['EPS Interlock', 'RA-RaSIB01:RF-LLRF-B:EPSEn'],
                '401': ['Interlock Bypass', 'RA-RaSIB01:RF-LLRF-B:FIMEn'],
                'Diag': {
                    '500': ['State Start', 'RA-RaSIB01:RF-LLRF-B:AutoStartState-Mon'],
                    '400': ['Tx Ready', 'RA-RaSIB01:RF-LLRF-B:SSARdy-Mon'],
                    '401': ['Fast Interlock', 'RA-RaSIB01:RF-LLRF-B:IntlkAll-Mon'],
                    '308': ['Slow Loop Fwd Min', 'RA-RaSIB01:RF-LLRF-B:SLFwdMin-Mon'],
                    '309': ['Fast Loop Fwd Min', 'RA-RaSIB01:RF-LLRF-B:FLFwdMin-Mon'],
                    '310': ['Amp Loop Fwd Min', 'RA-RaSIB01:RF-LLRF-B:ALFwdMin-Mon'],
                    '311': ['Phase Loop Fwd Min', 'RA-RaSIB01:RF-LLRF-B:PLFwdMin-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIB01:RF-LLRF-B:TuneFwdMin-Mon']
                }
            }
        },
        'Conditioning': {
            'A': {
                '200': ['Pulse Mode Enable', 'RA-RaSIA01:RF-LLRF-A:CondEn'],
                '201': ['Auto Conditioning Enable', 'RA-RaSIA01:RF-LLRF-A:CondAuto'],
                '204': ['Conditioning Freq', 'RA-RaSIA01:RF-LLRF-A:CondFreq'],
                '540': ['Cond Freq Diag', 'RA-RaSIA01:RF-LLRF-A:CondFreq-Mon'],
                '205': ['Duty Cycle', 'RA-RaSIA01:RF-LLRF-A:CondDuty2'],
                '530': ['Duty Cycle RB', 'RA-RaSIA01:RF-LLRF-A:CondDutyCycle-Mon'],
                '79': ['Vacuum', 'RA-RaSIA01:RF-LLRF-A:VacuumFastRly-Mon'],
            },
            'B': {
                '200': ['Pulse Mode Enable', 'RA-RaSIB01:RF-LLRF-B:CondEn'],
                '201': ['Auto Conditioning Enable', 'RA-RaSIB01:RF-LLRF-B:CondAuto'],
                '204': ['Conditioning Freq', 'RA-RaSIB01:RF-LLRF-B:CondFreq'],
                '540': ['Cond Freq Diag', 'RA-RaSIB01:RF-LLRF-B:CondFreq-Mon'],
                '205': ['Duty Cycle', 'RA-RaSIB01:RF-LLRF-B:CondDuty2'],
                '530': ['Duty Cycle RB', 'RA-RaSIB01:RF-LLRF-B:CondDutyCycle-Mon'],
                '79': ['Vacuum', 'RA-RaSIB01:RF-LLRF-B:VacuumFastRly-Mon'],
            }
        },
        'TunDtls': {
            'A': {
                'General': {
                    '34': ['Fwd Pwr Amplitude', 'RA-RaSIA01:RF-LLRF-A:CavFwdAmp-Mon'],
                    '19': ['Fwd Pwr Phase Angle', 'RA-RaSIA01:RF-LLRF-A:CavFwdPhs-Mon'],
                    '33': ['Cavity Amplitude', 'RA-RaSIA01:RF-LLRF-A:CavAmp-Mon'],
                    '18': ['Cavity Phase Angle', 'RA-RaSIA01:RF-LLRF-A:CavPhs-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIA01:RF-LLRF-A:TuneFwdMin-Mon'],
                    '303': ['Pulses Frequency', 'RA-RaSIA01:RF-LLRF-A:TuneFreq'],
                },
                'Manual': {
                    '302': ['Number of Pulses', 'RA-RaSIA01:RF-LLRF-A:TuneStep'],
                    '306': ['Tunner Move Dir', 'RA-RaSIA01:RF-LLRF-A:TunnerDir'],
                    '305': ['Tunner Move', 'RA-RaSIA01:RF-LLRF-A:TunnerMove'],
                    '307': ['Tuning Reset', 'RA-RaSIA01:RF-LLRF-A:TunnerMove-Cmd'],
                    '302 Man': ['Tunner Manual Dn', 'SI-03SP:RF-SRFCav-A:TunnerManDown-Mon'],
                    '303 Man': ['Tunner Manual Up', 'SI-03SP:RF-SRFCav-A:TunnerManUp-Mon'],
                },
                'Auto': {
                    '301': ['Tuning Pos Enable', 'RA-RaSIA01:RF-LLRF-A:TuneDir'],
                    '309': ['Tuning Margin High', 'RA-RaSIA01:RF-LLRF-A:TuneMarginHI'],
                    '310': ['Tuning Margin Low', 'RA-RaSIA01:RF-LLRF-A:TuneMarginLO'],
                    '308': ['Tuning Forward Min', 'RA-RaSIA01:RF-LLRF-A:TuneFwdMin'],
                    '311': ['Tuning Delay', 'RA-RaSIA01:RF-LLRF-A:TuneDly'],
                    '312': ['Tuning Filter Enable', 'RA-RaSIA01:RF-LLRF-A:TuneFilt'],
                    '313': ['Tuning Trigger Enable', 'RA-RaSIA01:RF-LLRF-A:TuneTrig'],
                    '316': ['Tuning/FF On Top Ramp', 'RA-RaSIA01:RF-LLRF-A:RampTuneTop'],
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
                    '34': ['Fwd Pwr Amplitude', 'RA-RaSIB01:RF-LLRF-B:CavFwdAmp-Mon'],
                    '19': ['Fwd Pwr Phase Angle', 'RA-RaSIB01:RF-LLRF-B:CavFwdPhs-Mon'],
                    '33': ['Cavity Amplitude', 'RA-RaSIB01:RF-LLRF-B:CavAmp-Mon'],
                    '18': ['Cavity Phase Angle', 'RA-RaSIB01:RF-LLRF-B:CavPhs-Mon'],
                    '307': ['Tuning Fwd Min', 'RA-RaSIB01:RF-LLRF-B:TuneFwdMin-Mon'],
                    '303': ['Pulses Frequency', 'RA-RaSIB01:RF-LLRF-B:TuneFreq'],
                },
                'Manual': {
                    '302': ['Number of Pulses', 'RA-RaSIB01:RF-LLRF-B:TuneStep'],
                    '306': ['Tunner Move Dir', 'RA-RaSIB01:RF-LLRF-B:TunnerDir'],
                    '305': ['Tunner Move', 'RA-RaSIB01:RF-LLRF-B:TunnerMove'],
                    '307': ['Tuning Reset', 'RA-RaSIB01:RF-LLRF-B:TunnerMove-Cmd'],
                    '302 Man': ['Tunner Manual Dn', 'SI-03SP:RF-SRFCav-B:TunnerManDown-Mon'],
                    '303 Man': ['Tunner Manual Up', 'SI-03SP:RF-SRFCav-B:TunnerManUp-Mon'],
                },
                'Auto': {
                    '301': ['Tuning Pos Enable', 'RA-RaSIB01:RF-LLRF-B:TuneDir'],
                    '309': ['Tuning Margin High', 'RA-RaSIB01:RF-LLRF-B:TuneMarginHI'],
                    '310': ['Tuning Margin Low', 'RA-RaSIB01:RF-LLRF-B:TuneMarginLO'],
                    '308': ['Tuning Forward Min', 'RA-RaSIB01:RF-LLRF-B:TuneFwdMin'],
                    '311': ['Tuning Delay', 'RA-RaSIB01:RF-LLRF-B:TuneDly'],
                    '312': ['Tuning Filter Enable', 'RA-RaSIB01:RF-LLRF-B:TuneFilt'],
                    '313': ['Tuning Trigger Enable', 'RA-RaSIB01:RF-LLRF-B:TuneTrig'],
                    '316': ['Tuning/FF On Top Ramp', 'RA-RaSIB01:RF-LLRF-B:RampTuneTop'],
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
                        'Manual': ['Manual Interlock', 'RA-RaSIA01:RF-LLRF-A:IntlkManual'],
                        'EndSw': ['End Switches', 'RA-RaSIA01:RF-LLRF-A:EndSwLogicInv'],
                        'Delay': 'RA-RaSIA01:RF-LLRF-A:IntlkDly',
                        'HW': 'RA-RaSIA01:RF-LLRF-A:FDLHwTrig-Mon',
                        'Beam Inv': ['Logic Inv. LLRF Beam Trip', 'RA-RaSIA01:RF-LLRF-A:OrbitIntlkLogicInv'],
                        'Vacuum Inv': ['Vacuum Logic Inversion', 'RA-RaSIA01:RF-LLRF-A:VacLogicInv']
                    },
                    'Levels': {
                        'RevSSA1': 'RA-RaSIA01:RF-LLRF-A:LimRevSSA1',
                        'RevSSA2': 'RA-RaSIA01:RF-LLRF-A:LimRevSSA2',
                        'RevSSA3': 'RA-RaSIA01:RF-LLRF-A:LimRevSSA3',
                        'RevSSA4': 'RA-RaSIA01:RF-LLRF-A:LimRevSSA4',
                        'RevCav': 'RA-RaSIA01:RF-LLRF-A:LimRevCav',
                        'VCav': 'RA-RaSIA01:RF-LLRF-A:LimCav',
                        'FwCav': 'RA-RaSIA01:RF-LLRF-A:LimFwdCav',
                        'FwSSA1': 'RA-RaSIA01:RF-LLRF-A:LimFwdSSA1',
                        'RF In 7': 'RA-RaSIA01:RF-LLRF-A:LimRefIn7',
                        'RF In 8': 'RA-RaSIA01:RF-LLRF-A:LimRefIn8',
                        'RF In 9': 'RA-RaSIA01:RF-LLRF-A:LimRefIn9',
                        'RF In 10': 'RA-RaSIA01:RF-LLRF-A:LimRefIn10',
                        'RF In 11': 'RA-RaSIA01:RF-LLRF-A:LimRefIn11',
                        'RF In 12': 'RA-RaSIA01:RF-LLRF-A:LimRefIn12',
                        'RF In 13': 'RA-RaSIA01:RF-LLRF-A:LimRefIn13',
                        'RF In 14': 'RA-RaSIA01:RF-LLRF-A:LimRefIn14',
                        'RF In 15': 'RA-RaSIA01:RF-LLRF-A:LimRefIn15'
                    },
                    'GPIO': {
                        'Inp': 'RA-RaSIA01:RF-LLRF-A:GPIOInp-Mon',
                        'Intlk': 'RA-RaSIA01:RF-LLRF-A:GPIOIntlk-Mon',
                        'Out': 'RA-RaSIA01:RF-LLRF-A:GPIOOut-Mon'
                    }
                },
                'Bypass': {
                    '806': ['Rev SSA 1', 'RA-RaSIA01:RF-LLRF-A:FIMRevSSA1'],
                    '807': ['Rev SSA 2', 'RA-RaSIA01:RF-LLRF-A:FIMRevSSA2'],
                    '808': ['Rev SSA 3', 'RA-RaSIA01:RF-LLRF-A:FIMRevSSA3'],
                    '809': ['Rev SSA 4', 'RA-RaSIA01:RF-LLRF-A:FIMRevSSA4'],
                    '810': ['Rev Cavity', 'RA-RaSIA01:RF-LLRF-A:FIMRevCav'],
                    '811': ['Manual Interlock', 'RA-RaSIA01:RF-LLRF-A:FIMManual'],
                    '812': ['PLC', 'RA-RaSIA01:RF-LLRF-A:FIMPLC'],
                    '813': ['Ext LLRF 1', 'RA-RaSIA01:RF-LLRF-A:FIMLLRF1'],
                    '814': ['Ext LLRF 2', 'RA-RaSIA01:RF-LLRF-A:FIMLLRF2'],
                    '815': ['Ext LLRF 3', 'RA-RaSIA01:RF-LLRF-A:FIMLLRF3'],
                    '816 1': ['End Switch Up 1', 'RA-RaSIA01:RF-LLRF-A:FIMTunnerHigh'],
                    '817 1': ['End Switch Down 1', 'RA-RaSIA01:RF-LLRF-A:FIMTunnerLow'],
                    '816 2': ['End Switch Up 2', 'RA-RaSIA01:RF-LLRF-A:FIMPLG2Up'],
                    '817 2': ['End Switch Down 2', 'RA-RaSIA01:RF-LLRF-A:FIMPLG2Down'],
                    '835': ['ILK VCav', 'RA-RaSIA01:RF-LLRF-A:FIMCav'],
                    '836': ['ILK Fwd Cav', 'RA-RaSIA01:RF-LLRF-A:FIMFwdCav'],
                    '837': ['ILK Fw SSA 1', 'RA-RaSIA01:RF-LLRF-A:FIMFwdSSA1'],
                    '838': ['ILK RF In 7', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn7'],
                    '839': ['ILK RF In 8', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn8'],
                    '840': ['ILK RF In 9', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn9'],
                    '841': ['ILK RF In 10', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn10'],
                    '842': ['ILK RF In 11', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn11'],
                    '843': ['ILK RF In 12', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn12'],
                    '844': ['ILK RF In 13', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn13'],
                    '845': ['ILK RF In 14', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn14'],
                    '846': ['ILK RF In 15', 'RA-RaSIA01:RF-LLRF-A:FIMRFIn15'],
                    '847': ['ILK LLRF Beam Trip', 'RA-RaSIA01:RF-LLRF-A:FIMOrbitIntlk']
                }
            },
            'B': {
                'Diagnostics': {
                    'General': {
                        'Manual': ['Manual Interlock', 'RA-RaSIB01:RF-LLRF-B:IntlkManual'],
                        'EndSw': ['End Switches', 'RA-RaSIB01:RF-LLRF-B:EndSwLogicInv'],
                        'Delay': 'RA-RaSIB01:RF-LLRF-B:IntlkDly',
                        'HW': 'RA-RaSIB01:RF-LLRF-B:FDLHwTrig-Mon',
                        'Beam Inv': ['Logic Inv. LLRF Beam Trip', 'RA-RaSIB01:RF-LLRF-B:OrbitIntlkLogicInv'],
                        'Vacuum Inv': ['Vacuum Logic Inversion', 'RA-RaSIB01:RF-LLRF-B:VacLogicInv']
                    },
                    'Levels': {
                        'RevSSA1': 'RA-RaSIB01:RF-LLRF-B:LimRevSSA1',
                        'RevSSA2': 'RA-RaSIB01:RF-LLRF-B:LimRevSSA2',
                        'RevSSA3': 'RA-RaSIB01:RF-LLRF-B:LimRevSSA3',
                        'RevSSA4': 'RA-RaSIB01:RF-LLRF-B:LimRevSSA4',
                        'RevCav': 'RA-RaSIB01:RF-LLRF-B:LimRevCav',
                        'VCav': 'RA-RaSIB01:RF-LLRF-B:LimCav',
                        'FwCav': 'RA-RaSIB01:RF-LLRF-B:LimFwdCav',
                        'FwSSA1': 'RA-RaSIB01:RF-LLRF-B:LimFwdSSA1',
                        'RF In 7': 'RA-RaSIB01:RF-LLRF-B:LimRefIn7',
                        'RF In 8': 'RA-RaSIB01:RF-LLRF-B:LimRefIn8',
                        'RF In 9': 'RA-RaSIB01:RF-LLRF-B:LimRefIn9',
                        'RF In 10': 'RA-RaSIB01:RF-LLRF-B:LimRefIn10',
                        'RF In 11': 'RA-RaSIB01:RF-LLRF-B:LimRefIn11',
                        'RF In 12': 'RA-RaSIB01:RF-LLRF-B:LimRefIn12',
                        'RF In 13': 'RA-RaSIB01:RF-LLRF-B:LimRefIn13',
                        'RF In 14': 'RA-RaSIB01:RF-LLRF-B:LimRefIn14',
                        'RF In 15': 'RA-RaSIB01:RF-LLRF-B:LimRefIn15'
                    },
                    'GPIO': {
                        'Inp': 'RA-RaSIB01:RF-LLRF-B:GPIOInp-Mon',
                        'Intlk': 'RA-RaSIB01:RF-LLRF-B:GPIOIntlk-Mon',
                        'Out': 'RA-RaSIB01:RF-LLRF-B:GPIOOut-Mon'
                    }
                },
                'Bypass': {
                    '806': ['Rev SSA 1', 'RA-RaSIB01:RF-LLRF-B:FIMRevSSA1'],
                    '807': ['Rev SSA 2', 'RA-RaSIB01:RF-LLRF-B:FIMRevSSA2'],
                    '808': ['Rev SSA 3', 'RA-RaSIB01:RF-LLRF-B:FIMRevSSA3'],
                    '809': ['Rev SSA 4', 'RA-RaSIB01:RF-LLRF-B:FIMRevSSA4'],
                    '810': ['Rev Cavity', 'RA-RaSIB01:RF-LLRF-B:FIMRevCav'],
                    '811': ['Manual Interlock', 'RA-RaSIB01:RF-LLRF-B:FIMManual'],
                    '812': ['PLC', 'RA-RaSIB01:RF-LLRF-B:FIMPLC'],
                    '813': ['Ext LLRF 1', 'RA-RaSIB01:RF-LLRF-B:FIMLLRF1'],
                    '814': ['Ext LLRF 2', 'RA-RaSIB01:RF-LLRF-B:FIMLLRF2'],
                    '815': ['Ext LLRF 3', 'RA-RaSIB01:RF-LLRF-B:FIMLLRF3'],
                    '816 1': ['End Switch Up 1', 'RA-RaSIB01:RF-LLRF-B:FIMTunnerHigh'],
                    '817 1': ['End Switch Down 1', 'RA-RaSIB01:RF-LLRF-B:FIMTunnerLow'],
                    '816 2': ['End Switch Up 2', 'RA-RaSIB01:RF-LLRF-B:FIMPLG2Up'],
                    '817 2': ['End Switch Down 2', 'RA-RaSIB01:RF-LLRF-B:FIMPLG2Down'],
                    '835': ['ILK VCav', 'RA-RaSIB01:RF-LLRF-B:FIMCav'],
                    '836': ['ILK Fwd Cav', 'RA-RaSIB01:RF-LLRF-B:FIMFwdCav'],
                    '837': ['ILK Fw SSA 1', 'RA-RaSIB01:RF-LLRF-B:FIMFwdSSA1'],
                    '838': ['ILK RF In 7', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn7'],
                    '839': ['ILK RF In 8', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn8'],
                    '840': ['ILK RF In 9', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn9'],
                    '841': ['ILK RF In 10', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn10'],
                    '842': ['ILK RF In 11', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn11'],
                    '843': ['ILK RF In 12', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn12'],
                    '844': ['ILK RF In 13', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn13'],
                    '845': ['ILK RF In 14', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn14'],
                    '846': ['ILK RF In 15', 'RA-RaSIB01:RF-LLRF-B:FIMRFIn15'],
                    '847': ['ILK LLRF Beam Trip', 'RA-RaSIB01:RF-LLRF-B:FIMOrbitIntlk']
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
        }
    },
}
