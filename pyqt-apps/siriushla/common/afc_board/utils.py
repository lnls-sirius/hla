from siriuspy.namesys import SiriusPVName

# For AFCv3.1., the PV name follows - $(AREA):$(DIS)-AMC-{1, 3, ..., 12}:
# For AFCv4.0., the PV name follows - $(AREA):$(DIS)-AMC-2:

# AREA=IA-{{01, ..., 20}RaBPM|20RaBPMTL} # Area = LNLS uTCA crates
# DIS=CO  # Discipline = Control

BO_N = [1, 3, 6, 8, 11, 13, 16, 18, 21, 23,
        26, 28, 31, 33, 36, 38, 41, 43, 46, 48]

BO_N1 = [n+1 for n in BO_N]

BO_N2 = [n+2 for n in BO_N]

DIS = 'CO'

AFCv3_1_PV_LIST = {
    'sensors': {
        'FMC1Volt12V': 'FMC1Volt12V-Mon',
        'FMC1Volt12VPrs': 'FMC1Volt12VPrs-Cte',
        'FMC1Curr12V': 'FMC1Curr12V-Mon',
        'FMC1Curr12VPrs': 'FMC1Curr12VPrs-Cte',
        'FMC2Volt12V': 'FMC2Volt12V-Mon',
        'FMC2Volt12VPrs': 'FMC2Volt12VPrs-Cte',
        'FMC2Curr12V': 'FMC2Curr12V-Mon',
        'FMC2Curr12VPrs': 'FMC2Curr12VPrs-Cte',
        'FMC1VoltVADJ': 'FMC1VoltVADJ-Mon',
        'FMC1VoltVADJPrs': 'FMC1VoltVADJPrs-Cte',
        'FMC1CurrVADJ': 'FMC1CurrVADJ-Mon',
        'FMC1CurrVADJPrs': 'FMC1CurrVADJPrs-Cte',
        'FMC2VoltVADJ': 'FMC2VoltVADJ-Mon',
        'FMC2VoltVADJPrs': 'FMC2VoltVADJPrs-Cte',
        'FMC2CurrVADJ': 'FMC2CurrVADJ-Mon',
        'FMC2CurrVADJPrs': 'FMC2CurrVADJPrs-Cte',
        'FMC1Volt3V3': 'FMC1Volt3V3-Mon',
        'FMC1Volt3V3Prs': 'FMC1Volt3V3Prs-Cte',
        'FMC1Curr3V3': 'FMC1Curr3V3-Mon',
        'FMC1Curr3V3Prs': 'FMC1Curr3V3Prs-Cte',
        'FMC2Volt3V3': 'FMC2Volt3V3-Mon',
        'FMC2Volt3V3Prs': 'FMC2Volt3V3Prs-Cte',
        'FMC2Curr3V3': 'FMC2Curr3V3-Mon',
        'FMC2Curr3V3Prs': 'FMC2Curr3V3Prs-Cte',
        'TempFPGA': 'TempFPGA-Mon',
        'TempFPGAPrs': 'TempFPGAPrs-Cte',
        'TempUC': 'TempUC-Mon',
        'TempUCPrs': 'TempUCPrs-Cte',
        'TempClkSwitch': 'TempClkSwitch-Mon',
        'TempClkSwitchPrs': 'TempClkSwitchPrs-Cte',
        'TempDCDC': 'TempDCDC-Mon',
        'TempDCDCPrs': 'TempDCDCPrs-Cte',
        'TempRAM': 'TempRAM-Mon',
        'TempRAMPrs': 'TempRAMPrs-Cte',
        'Pwr': 'Pwr-Mon'
    },
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
    'sensors': {
        'AMCVolt12V': 'AMCVolt12V-Mon',
        'AMCVolt12VPrs': 'AMCVolt12VPrs-Cte',
        'AMCCurr12V': 'AMCCurr12V-Mon',
        'AMCCurr12VPrs': 'AMCCurr12VPrs-Cte',
        'RTMVolt12V': 'RTMVolt12V-Mon',
        'RTMVolt12VPrs': 'RTMVolt12VPrs-Cte',
        'RTMCurr12V': 'RTMCurr12V-Mon',
        'RTMCurr12VPrs': 'RTMCurr12VPrs-Cte',
        'FMC1VoltVADJ': 'FMC1VoltVADJ-Mon',
        'FMC1VoltVADJPrs': 'FMC1VoltVADJPrs-Cte',
        'FMC1CurrVADJ': 'FMC1CurrVADJ-Mon',
        'FMC1CurrVADJPrs': 'FMC1CurrVADJPrs-Cte',
        'FMC2VoltVADJ': 'FMC2VoltVADJ-Mon',
        'FMC2VoltVADJPrs': 'FMC2VoltVADJPrs-Cte',
        'FMC2CurrVADJ': 'FMC2CurrVADJ-Mon',
        'FMC2CurrVADJPrs': 'FMC2CurrVADJPrs-Cte',
        'FMC1Volt3V3': 'FMC1Volt3V3-Mon',
        'FMC1Volt3V3Prs': 'FMC1Volt3V3Prs-Cte',
        'FMC1Curr3V3': 'FMC1Curr3V3-Mon',
        'FMC1Curr3V3Prs': 'FMC1Curr3V3Prs-Cte',
        'FMC2Volt3V3': 'FMC2Volt3V3-Mon',
        'FMC2Volt3V3Prs': 'FMC2Volt3V3Prs-Cte',
        'FMC2Curr3V3': 'FMC2Curr3V3-Mon',
        'FMC2Curr3V3Prs': 'FMC2Curr3V3Prs-Cte',
        'TempFPGA': 'TempFPGA-Mon',
        'TempFPGAPrs': 'TempFPGAPrs-Cte',
        'TempUC': 'TempUC-Mon',
        'TempUCPrs': 'TempUCPrs-Cte',
        'TempClkSwitch': 'TempClkSwitch-Mon',
        'TempClkSwitchPrs': 'TempClkSwitchPrs-Cte',
        'TempDCDC': 'TempDCDC-Mon',
        'TempDCDCPrs': 'TempDCDCPrs-Cte',
        'TempRAM': 'TempRAM-Mon',
        'TempRAMPrs': 'TempRAMPrs-Cte',
        'Pwr': 'Pwr-Mon'
    },
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


def device2slot(device):
    device = SiriusPVName(device)

    if device.sec == 'IA':
        if device.dev == 'AMCFPGAEVR':
            return 1
        if device.dev == 'FOFBCtrl':
            return 2

    elif device.sec == 'SI':
        if device.sub[2:] in ['SBFE', 'SPFE', 'SAFE']:
            return 4
        if device.sub[2:] == 'BCFE':
            return 5
        if device.sub.endswith(('SA', 'SB', 'SP')):
            return 6
        if device.sub.endswith(('M1', 'M2')):
            return 7
        if device.sub.endswith(('C1')):
            return 8
        if device.sub.endswith(('C2')) or device.sub.endswith(('C3')) and device.idx == '1':
            return 9
        if device.sub.endswith(('C4')) or device.sub.endswith(('C3')) and device.idx == '2':
            return 10

    elif device.sec == 'TB':
        if device.sub == '01':
            return 6
        if device.sub == '02':
            return 7
        if device.sub in ('03', '04'):
            return 8

    elif device.sec == 'TS':
        if device.sub in ('01', '02'):
            return 9
        if device.sub == '03' or device.sub == '04' and device.idx == '1':
            return 10
        if device.sub == '04' and device.idx == '2':
            return 11

    elif device.sec == 'BO':
        amc_bo = int(device.sub[:2])
        if amc_bo in (BO_N + BO_N1):
            return 11
        if amc_bo in BO_N2:
            return 12


def device2crate(device):
    device = SiriusPVName(device)

    if device.sec in ('TS', 'TB'):
        return 'IA-20RaBPMTL'

    if device.sec == 'BO':
        bo_num = int(device.sub[:2])
        if bo_num in BO_N:
            area_index = BO_N.index(bo_num) + 1
        elif bo_num in BO_N1:
            area_index = BO_N1.index(bo_num) + 1
        elif bo_num in BO_N2:
            area_index = BO_N2.index(bo_num) + 1
        else:
            return None

        area_str = f"{area_index:02}"
        return f'IA-{area_str}RaBPM'

    if device.sec == 'IA':
        return f'IA-{device.sub}'

    return f'IA-{device.sub[:2]}RaBPM'
