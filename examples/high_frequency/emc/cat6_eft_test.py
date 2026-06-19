# # CAT6A cable harness for EFT testing
#
# This example shows how to use PyAEDT to build a 5 cm long
# **PVC CAT6A 4x2 AWG25/7 GY** cable model in HFSS using the
# :class:`ansys.aedt.core.modules.cable_modeling.Cable` class and its
# :func:`~ansys.aedt.core.modules.cable_modeling.Cable.create_cable_harness`
# method, then attach a piecewise-linear (PWL) source that approximates an
# IEC 61000-4-4 Electrical Fast Transient (EFT) pulse.
#
# A full physical description of the reference cable (CAT6A, dual-layer
# shielding, AWG25/7 stranded conductors, PVC jacket, etc.) is provided in
# ``.github/CAT6-Cable.md``. Three simplifications are applied here, following
# the modelling guidance in that document and a few practical limitations of
# the PyAEDT ``Cable`` wrapper:
#
# * **Stranded conductors -> solid-equivalent**. Each AWG25/7 conductor is
#   modelled as a solid conductor with the AWG25 nominal outer diameter
#   (about 0.455 mm).
# * **S/STP -> UTP for the bundle**. The PyAEDT ``Cable`` wrapper can only
#   nominate one of the bundle's internal conductors as the harness ground
#   reference; the braided overall shield cannot be selected as ground via
#   the wrapper. The dual-layer S/STP shielding is therefore omitted and the
#   outer PVC jacket is modelled as a homogeneous insulation jacket. For an
#   EFT-focused study where common-mode current is excited through one of
#   the internal conductors this approximation captures the dominant
#   coupling behaviour while remaining inside what the wrapper supports.
# * **Twisting is applied at the harness level**. The AEDT cable manager
#   supports explicit twisted-pair definitions, but the PyAEDT ``Cable``
#   harness accessors enumerate bundle children as straight-wire instances
#   only, so this example places eight individual AWG25 conductors in the
#   bundle and uses ``TwistAngleAlongRoute`` on the harness to add an
#   overall helical twist.
#
# The PWL source is a single 5 ns rise / 50 ns half-width / ~1 kV peak
# pulse - a single-pulse approximation of the 5/50 ns EFT waveform from
# IEC 61000-4-4.
#
# Keywords: **HFSS**, **EMC**, **cable**, **CAT6A**, **EFT**, **cable harness**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
import math
import os
import tempfile
import time

import ansys.aedt.core
from ansys.aedt.core.modules.cable_modeling import Cable

# -

# Define constants.

AEDT_VERSION = "2026.1"
NG_MODE = False  # Open AEDT UI when it is launched.

# ## Create temporary directory
#
# Create a temporary directory where the project data is stored.
# If you would like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch AEDT and create an HFSS design
#
# The cable manager native API used by :class:`Cable` is available in
# HFSS designs.

project_path = os.path.join(temp_folder.name, "cat6_eft_test.aedt")
hfss = ansys.aedt.core.Hfss(
    project=project_path,
    design="CAT6A_EFT",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
hfss.modeler.model_units = "mm"

# The :class:`Cable` wrapper validates each material name against
# ``hfss.materials.material_keys`` (the project-level material list), so
# system-library materials are preloaded into the project here. Calling
# ``exists_material`` registers them if found in the AEDT library.

for material_name in ("copper", "PVC plastic"):
    hfss.materials.exists_material(material_name)

# ## CAT6A geometry parameters
#
# Nominal CAT6A S/STP 4x2 AWG25/7 dimensions used by the cable definitions.
# The bundle inner diameter is sized so the four insulated twisted pairs fit
# comfortably; the overall jacket is the outer braided shield.

# +
HARNESS_LENGTH_MM = 50.0  # 5 cm cable run.
CONDUCTOR_DIAMETER = "0.455mm"  # AWG25 nominal solid-equivalent OD.
INSULATION_THICKNESS = "0.20mm"  # PVC primary insulation per conductor.
BUNDLE_INNER_DIAMETER = "5.5mm"  # Inner ID of the overall braided shield.
HARNESS_TWIST = "720deg"  # Two full helical turns over the 5 cm run.
# -

# A small helper builds the JSON dictionaries consumed by :class:`Cable`.
# The full schema is documented in the ``CableModeling`` API reference; only
# the fields exercised by the workflow below are populated.


def _empty_cable_payload():
    """Return a Cable JSON payload with every action disabled."""
    return {
        "Add_Cable": "False",
        "Update_Cable": "False",
        "Remove_Cable": "False",
        "Add_CablesToBundle": "False",
        "Add_Source": "False",
        "Update_Source": "False",
        "Remove_Source": "False",
        "Add_CableHarness": "False",
        "Cable_prop": {
            "CableType": "",
            "IsJacketTypeInsulation": "False",
            "IsJacketTypeBraidShield": "False",
            "IsJacketTypeNoJacket": "False",
            "UpdatedName": "",
            "CablesToRemove": "",
        },
        "CablesToBundle_prop": {
            "CablesToAdd": "",
            "BundleCable": "",
            "NumberOfCableToAdd": 1,
        },
        "Source_prop": {
            "AddClockSource": "False",
            "UpdateClockSource": "False",
            "AddPwlSource": "False",
            "AddPwlSourceFromFile": "",
            "UpdatePwlSource": "False",
            "UpdatedSourceName": "",
            "SourcesToRemove": "",
        },
        "CableHarness_prop": {
            "Name": "",
            "Bundle": "",
            "TwistAngleAlongRoute": "0deg",
            "Polyline": "",
            "AutoOrient": "True",
            "XAxis": "Undefined",
            "XAxisOrigin": ["0mm", "0mm", "0mm"],
            "XAxisEnd": ["0mm", "0mm", "0mm"],
            "ReverseYAxisDirection": "False",
            "CableTerminationsToInclude": [],
        },
        "CableManager": {
            "TDSources": {
                "ClockSourceDef": {
                    "ClockSignalParams": {},
                    "TDSourceAttribs": {"Name": ""},
                },
                "PWLSourceDef": {
                    "PWLSignalParams": {"SignalValues": [], "TimeValues": []},
                    "TDSourceAttribs": {"Name": ""},
                },
            },
            "Definitions": {
                "CableBundle": {
                    "BundleParams": {
                        "AutoPack": "True",
                        "InsulationJacketParams": {
                            "InsThickness": "",
                            "JacketMaterial": "",
                            "InnerDiameter": "",
                        },
                        "BraidShieldJacketParams": {
                            "JacketMaterial": "",
                            "InnerDiameter": "",
                            "NumCarriers": "",
                            "NumWiresInCarrier": "",
                            "WireDiameter": "",
                            "WeaveAngle": "",
                        },
                        "VirtualJacketParams": {
                            "JacketMaterial": "",
                            "InnerDiameter": "",
                        },
                    },
                    "BundleAttribs": {"Name": ""},
                },
                "StWireCable": {
                    "StWireParams": {
                        "WireStandard": "",
                        "WireGauge": "",
                        "CondDiameter": "",
                        "CondMaterial": "",
                        "InsThickness": "",
                        "InsMaterial": "",
                        "InsType": "",
                    },
                    "StWireAttribs": {"Name": ""},
                },
                "TwistedPairCable": {
                    "TwistedPairParams": {
                        "StraightWireCableID": 0,
                        "IsLayLengthSpecified": "False",
                        "LayLength": "",
                        "TurnsPerMeter": "",
                    },
                    "TwistedPairAttribs": {"Name": ""},
                },
            },
        },
    }


# ## Create AWG25 straight-wire conductor definitions
#
# Eight AWG25 conductors (one per CAT6A wire) are defined.
# Support for ``WireStandard = "AWG"`` was added to the PyAEDT ``Cable``
# wrapper specifically for use cases such as this CAT6A cable; previously
# only ``ISO`` mm^2 cross-sections were accepted.

# +
CONDUCTOR_NAMES = [f"cat6a_awg25_{i + 1}" for i in range(8)]

for conductor_name in CONDUCTOR_NAMES:
    payload = _empty_cable_payload()
    payload["Add_Cable"] = "True"
    payload["Cable_prop"]["CableType"] = "straight wire"
    payload["CableManager"]["Definitions"]["StWireCable"] = {
        "StWireParams": {
            "WireStandard": "AWG",
            "WireGauge": "25",
            "CondDiameter": CONDUCTOR_DIAMETER,
            "CondMaterial": "copper",
            "InsThickness": INSULATION_THICKNESS,
            "InsMaterial": "PVC plastic",
            "InsType": "Thin Wall",
        },
        "StWireAttribs": {"Name": conductor_name},
    }
    Cable(hfss, payload).create_cable()
# -

# ## Create the cable bundle with a PVC insulation jacket
#
# A single :class:`Cable` bundle models the outer PVC jacket of the cable.
# The metallic outer braid is omitted (see note in the header) and the
# ``InsulationJacketParams`` block is used to represent the dielectric
# outer jacket of the cable.

# +
BUNDLE_NAME = "cat6a_bundle"

payload = _empty_cable_payload()
payload["Add_Cable"] = "True"
payload["Cable_prop"]["CableType"] = "bundle"
payload["Cable_prop"]["IsJacketTypeInsulation"] = "True"
payload["CableManager"]["Definitions"]["CableBundle"] = {
    "BundleParams": {
        "AutoPack": "True",
        "InsulationJacketParams": {
            "InsThickness": "0.5mm",
            "JacketMaterial": "PVC plastic",
            "InnerDiameter": BUNDLE_INNER_DIAMETER,
        },
        "BraidShieldJacketParams": {
            "JacketMaterial": "",
            "InnerDiameter": "",
            "NumCarriers": "",
            "NumWiresInCarrier": "",
            "WireDiameter": "",
            "WeaveAngle": "",
        },
        "VirtualJacketParams": {
            "JacketMaterial": "",
            "InnerDiameter": "",
        },
    },
    "BundleAttribs": {"Name": BUNDLE_NAME},
}
Cable(hfss, payload).create_cable()
# -

# ## Add the eight conductors to the bundle
#
# Each AWG25 straight-wire definition is added to the bundle via the
# underlying ``CableSetup`` module. ``Cable.add_cable_to_bundle()``
# (1) only acts on the first cable in its input list and (2) always
# emits ``XPos=0mm, YPos=0mm``, which would place every conductor on top
# of every other one. The eight conductors are therefore positioned by
# hand on a small circle inside the jacket - four "pairs" of adjacent
# conductors arranged at 90 deg around the bundle centre.

# +
cable_setup_module = hfss.odesign.GetModule("CableSetup")
PLACEMENT_RADIUS_MM = 1.4  # Conductor centres on this circle.
PAIR_PITCH_DEG = 22.0  # Angular separation between the two wires of a pair.

for index, conductor_name in enumerate(CONDUCTOR_NAMES):
    pair_center_deg = 90.0 * (index // 2)
    sign = -1 if index % 2 == 0 else 1
    theta_rad = math.radians(pair_center_deg + sign * PAIR_PITCH_DEG / 2.0)
    xpos_mm = PLACEMENT_RADIUS_MM * math.cos(theta_rad)
    ypos_mm = PLACEMENT_RADIUS_MM * math.sin(theta_rad)
    cable_setup_module.AddCableToBundle(
        BUNDLE_NAME,
        conductor_name,
        1,
        ["NAME:CableInstParams", "XPos:=", f"{xpos_mm:.4f}mm", "YPos:=", f"{ypos_mm:.4f}mm", "RotX:=", "0deg"],
        ["NAME:CableInstAttribs", "Name:=", conductor_name],
    )
# -

# ## Create a PWL source that approximates an EFT pulse
#
# Single-pulse approximation of the IEC 61000-4-4 5/50 ns waveform:
# 5 ns rise to 1 kV peak, 50 ns to half-amplitude, returning to 0 V.

# +
EFT_SOURCE_NAME = "eft_pulse"

payload = _empty_cable_payload()
payload["Add_Source"] = "True"
payload["Source_prop"]["AddPwlSource"] = "True"
payload["CableManager"]["TDSources"]["PWLSourceDef"] = {
    "PWLSignalParams": {
        "SignalValues": ["0V", "1000V", "500V", "0V"],
        "TimeValues": ["0ns", "5ns", "55ns", "150ns"],
    },
    "TDSourceAttribs": {"Name": EFT_SOURCE_NAME},
}
Cable(hfss, payload).create_pwl_source()
# -

# ## Draw the 5 cm cable route
#
# The cable harness needs a polyline that defines the centreline of the
# cable in the 3D modeller. A straight 5 cm segment along the X axis is
# sufficient for an EFT-style coupling study.

# +
ROUTE_NAME = "cat6a_route"

hfss.modeler.create_polyline(
    points=[["0mm", "0mm", "0mm"], [f"{HARNESS_LENGTH_MM}mm", "0mm", "0mm"]],
    name=ROUTE_NAME,
)
# -

# ## Create the cable harness with terminations
#
# The harness designates one of the eight conductors as the local reference
# conductor (its return path), drives the EFT PWL source onto conductor 1
# at the input end, and loads conductor 1 with 100 ohm at the output end.
# The remaining conductors keep the default 50 ohm input and output
# terminations emitted by the wrapper. ``TwistAngleAlongRoute`` gives the
# bundle a helical twist over the 5 cm run as a coarse model of the pair
# twisting.

# +
HARNESS_NAME = "cat6a_harness"

payload = _empty_cable_payload()
payload["Add_CableHarness"] = "True"
payload["CableHarness_prop"] = {
    "Name": HARNESS_NAME,
    "Bundle": BUNDLE_NAME,
    "TwistAngleAlongRoute": HARNESS_TWIST,
    "Polyline": ROUTE_NAME,
    "AutoOrient": "True",
    "XAxis": "Undefined",
    "XAxisOrigin": ["0mm", "0mm", "0mm"],
    "XAxisEnd": ["0mm", "0mm", "0mm"],
    "ReverseYAxisDirection": "False",
    "CableTerminationsToInclude": [
        {
            "CableName": CONDUCTOR_NAMES[-1],
            "Assignment": "Reference Conductor",
            "AssignmentType": "Impedance",
            "Impedance": "0ohm",
            "Source": {"Type": "Single Value", "Signal": "0V", "ImpedanceValue": "0ohm"},
        },
        {
            "CableName": CONDUCTOR_NAMES[0],
            "Assignment": "Input Terminations",
            "AssignmentType": "Source",
            "Impedance": "100ohm",
            "Source": {
                "Type": "Transient",
                "Signal": EFT_SOURCE_NAME,
                "ImpedanceValue": "100ohm",
            },
        },
        {
            "CableName": CONDUCTOR_NAMES[0],
            "Assignment": "Output Terminations",
            "AssignmentType": "Impedance",
            "Impedance": "100ohm",
            "Source": {
                "Type": "Single Value",
                "Signal": "0V",
                "ImpedanceValue": "100ohm",
            },
        },
    ],
}
Cable(hfss, payload).create_cable_harness()
# -

# ## Save the project and release AEDT
#
# The example does not run the HFSS solve - meshing a multi-conductor
# braided cable can take a long time on modest hardware. Uncomment the
# ``hfss.analyze()`` line below to solve.

# +
# hfss.analyze()

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)
# -

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you have run this example as a Jupyter notebook, you can retrieve
# those project files. The following cell removes all temporary files,
# including the project folder.

temp_folder.cleanup()
