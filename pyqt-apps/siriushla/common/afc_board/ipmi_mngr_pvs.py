# For AFCv3.1., the PV name follows - $(AREA):$(DIS)-AMC-{1, 3, ..., 12}:
# For AFCv4.0., the PV name follows - $(AREA):$(DIS)-AMC-2:

# AREA=IA-{{01, ..., 20}RaBPM|20RaBPMTL} # Area = LNLS uTCA crates
# DIS=CO  # Discipline = Control

DIS = 'CO'

list_3_1_sensors = [
    'FMC1Volt12V',
    'FMC1Volt12VPrs',
    'FMC1Curr12V',
    'FMC1Curr12VPrs',
    'FMC2Volt12V',
    'FMC2Volt12VPrs',
    'FMC2Curr12V',
    'FMC2Curr12VPrs',
    'FMC1VoltVADJ',
    'FMC1VoltVADJPrs',
    'FMC1CurrVADJ',
    'FMC1CurrVADJPrs',
    'FMC2VoltVADJ',
    'FMC2VoltVADJPrs',
    'FMC2CurrVADJ',
    'FMC2CurrVADJPrs',
    'FMC1Volt3V3',
    'FMC1Volt3V3Prs',
    'FMC1Curr3V3',
    'FMC1Curr3V3Prs',
    'FMC2Volt3V3',
    'FMC2Volt3V3Prs',
    'FMC2Curr3V3',
    'FMC2Curr3V3Prs',
    'TempFPGA',
    'TempFPGAPrs',
    'TempUC',
    'TempUCPrs',
    'TempClkSwitch',
    'TempClkSwitchPrs',
    'TempDCDC',
    'TempDCDCPrs',
    'TempRAM',
    'TempRAMPrs',
    'Pwr'
]

list_4_0_sensors = [
    'AMCVolt12V',
    'AMCVolt12VPrs',
    'AMCCurr12V',
    'AMCCurr12VPrs',
    'RTMVolt12V',
    'RTMVolt12VPrs',
    'RTMCurr12V',
    'RTMCurr12VPrs',
    'FMC1VoltVADJ',
    'FMC1VoltVADJPrs',
    'FMC1CurrVADJ',
    'FMC1CurrVADJPrs',
    'FMC2VoltVADJ',
    'FMC2VoltVADJPrs',
    'FMC2CurrVADJ',
    'FMC2CurrVADJPrs',
    'FMC1Volt3V3',
    'FMC1Volt3V3Prs',
    'FMC1Curr3V3',
    'FMC1Curr3V3Prs',
    'FMC2Volt3V3',
    'FMC2Volt3V3Prs',
    'FMC2Curr3V3',
    'FMC2Curr3V3Prs',
    'TempFPGA',
    'TempFPGAPrs',
    'TempUC',
    'TempUCPrs',
    'TempClkSwitch',
    'TempClkSwitchPrs',
    'TempDCDC',
    'TempDCDCPrs',
    'TempRAM',
    'TempRAMPrs',
    'Pwr'
]

AFCv3_1_PV_LIST = {
    'sensors': {},
    'FRU': {
        'Status': 'Status-Cte',
        'FruId': 'FruId-Cte',
        'BoardManuf': 'BoardManuf-Cte',
        'BoardName': 'BoardName-Cte',
        'BoardSN': 'BoardSN-Cte',
        'BoardPN': 'BoardPN-Cte',
        'ProdManuf': 'ProdManuf-Cte',
        'ProdName': 'ProdName-Cte',
        'ProdSN': 'ProdSN-Cte',
        'ProdPN': 'ProdPN-Cte',
        'PowerCtl': 'PowerCtl-Sel',
        'SoftRst': 'SoftRst-Cmd',
        'SoftRstSts': 'SoftRstSts-Mon'
    }
}

AFCv4_0_PV_LIST = {
    'sensors': {},
    'FRU': {
        'Status': 'Status-Cte',
        'FruId': 'FruId-Cte',
        'BoardManuf': 'BoardManuf-Cte',
        'BoardName': 'BoardName-Cte',
        'BoardSN': 'BoardSN-Cte',
        'BoardPN': 'BoardPN-Cte',
        'ProdManuf': 'ProdManuf-Cte',
        'ProdName': 'ProdName-Cte',
        'ProdSN': 'ProdSN-Cte',
        'ProdPN': 'ProdPN-Cte',
        'PowerCtl': 'PowerCtl-Sel',
        'SoftRst': 'SoftRst-Cmd',
        'SoftRstSts': 'SoftRstSts-Mon'
    }
}

AFCv3_1_PV_LIST['sensors'] = {sen: sen + ('-Cte' if sen.endswith('Prs') else '-Mon') for sen in list_3_1_sensors}

AFCv4_0_PV_LIST['sensors'] = {sen: sen + ('-Cte' if sen.endswith('Prs') else '-Mon') for sen in list_4_0_sensors}
