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
                'Fast Input': {
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
            'SW Trig': 'RA-RaBO01:RF-LLRF:FDLSwTrig-Mon',
            'HW Trig': 'RA-RaBO01:RF-LLRF:FDLHwTrig-Mon',
            'Trig': 'RA-RaBO01:RF-LLRF:FDLTrig-Cmd',
            'Processing': 'BR-RF-DLLRF-01:FDL:PROCESSING',
            'Rearm': 'BR-RF-DLLRF-01:FDL:REARM',
            'Raw': 'RA-RaBO01:RF-LLRF:FDLRaw-Sel',
            'Qty': 'BR-RF-DLLRF-01:FDL:FrameQty-',
            'Size': 'BR-RF-DLLRF-01:FDL:Size-Mon',
            'Duration': 'BR-RF-DLLRF-01:FDL:Duration-Mon',
            'Delay': 'BR-RF-DLLRF-01:FDL:TriggerDelay'
        },
        'ADCs and DACs': {
            'ADC Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaBO01:RF-LLRF:PhShADC'],
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
            'DAC Enable': ['102 - DACs Phase Shift Enable', 'RA-RaBO01:RF-LLRF:PhShDAC'],
            '14': ['Phase Shift Drive SSA 1', 'RA-RaBO01:RF-LLRF:PHSHSSA1'],
            '18': ['Gain Drive SSA 1', 'RA-RaBO01:RF-LLRF:GainSSA1'],
            '15': ['Phase Shift Drive SSA 2', 'RA-RaBO01:RF-LLRF:PHSHSSA2'],
            '19': ['Gain Drive SSA 2', 'RA-RaBO01:RF-LLRF:GainSSA2'],
            '16': ['Phase Shift Drive SSA 3', 'RA-RaBO01:RF-LLRF:PHSHSSA3'],
            '20': ['Gain Drive SSA 3', 'RA-RaBO01:RF-LLRF:GainSSA3'],
            '17': ['Phase Shift Drive SSA 4', 'RA-RaBO01:RF-LLRF:PHSHSSA4'],
            '21': ['Gain Drive SSA 4', 'RA-RaBO01:RF-LLRF:GainSSA4']
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
                'Mode': 'RA-RaBO01:RF-LLRF:LoopMode-Sts'
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
                    'Input': {
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
                    'Fast Input': {
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
                    'Fast Input': {
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
                'SW Trig': 'RA-RaSIA01:RF-LLRF-A:FDLSwTrig-Mon',
                'HW Trig': 'RA-RaSIA01:RF-LLRF-A:FDLHwTrig-Mon',
                'Trig': 'RA-RaSIA01:RF-LLRF-A:FDLTrig-Cmd',
                'Processing': 'SR-RF-DLLRF-01:FDL:PROCESSING',
                'Rearm': 'SR-RF-DLLRF-01:FDL:REARM',
                'Raw': 'RA-RaSIA01:RF-LLRF-A:FDLRaw',
                'Qty': 'SR-RF-DLLRF-01:FDL:FrameQty-',
                'Size': 'SR-RF-DLLRF-01:FDL:Size-Mon',
                'Duration': 'SR-RF-DLLRF-01:FDL:Duration-Mon',
                'Delay': 'SR-RF-DLLRF-01:FDL:TriggerDelay',
                'Name': 'A',
            },
            'B': {
                'Signals': (
                    ('Cav', 'SR-RF-DLLRF-02:FDL:CAV:AMP', 'SR-RF-DLLRF-02:FDL:CAV:PHS', 'blue'),
                    ('Fwd Cav', 'SR-RF-DLLRF-02:FDL:FWDCAV:AMP', 'SR-RF-DLLRF-02:FDL:FWDCAV:PHS', 'red'),
                    ('Rev Cav', 'SR-RF-DLLRF-02:FDL:REVCAV:AMP', 'SR-RF-DLLRF-02:FDL:REVCAV:PHS', 'darkSlateBlue'),
                    ('Fwd Ssa', 'SR-RF-DLLRF-02:FDL:FWDSSA:AMP', 'SR-RF-DLLRF-02:FDL:FWDSSA:PHS', 'darkGreen'),
                    ('Rev Ssa', 'SR-RF-DLLRF-02:FDL:REVSSA:AMP', 'SR-RF-DLLRF-02:FDL:REVSSA:PHS', 'magenta'),
                    ('Ctrl', 'SR-RF-DLLRF-02:FDL:CTRL:AMP', 'SR-RF-DLLRF-02:FDL:CTRL:PHS', 'darkCyan'),
                    ('Ref', 'SR-RF-DLLRF-02:FDL:SL:REF:AMP', 'SR-RF-DLLRF-02:FDL:SL:REF:PHS', 'darkRed'),
                    ('Err', 'SR-RF-DLLRF-02:FDL:SL:ERR:AMP', 'SR-RF-DLLRF-02:FDL:SL:ERR:PHS', 'purple'),
                    ('Err Acc', 'SR-RF-DLLRF-02:FDL:SL:ERRACC:AMP', 'SR-RF-DLLRF-02:FDL:SL:ERRACC:PHS', 'saddlebrown'),
                    ('MO', 'SR-RF-DLLRF-02:FDL:MO:AMP', 'SR-RF-DLLRF-02:FDL:MO:PHS', 'darkBlue'),
                    ('Tune', None, 'SR-RF-DLLRF-02:FDL:TUNE:DEPHS', 'orangered'),
                    ('Tune Filt', None, 'SR-RF-DLLRF-02:FDL:TUNE:DEPHS:FILT', 'darkOliveGreen')
                ),
                'Time': 'SR-RF-DLLRF-02:FDL:SCALE:32',
                'Mode': 'SR-RF-DLLRF-02:FDL:MODE',
                'SW Trig': 'RA-RaSIB01:RF-LLRF-B:FDLSwTrig-Mon',
                'HW Trig': 'RA-RaSIB01:RF-LLRF-B:FDLHwTrig-Mon',
                'Trig': 'RA-RaSIB01:RF-LLRF-B:FDLTrig-Cmd',
                'Processing': 'SR-RF-DLLRF-02:FDL:PROCESSING',
                'Rearm': 'SR-RF-DLLRF-02:FDL:REARM',
                'Raw': 'RA-RaSIB01:RF-LLRF-B:FDLRaw',
                'Qty': 'SR-RF-DLLRF-02:FDL:FrameQty-',
                'Size': 'SR-RF-DLLRF-02:FDL:Size-Mon',
                'Duration': 'SR-RF-DLLRF-02:FDL:Duration-Mon',
                'Delay': 'SR-RF-DLLRF-02:FDL:TriggerDelay',
                'Name': 'B',
            }
        },
        'ADCs and DACs': {
            'A': {
                'ADC Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaSIA01:RF-LLRF-A:PhShADC'],
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
                'DAC Enable': ['102 - DACs Phase Shift Enable', 'RA-RaSIA01:RF-LLRF-A:PhShDAC'],
                '14': ['Phase Shift Drive SSA 1', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA1'],
                '18': ['Gain Drive SSA 1', 'RA-RaSIA01:RF-LLRF-A:GainSSA1'],
                '15': ['Phase Shift Drive SSA 2', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA2'],
                '19': ['Gain Drive SSA 2', 'RA-RaSIA01:RF-LLRF-A:GainSSA2'],
                '16': ['Phase Shift Drive SSA 3', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA3'],
                '20': ['Gain Drive SSA 3', 'RA-RaSIA01:RF-LLRF-A:GainSSA3'],
                '17': ['Phase Shift Drive SSA 4', 'RA-RaSIA01:RF-LLRF-A:PHSHSSA4'],
                '21': ['Gain Drive SSA 4', 'RA-RaSIA01:RF-LLRF-A:GainSSA4']
            },
            'B': {
                'ADC Enable': ['101 - ADCs Phase Shift Enable', 'RA-RaSIB01:RF-LLRF-B:PhShADC'],
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
                'DAC Enable': ['102 - DACs Phase Shift Enable', 'RA-RaSIB01:RF-LLRF-B:PhShDAC'],
                '14': ['Phase Shift Drive SSA 1', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA1'],
                '18': ['Gain Drive SSA 1', 'RA-RaSIB01:RF-LLRF-B:GainSSA1'],
                '15': ['Phase Shift Drive SSA 2', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA2'],
                '19': ['Gain Drive SSA 2', 'RA-RaSIB01:RF-LLRF-B:GainSSA2'],
                '16': ['Phase Shift Drive SSA 3', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA3'],
                '20': ['Gain Drive SSA 3', 'RA-RaSIB01:RF-LLRF-B:GainSSA3'],
                '17': ['Phase Shift Drive SSA 4', 'RA-RaSIB01:RF-LLRF-B:PHSHSSA4'],
                '21': ['Gain Drive SSA 4', 'RA-RaSIB01:RF-LLRF-B:GainSSA4']
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
                    'Mode': 'RA-RaSIA01:RF-LLRF-A:LoopMode-Sts'
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
                    'Mode': 'RA-RaSIB01:RF-LLRF-B:LoopMode-Sts'
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
                }
            },
        },
        'RampDtls': {
            'A': {
                'Controls': {
                    'Ramp Enable': 'RA-Ra$(sys)$(sidx)01:$(llrf):RmpEn',
                    'Ramp Down Disable': 'RA-Ra$(sys)$(sidx)01:$(llrf):RampDownDsbl',
                    '356': ['T1 Ramp Delay After Trig', 'RA-Ra$(sys)$(sidx)01:$(llrf):RmpTs1'],
                    '357': ['T2 Ramp Up', 'RA-Ra$(sys)$(sidx)01:$(llrf):RmpTs2'],
                    '358': ['T3 Ramp Top', 'RA-Ra$(sys)$(sidx)01:$(llrf):RmpTs3'],
                    '359': ['T4 Ramp Down', 'RA-Ra$(sys)$(sidx)01:$(llrf):RmpTs4'],
                    '360': ['Ramp Increase Rate', 'RA-Ra$(sys)$(sidx)01:$(llrf):RmpIncTime'],
                    '164': ['Ref Top', 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopAmp-Mon', 'red'],
                    '362 mV': ['Amp Ramp Top (mV)', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampAmpTop'],
                    '362 Vgap': ['Amp Ramp Top (Vgap)', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampAmpTopVGap'],
                    '364': ['Phase Ramp Top', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampPhsTop'],
                    '184': ['Ref Bot', 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotAmp-Mon', 'blue'],
                    '361 mV': ['Amp Ramp Bot (mV)', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampAmpBot'],
                    '361 Vgap': ['Amp Ramp Bot (Vgap)', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampAmpBotVGap'],
                    '363': ['Phase Ramp Bot', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampPhsBot'],
                    '536': ['Ramp Top', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampTop-Mon', 'green'],
                    '533': ['Ramp Ready', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampRdy-Mon'],
                    '365': ['Amp Ramp Up Slope', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampAmpUpCnt'],
                    '366': ['Amp Ramp Down Slope', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampAmpDownCnt'],
                    '367': ['Phase Ramp Up Slope', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampPhsUpCnt'],
                    '368': ['Phase Ramp Down Slope', 'RA-Ra$(sys)$(sidx)01:$(llrf):RampPhsDownCnt']
                },
                'Diagnostics': {
                    'Top': {
                        '164': {
                            'Label': 'Ref',
                            'InPhs': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopI-Mon',
                            'Quad': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopQ-Mon',
                            'Amp1': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopAmp-Mon',
                            'Amp2': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopAmpW-Mon',
                            'Amp3': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopAmpdBm-Mon',
                            'Phs': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefTopPhs-Mon'
                        },
                        '150': {
                            'Label': 'Cell 3',
                            'InPhs': '$(cav):PwrTopI-Mon',
                            'Quad': '$(cav):PwrTopQ-Mon',
                            'Amp1': '$(cav):PwrTopAmp-Mon',
                            'Amp2': '$(cav):PwrTopAmpW-Mon',
                            'Amp3': '$(cav):PwrTopAmpdBm-Mon',
                            'Phs': '$(cav):PwrTopPhs-Mon'
                        },
                        '152': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdTopI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdTopQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                        },
                        '154': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevTopI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevTopQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevTopAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevTopPhs-Mon'
                        },
                        '190': {
                            'Label': 'Fwd Cavity',
                            'InPhs': '$(cav):PwrFwdTopI-Mon',
                            'Quad': '$(cav):PwrFwdTopQ-Mon',
                            'Amp1': '$(cav):PwrFwdTopAmp-Mon',
                            'Amp2': '$(cav):PwrFwdTopAmpW-Mon',
                            'Amp3': '$(cav):PwrFwdTopAmpdBm-Mon',
                            'Phs': '$(cav):PwrFwdTopPhs-Mon'
                        },
                        '156': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdTopI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdTopQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdTopAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdTopAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdTopAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdTopPhs-Mon'
                        },
                        '158': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs':  'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevTopI-Mon',
                            'Quad':  'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevTopQ-Mon',
                            'Amp1':  'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevTopAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevTopAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevTopAmpdBm-Mon',
                            'Phs':  'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevTopPhs-Mon'
                        },
                        '160': {
                            'Label': 'Rev Cavity',
                            'InPhs': '$(cav):PwrRevTopI-Mon',
                            'Quad': '$(cav):PwrRevTopQ-Mon',
                            'Amp1': '$(cav):PwrRevTopAmp-Mon',
                            'Amp2': '$(cav):PwrRevTopAmpW-Mon',
                            'Amp3': '$(cav):PwrRevTopAmpdBm-Mon',
                            'Phs': '(cav):PwrRevTopPhs-Mon'
                        },
                        '168': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrTopI-Mon',
                            'Quad': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrTopQ-Mon',
                            'Amp1': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrTopAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrTopPhs-Mon'
                        },
                        '166': {
                            'Label': 'Control',
                            'InPhs': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlTopI-Mon',
                            'Quad': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlTopQ-Mon',
                            'Amp1': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlTopAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlTopPhs-Mon'
                        },
                        '162': {
                            'Label': 'Tuning Dephase',
                            'PV': 'RA-Ra$(sys)$(sidx)01:$(llrf):TuneDephsTop-Mon'
                        },
                        '163': {
                            'Label': 'FF Error',
                            'PV': 'RA-Ra$(sys)$(sidx)01:$(llrf):FFErrTop-Mon'
                        },
                        '531': {
                            'Label': '5 Hz Trigger',
                            'PV': 'RA-Ra$(sys)$(sidx)01:$(llrf):RampTrigger-Mon'
                        }
                    },
                    'Bot': {
                        '184': {
                            'Label': 'Ref',
                            'InPhs': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotI-Mon',
                            'Quad': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotQ-Mon',
                            'Amp1': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotAmp-Mon',
                            'Amp2': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotAmpW-Mon',
                            'Amp3': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotAmpdBm-Mon',
                            'Phs': 'RA-Ra$(sys)$(sidx)01:$(llrf):RefBotPhs-Mon'
                        },
                        '170': {
                            'Label': 'Cell 3',
                            'InPhs': '$(cav):PwrBotI-Mon',
                            'Quad': '$(cav):PwrBotQ-Mon',
                            'Amp1': '$(cav):PwrBotAmp-Mon',
                            'Amp2': '$(cav):PwrBotAmpW-Mon',
                            'Amp3': '$(cav):PwrBotAmpdBm-Mon',
                            'Phs': '$(cav):PwrBotPhs-Mon'
                        },
                        '172': {
                            'Label': 'Cell 2',
                            'InPhs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdBotI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdBotQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                        },
                        '174': {
                            'Label': 'Cell 4',
                            'InPhs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevBotI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevBotQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevBotAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)02:RF-SSAmpTower:PwrRevBotPhs-Mon'
                        },
                        '192': {
                            'Label': 'Fwd Cavity',
                            'InPhs': '$(cav):PwrFwdBotI-Mon',
                            'Quad': '$(cav):PwrFwdBotQ-Mon',
                            'Amp1': '$(cav):PwrFwdBotAmp-Mon',
                            'Amp2': '$(cav):PwrFwdBotAmpW-Mon',
                            'Amp3': '$(cav):PwrFwdBotAmpdBm-Mon',
                            'Phs': '$(cav):PwrFwdBotPhs-Mon'
                        },
                        '176': {
                            'Label': 'Fwd Pwr SSA 1',
                            'InPhs': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdBotI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdBotQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdBotAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdBotAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdBotAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrFwdBotPhs-Mon'
                        },
                        '178': {
                            'Label': 'Rev Pwr SSA 1',
                            'InPhs': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevBotI-Mon',
                            'Quad': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevBotQ-Mon',
                            'Amp1': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevBotAmp-Mon',
                            'Amp2': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevBotAmpW-Mon',
                            'Amp3': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevBotAmpdBm-Mon',
                            'Phs': 'RA-To$(sys)$(sidx)01:RF-SSAmpTower:PwrRevBotPhs-Mon'
                        },
                        '180': {
                            'Label': 'Rev Cavity',
                            'InPhs': '$(cav):PwrRevBotI-Mon',
                            'Quad': '$(cav):PwrRevBotQ-Mon',
                            'Amp1': '$(cav):PwrRevBotAmp-Mon',
                            'Amp2': '$(cav):PwrRevBotAmpW-Mon',
                            'Amp3': '$(cav):PwrRevBotAmpdBm-Mon',
                            'Phs': '$(cav):PwrRevBotPhs-Mon'
                        },
                        '188': {
                            'Label': 'Loop Error',
                            'InPhs': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrBotI-Mon',
                            'Quad': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrBotQ-Mon',
                            'Amp1': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrBotAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-Ra$(sys)$(sidx)01:$(llrf):ErrBotPhs-Mon'
                        },
                        '186': {
                            'Label': 'Control',
                            'InPhs': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlBotI-Mon',
                            'Quad': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlBotQ-Mon',
                            'Amp1': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlBotAmp-Mon',
                            'Amp2': '-',
                            'Amp3': '-',
                            'Phs': 'RA-Ra$(sys)$(sidx)01:$(llrf):CtrlBotPhs-Mon'
                        },
                        '183': {
                            'Label': 'FF Error',
                            'PV': 'RA-Ra$(sys)$(sidx)01:RF-LLRF:FFErrBot-Mon'
                        },
                        '531': {
                            'Label': '5 Hz Trigger',
                            'PV': 'RA-Ra$(sys)$(sidx)01:$(llrf):RampTrigger-Mon'
                        }
                    }
                }
            },
            'B': {
            }
        }
    },
}
