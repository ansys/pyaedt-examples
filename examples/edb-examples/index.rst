EDB Examples
~~~~~~~~~~~~

These examples demonstrate complete, end-to-end workflows using PyEDB (the
Python interface to the Ansys Electronics Database) together with PyAEDT to
run simulations in Ansys Electronics Desktop.

.. grid:: 2

   .. grid-item-card:: PCB Signal Integrity Analysis
      :padding: 2 2 2 2
      :link: pcb_signal_integrity
      :link-type: doc

      .. image:: _static/pcb_signal_integrity.png
         :alt: PCIe channel insertion loss
         :width: 250px
         :height: 200px
         :align: center

      Configure a PCB layout using PyEDB, run a SIwave AC analysis in HFSS 3D
      Layout, and plot the differential insertion loss for a PCIe Gen4 channel.

.. toctree::
   :hidden:

   pcb_signal_integrity
