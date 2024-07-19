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
            'ASet': 'RA-RaSIA01:RF-LLRF:AmpVCav'
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
        }
    },
}
