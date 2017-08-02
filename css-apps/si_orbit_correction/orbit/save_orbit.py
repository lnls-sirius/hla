from org.csstudio.opibuilder.scriptUtil import PVUtil, DataUtil, FileUtil, ConsoleUtil

## Get Orbit Widgets Information
graph_orbit_x = display.getWidget("Graph Orbit X")
graph_orbit_y = display.getWidget("Graph Orbit Y")

orbit_x_pv = graph_orbit_x.getPV()
orbit_y_pv = graph_orbit_y.getPV()


## Save File
try:
    try:
        orbit_x = PVUtil.getDoubleArray(orbit_x_pv)
        orbit_y = PVUtil.getDoubleArray(orbit_y_pv)
        orbit_xy = orbit_x + orbit_y
    except:
        ConsoleUtil.writeError("Graphics PV must be defined. Choose a register first.")
        raise
    file = FileUtil.saveFileDialog(False)
    widget.setPropertyValue("label", file)

    orbit_xy_data = open(file, "w")
    for data in orbit_xy:
        orbit_xy_data.write("%s\n" % data)
    orbit_xy_data.close()
except:
    pass
