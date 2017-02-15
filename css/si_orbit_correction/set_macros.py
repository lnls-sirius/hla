from org.csstudio.opibuilder.scriptUtil import PVUtil, DataUtil, ConsoleUtil

## PVS Database

# External PVs

# Beam Orbit
ref_orbit_x_pv = "SI-GLOB:AP-SOFB.RefOrbX"
orbit_x_pv = "SI-GLOB:AP-SOFB.AvgMeasOrbX"
ref_orbit_x_sel_pv = "SI-GLOB:AP-SOFB.RefOrbXSlot"
ref_orbit_y_pv = "SI-GLOB:AP-SOFB.RefOrbY"
orbit_y_pv = "SI-GLOB:AP-SOFB.AvgMeasOrbY"
ref_orbit_y_sel_pv = "SI-GLOB:AP-SOFB.RefOrbYSlot"
bpm_pos_pv = "VA-SIFK-BPM-POS"

# Orbits
num_samples_pv = "SI-GLOB:AP-SOFB.NrSpl"

# SOFB
sofb_weight_h_pv = "SI-GLOB:AP-SOFB.StrthCH"
sofb_weight_v_pv = "SI-GLOB:AP-SOFB.StrthCV"
sofb_mode_pv = "SI-GLOB:AP-SOFB.OpMode"
sofb_mode_plane_pv = "SI-GLOB:AP-SOFB.RespMatType"
sofb_mode_rffreq_pv = "SI-GLOB:AP-SOFB.RFreqEnbl"
sofb_mancorr_pv = "SI-GLOB:AP-SOFB.ManCorrTrig"
sofb_error_pv = "SI-GLOB:AP-SOFB.Err"

# Features
add_bpm_pv = "SI-GLOB:AP-SOFB.AddBPM"
rmv_bpm_pv = "SI-GLOB:AP-SOFB.RmvBPM"
add_ch_pv = "SI-GLOB:AP-SOFB.AddCH"
rmv_ch_pv = "SI-GLOB:AP-SOFB.RmvCH"
add_cv_pv = "SI-GLOB:AP-SOFB.AddCV"
rmv_cv_pv = "SI-GLOB:AP-SOFB.RmvCV"
enbl_list_bpm_pv = "SI-GLOB:AP-SOFB.EnblListBPM"
enbl_list_ch_pv = "SI-GLOB:AP-SOFB.EnblListCH"
enbl_list_cv_pv = "SI-GLOB:AP-SOFB.EnblListCV"

# Local PVs

# Beam Orbit
ref_orbit_x_locpv = "loc://ref_orbit_x(0)"
orbit_x_locpv = "loc://orbit_x(0)"
delta_orbit_x_locpv = "loc://delta_orbit_x(0)"
ref_orbit_y_locpv = "loc://ref_orbit_y(0)"
orbit_y_locpv = "loc://orbit_y(0)"
delta_orbit_y_locpv = "loc://delta_orbit_y(0)"
rms_x_locpv = "loc://rms_x(0)"
mean_x_locpv = "loc://mean_x(0)"
max_x_locpv = "loc://max_x(0)"
min_x_locpv = "loc://min_x(0)"
rms_y_locpv = "loc://rms_y(0)"
mean_y_locpv = "loc://mean_y(0)"
max_y_locpv = "loc://max_y(0)"
min_y_locpv = "loc://min_y(0)"

# Orbits
register_locpv = "loc://register(0)"
display_mode_locpv = "loc://display_mode(0)"
deviation_register_locpv = "loc://deviation_register(0)"
update_orbit_locpv = "loc://update_orbit(0)"

# SOFB
sofb_corr_h_locpv = "loc://sofb_corr_h(0)"
sofb_corr_v_locpv = "loc://sofb_corr_v(0)"
sofb_corr_coupling_locpv = "loc://sofb_coupling(0)"
sofb_corr_rffreq_locpv = "loc://sofb_corr_freq(0)"

# FOFB
fofb_corr_h_locpv = "loc://fofb_corr_h(0)"
fofb_corr_v_locpv = "loc://fofb_corr_v(0)"
fofb_corr_coupling_locpv = "loc://fofb_coupling(0)"

# Features
feature_type_locpv = "loc://feature_type(0)"


## Control Panel

# Get Widgets
control_panel = display.getWidget("Control Panel")

# Set Macros
control_panel_macros = DataUtil.createMacrosInput(True)
control_panel_macros.put("ref_orbit_x_ioc", ref_orbit_x_pv)
control_panel_macros.put("orbit_x_ioc", orbit_x_pv)
control_panel_macros.put("ref_orbit_x_ioc_sel", ref_orbit_x_sel_pv)
control_panel_macros.put("ref_orbit_y_ioc", ref_orbit_y_pv)
control_panel_macros.put("orbit_y_ioc", orbit_y_pv)
control_panel_macros.put("ref_orbit_y_ioc_sel", ref_orbit_y_sel_pv)
control_panel_macros.put("ref_orbit_x_graph", ref_orbit_x_locpv)
control_panel_macros.put("orbit_x_graph", orbit_x_locpv)
control_panel_macros.put("delta_orbit_x", delta_orbit_x_locpv)
control_panel_macros.put("ref_orbit_y_graph", ref_orbit_y_locpv)
control_panel_macros.put("orbit_y_graph", orbit_y_locpv)
control_panel_macros.put("delta_orbit_y", delta_orbit_y_locpv)
control_panel_macros.put("bpm_pos", bpm_pos_pv)
control_panel_macros.put("register", register_locpv)
control_panel_macros.put("display_mode", display_mode_locpv)
control_panel_macros.put("deviation_register", deviation_register_locpv)
control_panel_macros.put("update_orbit", update_orbit_locpv)
control_panel_macros.put("rms_x", rms_x_locpv)
control_panel_macros.put("mean_x", mean_x_locpv)
control_panel_macros.put("max_x", max_x_locpv)
control_panel_macros.put("min_x", min_x_locpv)
control_panel_macros.put("rms_y", rms_y_locpv)
control_panel_macros.put("mean_y", mean_y_locpv)
control_panel_macros.put("max_y", max_y_locpv)
control_panel_macros.put("min_y", min_y_locpv)
control_panel_macros.put("feature_type", feature_type_locpv)
control_panel_macros.put("num_samples", num_samples_pv)
control_panel_macros.put("sofb_weight_h", sofb_weight_h_pv)
control_panel_macros.put("sofb_weight_v", sofb_weight_v_pv)
control_panel_macros.put("sofb_mode", sofb_mode_pv)
control_panel_macros.put("sofb_mode_plane", sofb_mode_plane_pv)
control_panel_macros.put("sofb_mode_rffreq", sofb_mode_rffreq_pv)
control_panel_macros.put("sofb_mancorr", sofb_mancorr_pv)
control_panel_macros.put("sofb_error", sofb_error_pv)
control_panel_macros.put("add_bpm", add_bpm_pv)
control_panel_macros.put("add_ch", add_ch_pv)
control_panel_macros.put("add_cv", add_cv_pv)
control_panel_macros.put("rmv_bpm", rmv_bpm_pv)
control_panel_macros.put("rmv_ch", rmv_ch_pv)
control_panel_macros.put("rmv_cv", rmv_cv_pv)
control_panel_macros.put("enbl_list_bpm", enbl_list_bpm_pv)
control_panel_macros.put("enbl_list_ch", enbl_list_ch_pv)
control_panel_macros.put("enbl_list_cv", enbl_list_cv_pv)
control_panel.setPropertyValue("macros", control_panel_macros)

# Reload OPI
control_panel.setPropertyValue("opi_file", "control_panel.opi")