from siriuspy.namesys import SiriusPVName
from siriuspy.search import RaBPMSearch

# For AFCv3.1., the PV name follows - $(AREA):$(DIS)-AMC-{1, 3, ..., 12}:
# For AFCv4.0., the PV name follows - $(AREA):$(DIS)-AMC-2:

# AREA=IA-{{01, ..., 20}RaBPM|20RaBPMTL} # Area = LNLS uTCA crates
# DIS=CO  # Discipline = Control

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
    return RaBPMSearch.conv_devname_2_slot(device)


def device2crate(device):
    device = SiriusPVName(device)
    return RaBPMSearch.conv_devname_2_cratename(device)


def get_amc_pair(device):
    device = SiriusPVName(device)
    return RaBPMSearch.get_bpm_pair(device)
