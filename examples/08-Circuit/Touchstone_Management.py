# # Touchstone Files
#
# This example shows how you can use objects in a Touchstone file without opening AEDT.
#
# To provide the advanced postprocessing features needed for this example, Matplotlib and NumPy
# must be installed on your machine.
#
# This example runs only on Windows using CPython.
#
# Keywords: **Circuit**, **Report**.

# ## Perform required imports
#

from ansys.aedt.core import downloads
from ansys.aedt.core.generic.touchstone_parser import read_touchstone

example_path = downloads.download_touchstone()

# ## Read the Touchstone file.

data = read_touchstone(example_path)

# ## Plot Data
#
# Get the curve plot by category. The following code shows how to plot lists of the return losses,
# insertion losses, fext, and next based on a few inputs and port names.


data.plot_return_losses()
data.plot_insertion_losses()
data.plot_next_xtalk_losses("U1")
data.plot_fext_xtalk_losses(tx_prefix="U1", rx_prefix="U7")

# ## Cross-talk
#
# Identify the worst case cross-talk.

worst_rl, global_mean = data.get_worst_curve(
    freq_min=1,
    freq_max=20,
    worst_is_higher=True,
    curve_list=data.get_return_loss_index(),
)
worst_il, mean2 = data.get_worst_curve(
    freq_min=1,
    freq_max=20,
    worst_is_higher=False,
    curve_list=data.get_insertion_loss_index(),
)
worst_fext, mean3 = data.get_worst_curve(
    freq_min=1,
    freq_max=20,
    worst_is_higher=True,
    curve_list=data.get_fext_xtalk_index_from_prefix(tx_prefix="U1", rx_prefix="U7"),
)
worst_next, mean4 = data.get_worst_curve(
    freq_min=1,
    freq_max=20,
    worst_is_higher=True,
    curve_list=data.get_next_xtalk_index("U1"),
)
