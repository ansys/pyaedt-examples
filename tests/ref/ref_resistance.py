from ansys.aedt.core.generic.numbers_utils import is_close

RESISTANCE_REF = 1.6724005905658806e-5 # reference resistance value (2026.1)
CONV_ERROR = 0.01 # percentage error
FILE = "resistance.py" # file name of the example

if is_close(float(resistance[0]), RESISTANCE_REF, CONV_ERROR) is False:
    raise ValueError(f"Error value mismatch in example file: {FILE}")