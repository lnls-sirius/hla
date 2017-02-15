from org.csstudio.opibuilder.scriptUtil import PVUtil, WidgetUtil, DataUtil
import os as _os

bpm_fname = _os.path.join('.','fac_files',
'siriusdb', 'recordnames_flatlists', 'dname-bpm.txt')
ch_fname  = _os.path.join('.','fac_files',
'siriusdb', 'recordnames_flatlists', 'dname-ch.txt')
cv_fname  = _os.path.join('.','fac_files',
'siriusdb', 'recordnames_flatlists', 'dname-cv.txt')

def _read_devicename_file(filename):
    with open(filename, 'r') as fp:
        content = fp.read()
    content = content.splitlines()
    devicenames = []
    for line in content:
        line = line.strip()
        if not line or line[0] == '#': continue
        words = line.split()
        devicenames.append(words[0])
    return devicenames


def _get_device_list(device_type):
    if device_type == 'bpm':
        devices = _read_devicename_file(bpm_fname)
    elif device_type == 'ch':
        devices = _read_devicename_file(ch_fname)
    elif device_type == 'cv':
        devices = _read_devicename_file(cv_fname)
    else:
        devices = None
    return devices


bpm_devicenames = _get_device_list('bpm')
ch_devicenames = _get_device_list('ch')
cv_devicenames = _get_device_list('cv')

macro_inputs = DataUtil.createMacrosInput(True)
#macro_inputs.put("device", device)
macro_inputs.put("power_supply_sp", "loc://power_supply_sp")
display.setPropertyValue("macros", macro_inputs)
