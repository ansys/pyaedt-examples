# # Configuration files
#
# This example shows how to use PyAEDT to export configuration files and reuse
# them to import in a new project. A configuration file is supported by these applications:
#
# * HFSS
# * 2D Extractor and Q3D Extractor
# * Maxwell
# * Icepak (in AEDT)
# * Mechanical (in AEDT)
#
# The following topics are covered:
#
# * Variables
# * Mesh operations (except Icepak)
# * Setup and optimetrics
# * Material properties
# * Object properties
# * Boundaries and excitations
#
# When a boundary is attached to a face, PyAEDT tries to match it with a
# ``FaceByPosition`` on the same object name on the target design. If for
# any reason this face position has changed or the object name in the target
# design has changed, the boundary fails to apply.
#
# Keywords: **AEDT**, **general**, **configuration file**, **setup**.

# ## Perform imports and define constants
# Import the required packages.

import time

time.sleep(20)

1 / 0

print("never called")