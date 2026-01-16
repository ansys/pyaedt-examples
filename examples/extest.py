from pathlib import Path
from ansys.aedt.core.generic.settings import settings

settings.enable_error_handler = False


def reference_check(var_test, reference, convergence_error, file):
    """
    Check the reference value.

    var_test: scalar value of the quantity to test
    reference: reference value of the testing quantity
    convergence_error: percentage error in the analysis setup
    file: path of the texting example
    """
    try:
        if 100 * abs(var_test - reference) / reference > convergence_error:
            raise Exception(f"Error example file: {Path(file).name}")
    except:
        raise Exception(f"Error example file: {Path(file).name}")