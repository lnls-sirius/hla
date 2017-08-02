from org.csstudio.opibuilder.scriptUtil import PVUtil, DataUtil, FileUtil, ConsoleUtil
from time import sleep

numBPM = 160
ref_orbit_x_pv = widget.getMacroValue("ref_orbit_x_ioc")
ref_orbit_x_sel_pv = widget.getMacroValue("ref_orbit_x_ioc_sel")
ref_orbit_y_pv = widget.getMacroValue("ref_orbit_y_ioc")
ref_orbit_y_sel_pv = widget.getMacroValue("ref_orbit_y_ioc_sel")

try:
        orbit_x = DataUtil.createDoubleArray(numBPM)
        orbit_y = DataUtil.createDoubleArray(numBPM)
        orbit_file = widget.getPropertyValue("label")
        if orbit_file == "":
                ConsoleUtil.writeError("Reference orbit must be defined. Load a file first.")
                raise
        orbit_xy_data = open(orbit_file).readlines()
        orbit_x_data, orbit_y_data = orbit_xy_data[:len(orbit_xy_data)//2], orbit_xy_data[len(orbit_xy_data)//2:]
        for i in range(len(orbit_x_data)):
                orbit_x[i] = float(orbit_x_data[i])
        for i in range(len(orbit_y_data)):
                orbit_y[i] = float(orbit_y_data[i])
        PVUtil.writePV(ref_orbit_x_sel_pv, 2)
        sleep(.5)
        PVUtil.writePV(ref_orbit_y_sel_pv, 2)
        sleep(.5)
        PVUtil.writePV(ref_orbit_x_pv, orbit_x)
        sleep(.5)
        PVUtil.writePV(ref_orbit_y_pv, orbit_y)
except:
        pass
