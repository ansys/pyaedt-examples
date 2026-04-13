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

   .. grid-item-card:: Configuration Files
      :padding: 2 2 2 2
      :link: use_configuration/index
      :link-type: doc

      .. image:: use_configuration/_static/configurator_2.png
         :alt: PyEDB2
         :width: 250px
         :height: 200px
         :align: center

      Links to examples in the PyAEDT documentation that show how to use PyEDB configuration files.

   .. grid-item-card:: IPC2581
      :padding: 2 2 2 2
      :link: legacy_standalone/edb_to_ipc2581
      :link-type: doc

      .. image:: legacy_standalone/_static/ipc.png
         :alt: PyEDB2
         :width: 250px
         :height: 200px
         :align: center

      This example shows how you can use PyAEDT to export an IPC2581 file.

   .. grid-item-card:: IC Workflow using GDS
      :padding: 2 2 2 2
      :link: legacy_standalone/gds_workflow
      :link-type: doc

      .. image:: legacy_standalone/_static/gds.png
         :alt: GDS
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use the ``Edb`` class to manage ``GDS`` files, import them and setup analysis.


.. toctree::
   :hidden:

   pcb_signal_integrity
   use_configuration/index
   legacy_standalone/edb_to_ipc2581
   legacy_standalone/gds_workflow
