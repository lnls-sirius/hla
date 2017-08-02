from org.csstudio.opibuilder.scriptUtil import PVUtil, DataUtil, ConsoleUtil

register_pv = pvArray[0]
display_mode_pv = pvArray[1]
deviation_register_pv = pvArray[2]
numBPM = 160

## Get Orbit Widgets
graph_orbit_x = display.getWidget("Graph Orbit X")
graph_orbit_y = display.getWidget("Graph Orbit Y")


## Update Graphical Data
try:
        if triggerPV == register_pv:
                register = PVUtil.getString(register_pv)
                registers = widget.getWidget("Register Selection").getPropertyValue("items")
                if register == registers[0]:
                        orbit_x_pv = widget.getMacroValue("orbit_x_ioc")
                        orbit_y_pv = widget.getMacroValue("orbit_y_ioc")
                        trigger = 1
                else:
                        orbit_x_pv = widget.getMacroValue("orbit_x_graph")
                        orbit_y_pv = widget.getMacroValue("orbit_y_graph")
                        orbit_x = DataUtil.createDoubleArray(numBPM)
                        orbit_y = DataUtil.createDoubleArray(numBPM)
                        if register == registers[1] or register == registers[2]:
                                orbit_filename = register[-1] + ".txt"
                                orbit_pathname = "/home/fac_files/hla/sirius/machine_apps/si_sofb/"
                                orbit_x_data = open(orbit_pathname+"reforbit_x/"+orbit_filename).readlines()
                                orbit_y_data = open(orbit_pathname+"reforbit_y/"+orbit_filename).readlines()
                        else:
                                orbit_file = widget.getWidget("Text Reg. " + str(register[-1])).getPropertyValue("label")
                                orbit_xy_data = open(orbit_file).readlines()
                                orbit_x_data, orbit_y_data = orbit_xy_data[:len(orbit_xy_data)//2], orbit_xy_data[len(orbit_xy_data)//2:]
                        for i in range(len(orbit_x_data)):
                                orbit_x[i] = float(orbit_x_data[i])
                        for i in range(len(orbit_y_data)):
                                orbit_y[i] = float(orbit_y_data[i])
                		PVUtil.writePV(orbit_x_pv, orbit_x)
                		PVUtil.writePV(orbit_y_pv, orbit_y)
                		trigger = 2
                graph_orbit_x.setPropertyValue("pv_name", orbit_x_pv)
                graph_orbit_y.setPropertyValue("pv_name", orbit_y_pv)
        else:
                if triggerPV == display_mode_pv:
                        trigger = 3
                elif triggerPV == deviation_register_pv:
                        trigger = 4
                display_mode = PVUtil.getString(display_mode_pv)
                display_modes = widget.getWidget("Display Mode").getPropertyValue("items")
                ref_orbit_x_pv = widget.getMacroValue("ref_orbit_x_graph")
                ref_orbit_y_pv = widget.getMacroValue("ref_orbit_y_graph")
                ref_orbit_x = DataUtil.createDoubleArray(numBPM)
                ref_orbit_y = DataUtil.createDoubleArray(numBPM)
                if display_mode == display_modes[0]:
                        for i in range(numBPM):
                                ref_orbit_x[i] = 0
                                ref_orbit_y[i] = 0
                else:
                        deviation_register = PVUtil.getString(deviation_register_pv)
                        deviation_registers = widget.getWidget("Deviation Register").getPropertyValue("items")
                        if deviation_register == deviation_registers[0] or deviation_register == deviation_registers[1]:
                                ref_orbit_filename = deviation_register[-1] + ".txt"
                                ref_orbit_pathname = "/home/fac_files/hla/sirius/machine_apps/si_sofb/"
                                ref_orbit_x_data = open(ref_orbit_pathname+"reforbit_x/"+ref_orbit_filename).readlines()
                                for i in range(len(ref_orbit_x_data)):
                                        ref_orbit_x[i] = float(ref_orbit_x_data[i])
                                ref_orbit_y_data = open(ref_orbit_pathname+"reforbit_y/"+ref_orbit_filename).readlines()
                                for i in range(len(ref_orbit_y_data)):
                                        ref_orbit_y[i] = float(ref_orbit_y_data[i])
                PVUtil.writePV(ref_orbit_x_pv, ref_orbit_x)
                PVUtil.writePV(ref_orbit_y_pv, ref_orbit_y)
        PVUtil.writePV(widget.getMacroValue("update_orbit"),trigger)
except:
        pass
