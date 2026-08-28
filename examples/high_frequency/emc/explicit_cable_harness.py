# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Explicit cable harness modeling example."""

# # Explicit cable harness modeling
#
# This example shows how to use PyAEDT to build a fully explicit HFSS model of a routed CAT6A S/STP
# cable bundle from a configuration file. An explicit harness model represents every conductor,
# insulation body, pair foil shield, overall braid shield, port, and shield boundary as 3-D HFSS
# entities. This makes the model useful for EMC and signal-integrity studies where shield transfer
# impedance controls how external disturbances couple through the cable shield into the conductors.
#
# The CAT6A S/STP bundle is defined in ``cat6a_sstp_awg25.yaml``. The high-level
# :class:`RoutedCableBundle` API replaces the inline geometry, shield-boundary, port, and
# differential-pair helper code that would otherwise be needed to create this model.
#
# Keywords: **HFSS**, **EMC**, **cable**, **CAT6A**, **S-parameters**, **transfer impedance**.

# ## Perform imports and define constants
#
# Perform required imports.

# +
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

import ansys.aedt.core
import numpy as np
from ansys.aedt.core.modeler.advanced_cad.cable_harness import (
    CableBundleConfig,
    MeasuredShield,
    RoutedCableBundle,
    build_shield_model,
)

# -

# Define constants.

AEDT_VERSION = "2026.1"
NG_MODE = False  # Open AEDT UI when it is launched.
EXAMPLE_PATH = Path(__file__).parent if "__file__" in globals() else Path.cwd()
CONFIG_FILE = EXAMPLE_PATH / "_static" / "cat6a_sstp_awg25.yaml"

# ## Create temporary directory
#
# Create a temporary directory where the project can be saved.
# If you'd like to retrieve the project data for subsequent use,
# the temporary folder name is given by ``temp_folder.name``.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Load and validate the cable definition
#
# Load the cable-bundle configuration from YAML. ``CableBundleConfig.from_file()`` validates the
# file against the cable-harness JSON schema and runs semantic cross-reference checks.

config = CableBundleConfig.from_file(CONFIG_FILE)
config.validate()

route_points = config.active_route.points
route_length = float(np.linalg.norm(np.diff(route_points, axis=0), axis=1).sum())
print("CAT6A S/STP cable-bundle configuration")
print(f"  Pairs: {len(config.pairs)}")
print(f"  Conductors: {len(config.conductors)}")
print(f"  Route length: {route_length:.3f} {config.units}")
print(f"  Frequency range: {config.simulation.frequency_start:.3e} Hz to {config.simulation.frequency_stop:.3e} Hz")

# ## Launch AEDT and create the HFSS design
#
# Launch HFSS with a terminal solution type. The model units, material override setting, and causal
# material option follow the original CAT6A EFT HFSS setup.

project_name = os.path.join(temp_folder.name, "cat6a_explicit_harness.aedt")
hfss = ansys.aedt.core.Hfss(
    project=project_name,
    design="CAT6A_Explicit_Harness",
    solution_type="DrivenTerminal",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)
hfss.modeler.model_units = config.units
hfss.change_material_override(material_override=True)
hfss.change_automatically_use_causal_materials(lossy_dielectric=True)

# ## Build the explicit cable harness
#
# Create the explicit geometry, assign transfer-impedance boundaries to the foil and braid shields,
# create both end ports for each conductor, and define the differential pairs from the configuration.
# The returned ``BuildArtifacts`` object records every created entity by role.

bundle = RoutedCableBundle(config, hfss, name_prefix="cat6a")
artifacts = bundle.build()
print("Created explicit cable-harness artifacts:")
for role, names in artifacts.as_dict().items():
    print(f"  {role}: {len(names)}")

# ``build()`` is a convenience wrapper. Advanced workflows can call the same steps individually:
# ``ensure_materials()``, ``build_geometry()``, ``assign_shield_boundaries()``, ``create_ports()``,
# and ``define_differential_pairs()``.

# ## Review the overall braid transfer impedance
#
# Build the analytic transfer-impedance model for the overall braid and print ``|Zt|`` at several
# frequencies. To substitute bench data or vendor data, provide a ``shield_model_factory`` to
# ``RoutedCableBundle`` that returns :class:`MeasuredShield` for the desired shield definition.

if config.bundle.overall_shield:
    shield_model = build_shield_model(
        config.bundle.overall_shield,
        radius_mm=config.simulation.geometry.overall_shield_radius,
        materials=config.materials,
    )
    transfer_frequencies = np.array([1e6, 1e8, 1e9, 1e10])
    transfer_impedance = shield_model.transfer_impedance(transfer_frequencies)
    print("Overall braid transfer impedance:")
    for frequency, impedance in zip(transfer_frequencies, transfer_impedance):
        print(f"  f = {frequency:.3e} Hz, |Zt| = {abs(impedance) * 1e3:.3f} mOhm/m")

# ``MeasuredShield`` can be used by a custom shield model factory. This object is not assigned below;
# it shows the expected shape of measured transfer-impedance data.
measured_shield_example = MeasuredShield(np.array([1e6, 1e9]), np.array([1e-3 + 0j, 2e-2 + 1j * 1e-3]))
print(f"Measured-shield example at 10 MHz: {abs(measured_shield_example.transfer_impedance(np.array([1e7]))[0]) * 1e3:.3f} mOhm/m")

# ## Create setup and sweep
#
# Create the broadband S-parameter setup and interpolating sweep described by the configuration. The
# analysis is not run because meshing a multi-conductor explicit cable model can take a long time.

setup = bundle.create_setup(name="Sparam", maximum_passes=8, delta_s=0.02, num_points=401, sweep_name="Broadband")
print(f"Created setup: {setup.name}")

# Uncomment to solve. Meshing a multi-conductor cable can take a long time.
# hfss.analyze()

# ## Save project and release AEDT

hfss.save_project()
hfss.release_desktop()
# Wait 3 seconds to allow AEDT to shut down before cleaning the temporary directory.
time.sleep(3)

# ## Clean up
#
# All project files are saved in the folder ``temp_folder.name``.
# If you've run this example as a Jupyter notebook, you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()
