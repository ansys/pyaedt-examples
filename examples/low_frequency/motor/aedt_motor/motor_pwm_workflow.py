# # PWM Losses Calculation in a Permanent Magnet Machine
#
# This example covers the workflow to compute the PWM losses in an IPM motor, using the Maxwell 2D model and the SVPWM
# feature to automatically generate the voltage waveform for each operating point.
#
# A set of operating points is defined containing the information of the stator current peak and phase advance for each
# torque/speed combination selected for the PWM analysis.
#
# The purpose of this workflow is producing the machine loss maps considering the PWM voltage supply. The set of points
# to simulate is selected by the user and requires to define the operating points with speed and current
# (amplitude and phase). The parametric analysis is carried out using the Maxwell Optimetrics feature to enable parallel
# simulations.
#
# The procedure is divided into two main steps:
#
# - **Current-Driven Simulations**. Every operating point selected for PWM analysis is first analysed with a current
# driven simulation. The stator current (amplitude and phase advance) and speed are imposed to derive the voltage
# required to apply the reference current.
#
# - **PWM Simulations**. The voltage analysis, carried out in the previous step, derives the amplitude and phase of
# voltage first harmonic required in each operating point to inject the reference current. The voltage definition is
# used to generate the PWM voltage. The simulations are repeated in each operating point, supplying the machine with the
# PWM and extracting the machine losses.

# Keywords: **Maxwell 2D**, **transient**, **motor**

# ## Prerequisites
#
# ### Perform imports

# +

import csv
import os
import tempfile
import time

import ansys.aedt.core
import numpy as np
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.generic.file_utils import write_csv

# -

# ### Define Constants

# #### AEDT constants

AEDT_VERSION = "2026.1"
NUM_CORES = 4
NG_MODE = False  # Open AEDT UI when it is launched.

# ### Create temporary directory and define filenames
#
# Create a temporary working directory.
# The name of the working folder is stored in ``temp_folder.name``.
#
# > **Note:** The final cell in the notebook cleans up the temporary folder. If you want to
# > retrieve the AEDT project and data, do so before executing the final cell in the notebook.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Model preparation
#
# ### Download the example project file
#
# Many PyAEDT examples use project files or data from the
# [Ansys example data repository](https://www.github.com/ansys/example-data)
# in GitHub.
#
# > *Note:* You can update ``settings`` as shown below
# > to work with a local copy of the
# > [example-data](https://github.com/ansys/example-data) repository.
# > Replace ``'/home/user/repo/example-data'`` with
# > the path to the cloned ``"example-data"`` repository.
#
# ``` python
# from ansys.aedt.core import settings
# settings.use_example_data = True
# settings.local_example_folder = r'/home/user/repo/example-data'
# ```

# Retrieve the example model and place
# it in the project folder.

aedt_file = download_file(
    source="maxwell_pwm_wf",
    name="model.aedt",
    local_path=temp_folder.name,
)

OPERATING_POINTS_FILENAME = "OperatingPoints"
OPERATING_POINTS_FILE = os.path.join(temp_folder.name, OPERATING_POINTS_FILENAME + ".csv")

# #### Model constants

# Stator winding total resistance [Ohm]
STATOR_RESISTANCE = 0.01958

# Stator winding 2D resistance [Ohm]
STATOR_RESISTANCE_2D = 0.01237

# End-winding inductace [H]
END_WINDING_INDUCTANCE = 0.001868 / 1000

# Pole pairs
POLE_PAIRS = 4

# #### Define constants for the current driven simulation
#
# The current driven simulation is carried out over 1 full electrical cycle. The outputs (torque, flux linkage) are
# computed over the last 1/6th of the period.

# Fraction of electric period to simulate
CD_PERIOD_MULTIPLIER = 1

# Points per electrical cycle
CD_NUM_TORQUE_POINTS_PER_CYCLE = 30

# starting point for performing the average on the resulting curves.
CD_PERIOD_MULTIPLIER_START = 5 / 6

# end point for the average calculation.
CD_PERIOD_MULTIPLIER_END = CD_PERIOD_MULTIPLIER

# current driven optimetrics file name and path
CD_OPTIMETRICS_CSV_FILENAME = "Optimetrics_CD"
CD_OPTIMETRICS_CSV_FILE = os.path.join(CD_OPTIMETRICS_CSV_FILENAME + ".csv")
CD_OPTIMETRICS_CSV_PATH = os.path.join(temp_folder.name, CD_OPTIMETRICS_CSV_FILE)

# current driven Maxwell model name
CD_DESIGN_NAME = "Sinusoidal_Current"

# #### Define constants for the PWM voltage simulation
#
# The following constants determine both the PWM voltage definition and the simulation settings. The Maxwell tab to
# define the PWM voltage for the simulation is the following:

# <img src="_static/motor_pwm_workflow/PWM_UI_Maxwell.svg" alt="" width="600">

# The winding definition must be done using the PWM option:

# <img src="_static/motor_pwm_workflow/winding_setting.svg" alt="" width="600">

# - "BusDC" = PWM_BUS_DC_VOLTAGE * PWM_BUS_DC_MULTIPLIER.
# - "PhaseVoltagePeak" is the amplitude of the fundamental voltage to generate. Changed for each operating point as a
# variable in the Optimetrics.
# - "PhaseVoltageAngle" is the phase of the reference voltage. Changed for each operating point as a  variable in the
# Optimetrics.
# - The reference voltage equation is: <img src="_static/motor_pwm_workflow/reference_voltage_equation.svg" alt="" width="200">
# - "StatorFrequency" is changed for each operating point as a variable in the Optimetrics.
# - SwitchingFrequency = PWM_SWITCHING_FREQUENCY
# - Tmin = PWM_TMIN is the minimum time step used to sample the PWM voltage. The software automatically applies it in
# proximity of the switching event to have high points density around the voltage variation. In this example, it  is
# defined as 1/100th of the switching period.
# - Tmax = PWM_TMAX is the maximum time step used to sample the PWM voltage. The software automatically applies it when
# the voltage is constant after the switching event. This variable time step approach allows to reduce the simulation
# time, still applying carefully the PWM voltage. In this example, the maximum time step is 3 times the minimum time
# step.

# Switching Frequency [Hz]
PWM_SWITCHING_FREQUENCY = 10000

# Switching Period [1/s]
PWM_SWITCHING_PERIOD = 1 / PWM_SWITCHING_FREQUENCY

# ratio between maximum and minimum time step
PWM_TMAX_TMIN_RATIO = 3

# minimum time-step for PWM simulations
PWM_TMIN = PWM_SWITCHING_PERIOD / 20

# maximum time-step for PWM simulations
PWM_TMAX = PWM_TMAX_TMIN_RATIO * PWM_TMIN

# Bus DC voltage and the multiplier to account the inverter voltage drop.
PWM_BUS_DC_VOLTAGE = 720
PWM_BUS_DC_MULTIPLIER = 0.97

# The PWM voltage driven simulation is carried out over 2 electric periods to allow all the losses and induced
# currents to converge. All the outputs (iron, copper and magnet losses) are averaged over the last period.

# Fraction of electric period to simulate in the PWM simulation
PWM_PERIOD_MULTIPLIER = 2

# starting points for the average window.
PWM_PERIOD_MULTIPLIER_START = 1

# end points for the average window.
PWM_PERIOD_MULTIPLIER_END = PWM_PERIOD_MULTIPLIER

# current driven optimetrics file name and path
PWM_OPTIMETRICS_CSV_FILENAME = "Optimetrics_PWM"
PWM_OPTIMETRICS_CSV_FILE = os.path.join(PWM_OPTIMETRICS_CSV_FILENAME + ".csv")
PWM_OPTIMETRICS_CSV_PATH = os.path.join(temp_folder.name, PWM_OPTIMETRICS_CSV_FILE)

# current driven Maxwell model name
PWM_DESIGN_NAME = "PWM_Voltage"

# cPWM simulations results file name and path
OUTPUT_PWM_CSV_FILENAME = "PWM_losses"
OUTPUT_PWM_CSV_FILE = os.path.join(temp_folder.name, OUTPUT_PWM_CSV_FILENAME + ".csv")
OUTPUT_PWM_CSV_PATH = os.path.join(temp_folder.name, OUTPUT_PWM_CSV_FILE)

# #### Define common output variables for both current driven and PWM simulations
#
# - "ThetaED" is the dq reference frame position in electric degrees.
# - "PsiD" is the d-axis flux linkage.
# - "PsiQ" is the d-axis flux linkage.
# - "TorqueDQ" is the torque calculated from the d- and q- axis current and flux linkage.
# - "ThetaED" is the dq reference frame position in electric degrees.
# - "StatorHy" is the stator hysteresis losses. Every portion of the stator must be added in the definition
# - "StatorEddy" is the stator eddy current losses. Every portion of the stator must be added in the definition
# - "RotorEddy" is the rotor eddy current losses. Every portion of the rotor must be added in the definition
# - "MagLoss" is the magnet losses. Every magnet must be added in the definition.
# - "WindingLoss" is the solid winding losses.

output_vars = {
    "ThetaED": "((pi * MachineRPM/1rpm*NumPoles / 60*time)) + pi",
    "PsiD": "2/3*(FluxLinkage(WG_Ph1_P1)*cos(ThetaED)+FluxLinkage(WG_Ph2_P1)*cos(ThetaED - 120deg)+FluxLinkage(WG_Ph3_P1)*cos(ThetaED - 240deg))",
    "PsiQ": "2/3*(FluxLinkage(WG_Ph1_P1)*-sin(ThetaED)+FluxLinkage(WG_Ph2_P1)*-sin(ThetaED - 120deg)+FluxLinkage(WG_Ph3_P1)*-sin(ThetaED - 240deg))",
    "TorqueDQ": "3/2*NumPoles/2*(PsiD*Iq_peak - PsiQ*Id_peak)",
    "StatorHy": "HysteresisLoss(Stator_1) + HysteresisLoss(Stator_2)",
    "StatorEddy": "EddyCurrentLoss(Stator_1) + EddyCurrentLoss(Stator_2)",
    "RotorHy": "HysteresisLoss(Rotor_1) + HysteresisLoss(Rotor_2) + HysteresisLoss(Rotor_3)",
    "RotorEddy": "EddyCurrentLoss(Rotor_1) + EddyCurrentLoss(Rotor_2) + EddyCurrentLoss(Rotor_3)",
    "MagLoss": "SolidLoss(L1_1Magnet1N1_1) + SolidLoss(L1_1Magnet2N1_1) + SolidLoss(L2_1Magnet1N1_1) + SolidLoss(L2_1Magnet2N1_1)",
    "WindingLoss": "PerWindingSolidLoss(WG_Ph1_P1) + PerWindingSolidLoss(WG_Ph2_P1) + PerWindingSolidLoss(WG_Ph3_P1)",
}

# ## Define The Operating Points

OPERATING_POINTS = [
    ['MachineRPM', 'PhaseAdvance', 'IPeak'],
    ['15000', '79.41244351', '231.129587'],
    # ['15000', '75.66628551', '308.3753812'],
    # ['15000', '75.39984866', '411.7977408'],
    # ['15000', '77.59084809', '578.0743934'],
    ['15000', '78.96214049', '645.8155811']
]

# ## Run the Current Driven Optimetrics

# ### Write the csv file containing the operating points for the current driven optimetrics

rows = OPERATING_POINTS[1:]  # skip header
speed_str_vec, phase_advance_str_vec, peak_current_str_vec = map(list, zip(*rows))

speed_str_vec_uom = [x + "rpm" for x in speed_str_vec]
phase_advance_str_vec_uom = [x + "deg" for x in phase_advance_str_vec]
peak_current_str_vec_uom = [x + "A" for x in peak_current_str_vec]

header_current_driven = OPERATING_POINTS[0]
operating_points_current_driven_uom = [header_current_driven] + [
    list(row) for row in zip(speed_str_vec_uom, phase_advance_str_vec_uom, peak_current_str_vec_uom)
]

n_OPpoints = len(operating_points_current_driven_uom) - 1  # exclude header

left_col = ['*'] + [str(i) for i in range(1, n_OPpoints + 1)]

optimetrics_current_driven_list = [
    [left_col[i]] + operating_points_current_driven_uom[i]
    for i in range(len(operating_points_current_driven_uom))
]

write_csv(CD_OPTIMETRICS_CSV_PATH, optimetrics_current_driven_list)

# ### Launch Maxwell 2D
# Launch AEDT and Maxwell 2D after first setting up the project, the version and the graphical mode.

m2d = ansys.aedt.core.Maxwell2d(
    project=aedt_file,
    version=AEDT_VERSION,
    design=CD_DESIGN_NAME,
    solution_type="TransientXY",
    new_desktop=True,
    non_graphical=NG_MODE,
)

# ### Define the variables in the model

# Define how many periods to simulate.
m2d["PeriodMultiplier"] = CD_PERIOD_MULTIPLIER

# Define the number of points per cycle.
m2d["NumTorquePointsPerCycle"] = CD_NUM_TORQUE_POINTS_PER_CYCLE

# The following variables are defined with their expression, since they will be changed at each iteration of the
# Optimetrics analysis.
# - The stator frequency is defined according to the machine speed, which changes at every iteration.
# - The stop time is defined according to the stator frequency and the number of periods to simulate.
# - The time step is here defined as an example. It will be overwritten by the SVPWM feature automatically.

m2d.variable_manager["StatorFrequency"].expression = "NumPoles/2*MachineRPM/1rpm/60" + "*1Hz"
CD_StopTimeExp = "1/StatorFrequency*1Hz*1s*PeriodMultiplier"
CD_TimeStepExp = "1/StatorFrequency*1Hz*1s/NumTorquePointsPerCycle"

# ### Define the simulation setup

# Create the new setup
setup_name = "MySetupAuto"
setup = m2d.create_setup(name=setup_name)
setup.props["StopTime"] = str(CD_StopTimeExp)
setup.props["TimeStep"] = str(CD_TimeStepExp)
setup.props["NonlinearSolverResidual"] = "0.00000001"
setup.props["OutputPerObjectCoreLoss"] = True
setup.props["OutputPerObjectSolidLoss"] = True
setup.update()

# ### Define output variables

for k, v in output_vars.items():
    m2d.create_output_variable(k, v)

# Define the transformation from ABC to dq currents. In the current driven simulation, use the command "InputCurrent".
m2d.create_output_variable("Id_peak", "2/3*(InputCurrent(WG_Ph1_P1)*cos(ThetaED)+InputCurrent(WG_Ph2_P1)*cos(ThetaED - 120deg)+InputCurrent(WG_Ph3_P1)*cos(ThetaED - 240deg))")
m2d.create_output_variable("Iq_peak", "2/3*(InputCurrent(WG_Ph1_P1)*-sin(ThetaED)+InputCurrent(WG_Ph2_P1)*-sin(ThetaED - 120deg)+InputCurrent(WG_Ph3_P1)*-sin(ThetaED - 240deg))")

# ### Import and run the optimetrics analysis

# Import the csv file.
param_sweep = m2d.parametrics.add_from_file(CD_OPTIMETRICS_CSV_PATH, name=CD_OPTIMETRICS_CSV_FILENAME)

# Run the parametric analysis
param_sweep.analyze(cores=NUM_CORES, tasks=NUM_CORES, use_auto_settings=False)

# ## Execute the current driven optimetrics post-processing

variations = {"MachineRPM": "All", "PhaseAdvance": "All", "IPeak": "All"}

data_Id = m2d.post.get_solution_data(
    expressions=["Id_peak"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_Iq = m2d.post.get_solution_data(
    expressions=["Iq_peak"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_Fd = m2d.post.get_solution_data(
    expressions=["PsiD"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_Fq = m2d.post.get_solution_data(
    expressions=["PsiQ"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

id_vec = np.zeros(n_OPpoints)
iq_vec = np.zeros(n_OPpoints)
fd_vec = np.zeros(n_OPpoints)
fq_vec = np.zeros(n_OPpoints)

for OPidx in range(n_OPpoints):

    ## ---------- GET CURRENT DATA ---------- ##
    data_Id.active_variation = data_Id.variations[OPidx]

    time = data_Id.get_expression_data(formula="magnitude")[0]  # get the X axis (time)
    time_last_index = len(time)  # last simulated time instant
    time_frame = time[-1] * CD_PERIOD_MULTIPLIER_START / CD_PERIOD_MULTIPLIER_END
    time_frame_index = np.abs(time - time_frame).argmin()  # index for the time frame

    Id_values = data_Id.get_expression_data(formula="real")[1]
    Id_vec = Id_values[time_frame_index:time_last_index]
    Id_mean = sum(Id_vec) / len(Id_vec)

    data_Iq.active_variation = data_Iq.variations[OPidx]
    Iq_values = data_Iq.get_expression_data(formula="real")[1]
    Iq_vec = Iq_values[time_frame_index:time_last_index]
    Iq_mean = sum(Iq_vec) / len(Iq_vec)

    ## ---------- GET FLUX DATA ---------- ##
    data_Fd.active_variation = data_Fd.variations[OPidx]
    Fd_values = data_Fd.get_expression_data(formula="real")[1]
    Fd_vec = Fd_values[time_frame_index:time_last_index]
    Fd_mean = sum(Fd_vec) / len(Fd_vec)

    data_Fq.active_variation = data_Fq.variations[OPidx]
    Fq_values = data_Fq.get_expression_data(formula="real")[1]
    Fq_vec = Fq_values[time_frame_index:time_last_index]
    Fq_mean = sum(Fq_vec) / len(Fq_vec)

    # ---------- STORE RESULTS ---------- #
    id_vec[OPidx] = Id_mean
    iq_vec[OPidx] = Iq_mean
    fd_vec[OPidx] = Fd_mean
    fq_vec[OPidx] = Fq_mean

# # ---------- COMPUTE VOLTAGE FIRST HARMONIC ---------- ##

voltage_peak_vec = np.zeros(n_OPpoints)
voltage_angle_vec = np.zeros(n_OPpoints)
for Idx in range(n_OPpoints):

    isd = id_vec[Idx]
    isq = iq_vec[Idx]
    fd = fd_vec[Idx]
    fq = fq_vec[Idx]
    speed = float(speed_str_vec[Idx])

    Fs = POLE_PAIRS * speed / 60
    Ws = Fs * 2 * np.pi

    vd = STATOR_RESISTANCE * isd - Ws * (fq + END_WINDING_INDUCTANCE * isq)
    vq = STATOR_RESISTANCE * isq + Ws * (fd + END_WINDING_INDUCTANCE * isd)

    voltage_peak_vec[Idx] = np.hypot(vd, vq)
    voltage_angle_vec[Idx] = np.atan2(vq, -vd) * 180 / np.pi

voltage_peak_str_vec = [str(x) for x in voltage_peak_vec]
voltage_angle_str_vec = [str(x) for x in voltage_angle_vec]

voltage_peak_str_vec_uom = [x + "V" for x in voltage_peak_str_vec]
voltage_angle_str_vec_uom = [x + "deg" for x in voltage_angle_str_vec]

header_pwm = header_current_driven + ["PhaseVoltagePeak", "phiV"]
operating_points_pwm_uom = [header_pwm] + [
    list(row) for row in zip(speed_str_vec_uom, phase_advance_str_vec_uom, peak_current_str_vec_uom, voltage_peak_str_vec_uom, voltage_angle_str_vec_uom)
]

optimetrics_pwm_list = [
    [left_col[i]] + operating_points_pwm_uom[i]
    for i in range(len(operating_points_pwm_uom))
]
write_csv(PWM_OPTIMETRICS_CSV_PATH, optimetrics_pwm_list)

# # ========== RUN PWM OPTIMETRICS ========== ##

m2d.set_active_design(PWM_DESIGN_NAME)

# Define variables in the model
m2d["PeriodMultiplier"] = PWM_PERIOD_MULTIPLIER
m2d.variable_manager["StatorFrequency"].expression = "NumPoles/2*MachineRPM/1rpm/60" + "*1Hz"
PWM_StopTimeExp = "1/StatorFrequency*1Hz*1s*PeriodMultiplier"

m2d["SwitchingFrequency"] = PWM_SWITCHING_FREQUENCY
m2d["BusDC"] = PWM_BUS_DC_VOLTAGE * PWM_BUS_DC_MULTIPLIER
m2d["Tmin"] = PWM_TMIN
m2d["Tmax"] = PWM_TMAX

# Define the simulation setup
setup_name = "MySetupAuto"
setup = m2d.create_setup(name=setup_name)
setup.props["StopTime"] = str(PWM_StopTimeExp)
setup.props["NonlinearSolverResidual"] = "0.00000001"
setup.props["OutputPerObjectCoreLoss"] = True
setup.props["OutputPerObjectSolidLoss"] = True
setup.update()

# Import output variables
for k, v in output_vars.items():
    m2d.create_output_variable(k, v)
m2d.create_output_variable("Id_peak", "2/3*(Current(WG_Ph1_P1)*cos(ThetaED)+Current(WG_Ph2_P1)*cos(ThetaED - 120deg)+Current(WG_Ph3_P1)*cos(ThetaED - 240deg))")
m2d.create_output_variable("Iq_peak", "2/3*(Current(WG_Ph1_P1)*-sin(ThetaED)+Current(WG_Ph2_P1)*-sin(ThetaED - 120deg)+Current(WG_Ph3_P1)*-sin(ThetaED - 240deg))")

# Import and run the optimetrics analysis
param_sweep = m2d.parametrics.add_from_file(PWM_OPTIMETRICS_CSV_PATH, name=PWM_OPTIMETRICS_CSV_FILENAME)
param_sweep.analyze(cores=NUM_CORES, tasks=NUM_CORES, use_auto_settings=False)

# # ---------- PWM OPTIMETRICS POST-PROCESSING ---------- ##

variations = {"MachineRPM": "All", "PhaseAdvance": "All", "IPeak": "All", "PhaseVoltagePeak": "All", "phiV": "All"}

PWM_output_variables = ["Torque", "Speed", "Id", "Iq", "Winding Losses 2D Tot", "Winding Losses 2D DC", "Magnet Losses",
                        "Stator Eddy Currents Losses", "Rotor Eddy Currents Losses"]
PWM_output_vec = np.zeros(len(PWM_output_variables))
PWM_output_mat = np.zeros((n_OPpoints, len(PWM_output_variables)))

data_SolidLoss = m2d.post.get_solution_data(
    expressions=["SolidLoss"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_StatorEddy = m2d.post.get_solution_data(
    expressions=["StatorEddy"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_RotorEddy = m2d.post.get_solution_data(
    expressions=["RotorEddy"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_torque = m2d.post.get_solution_data(
    expressions=["Moving1.Torque"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_Id = m2d.post.get_solution_data(
    expressions=["Id_peak"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_Iq = m2d.post.get_solution_data(
    expressions=["Iq_peak"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

data_WindingLoss = m2d.post.get_solution_data(
    expressions=["WindingLoss"],
    setup_sweep_name=m2d.nominal_sweep,
    domain="Sweep",
    variations=variations,
    primary_sweep_variable="Time",
)

for OPidx in range(n_OPpoints):
    speed = speed_str_vec[OPidx]

    ## ---------- GET TORQUE DATA ---------- ##
    torque_uom = data_torque.units_data["Moving1.Torque"]  # get the variable uom
    data_torque.active_variation = data_torque.variations[OPidx]  # determine current variation (sets of variable applied)

    time = data_torque.get_expression_data(formula="magnitude")[0]  # get the X axis (time)
    time_last_index = len(time)  # last simulated time instant
    time_frame = time[-1] * PWM_PERIOD_MULTIPLIER_START / PWM_PERIOD_MULTIPLIER_END
    time_frame_index = np.abs(time - time_frame).argmin()  # index for the time frame

    torque_values = data_torque.get_expression_data(formula="magnitude")[1]  # get Y axis
    torque_vec = torque_values[time_frame_index:time_last_index]
    Torque_mean = Quantity(sum(torque_vec) / len(torque_vec), torque_uom)
    Torque_mean = Torque_mean.to("NewtonMeter")

    ## ---------- GET CURRENT DATA ---------- ##
    data_Id.active_variation = data_Id.variations[OPidx]
    Id_values = data_Id.get_expression_data(formula="magnitude")[1]
    Id_vec = Id_values[time_frame_index:time_last_index]
    Id_mean = sum(Id_vec) / len(Id_vec)

    data_Iq.active_variation = data_Iq.variations[OPidx]
    Iq_values = data_Iq.get_expression_data(formula="magnitude")[1]
    Iq_vec = Iq_values[time_frame_index:time_last_index]
    Iq_mean = sum(Iq_vec) / len(Iq_vec)

    I_peak = np.sqrt(Id_mean**2 + Iq_mean**2)

    ## ---------- GET WINDING LOSS DATA ---------- ##
    WindingLoss_uom = data_WindingLoss.units_data["WindingLoss"]  # get the variable uom

    data_WindingLoss.active_variation = data_WindingLoss.variations[OPidx]

    WindingLoss_values = data_WindingLoss.get_expression_data(formula="magnitude")[1]
    WindingLoss_vec = WindingLoss_values[time_frame_index:time_last_index]
    WindingLoss_mean = Quantity(sum(WindingLoss_vec) / len(WindingLoss_vec), WindingLoss_uom)
    WindingLoss_mean = WindingLoss_mean.to("W")

    ActiveLengthLosses = 3 / 2 * STATOR_RESISTANCE_2D * (Id_mean**2 + Iq_mean**2)

    ## ---------- GET SOLID LOSS DATA ---------- ##
    SolidLoss_uom = data_SolidLoss.units_data["SolidLoss"]  # get the variable uom

    data_SolidLoss.active_variation = data_SolidLoss.variations[OPidx]
    SolidLoss_values = data_SolidLoss.get_expression_data(formula="magnitude")[1]
    SolidLoss_vec = SolidLoss_values[time_frame_index:time_last_index]
    SolidLoss_mean = Quantity(sum(SolidLoss_vec) / len(SolidLoss_vec), SolidLoss_uom)
    SolidLoss_mean = SolidLoss_mean.to("W")

    ## ---------- GET MAGNET LOSS DATA ---------- ##
    MagLoss_mean = SolidLoss_mean - WindingLoss_mean

    ## ---------- GET STATOR EDDY LOSS DATA ---------- ##
    StatorEddy_uom = data_StatorEddy.units_data["StatorEddy"]  # get the variable uom

    data_StatorEddy.active_variation = data_StatorEddy.variations[OPidx]

    StatorEddy_values = data_StatorEddy.get_expression_data(formula="magnitude")[1]
    StatorEddy_vec = StatorEddy_values[time_frame_index:time_last_index]
    StatorEddy_mean = Quantity(sum(StatorEddy_vec) / len(StatorEddy_vec), StatorEddy_uom)
    StatorEddy_mean = StatorEddy_mean.to("W")

    ## ---------- GET ROTOR EDDY LOSS DATA ---------- ##
    RotorEddy_uom = data_RotorEddy.units_data["RotorEddy"]  # get the variable uom

    data_RotorEddy.active_variation = data_RotorEddy.variations[OPidx]

    RotorEddy_values = data_RotorEddy.get_expression_data(formula="magnitude")[1]
    RotorEddy_vec = RotorEddy_values[time_frame_index:time_last_index]
    RotorEddy_mean = Quantity(sum(RotorEddy_vec) / len(RotorEddy_vec), RotorEddy_uom)
    RotorEddy_mean = RotorEddy_mean.to("W")

    ## ---------- STORE RESULTS ---------- ##
    PWM_output_vec = [Torque_mean, data_torque.active_variation["MachineRPM"], Id_mean, Iq_mean, WindingLoss_mean, ActiveLengthLosses, MagLoss_mean, StatorEddy_mean, RotorEddy_mean]
    PWM_output_mat[OPidx, 0: len(PWM_output_vec)] = PWM_output_vec


output_pwm_list = [PWM_output_variables] + PWM_output_mat.tolist()
write_csv(OUTPUT_PWM_CSV_PATH, output_pwm_list)

# ## Finish
#
# ### Save the project

m2d.save_project()
m2d.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
