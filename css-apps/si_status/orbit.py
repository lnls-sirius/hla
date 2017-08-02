from org.csstudio.opibuilder.scriptUtil import PVUtil, DataUtil
import math

ref_orbit_pv = pvArray[0]
bpm_pos_pv   = pvArray[1]
orbit_pv     = pvArray[2]
y_pv         = pvArray[3]

try:
    bpm_pos   = PVUtil.getDoubleArray(bpm_pos_pv)
    ref_orbit = PVUtil.getDoubleArray(ref_orbit_pv)
    orbit     = PVUtil.getDoubleArray(orbit_pv)
    
    y = DataUtil.createDoubleArray(len(orbit))
    for i in range(len(orbit)):
        y[i] = orbit[i] - ref_orbit[i]
    
    y_pv.setValue(y)
    
    # Set y axis limits
    abs_y = [math.fabs(i) for i in y]
    default = 10
    maximum = max(abs_y) if len(abs_y) > 0 else default
    if maximum <= default:
        widget.setPropertyValue("axis_1_maximum",  default)
        widget.setPropertyValue("axis_1_minimum", -default)
    else:
        widget.setPropertyValue("axis_1_maximum",  maximum)
        widget.setPropertyValue("axis_1_minimum", -maximum)
except:
    pass