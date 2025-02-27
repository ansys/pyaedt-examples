Signal integrity
~~~~~~~~~~~~~~~~

These examples use PyAEDT to show signal integrity examples.

.. grid:: 2

   .. grid-item-card:: Channel Operating Margin (COM)
      :padding: 2 2 2 2
      :link: com_analysis
      :link-type: doc

      .. image:: _static/com_eye.png
         :alt: COM
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT for COM analysis.

   .. grid-item-card:: Pre-layout signal integrity
      :padding: 2 2 2 2
      :link: pre_layout
      :link-type: doc

      .. image:: _static/pre_layout_sma_connector_on_pcb.png
         :alt: Pre layout connector
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create a parameterized layout design and load the layout into HFSS 3D Layout
      for analysis and postprocessing.

   .. grid-item-card:: Siwave differential pairs in Hfss 3D Layout
      :padding: 2 2 2 2
      :link: serdes_differential
      :link-type: doc

      .. image:: _static/parametrized_edb.png
         :alt: Parametrized differential pairs
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to set up SYZ analysis on a
      serdes channel.

   .. grid-item-card:: Pre-layout Parameterized PCB
      :padding: 2 2 2 2
      :link: pre_layout_parametrized
      :link-type: doc

      .. image:: _static/pre_layout_parameterized_pcb.png
         :alt: Pre layout parametrized
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use the EDB interface along with HFSS 3D Layout to create and solve a parameterized layout.

   .. grid-item-card:: AMI Postprocessing
      :padding: 2 2 2 2
      :link: ami
      :link-type: doc

      .. image:: _static/ami.png
         :alt: AMI
         :width: 250px
         :height: 200px
         :align: center

      This example demonstrates advanced postprocessing of AMI simulations.

   .. grid-item-card:: Multi-zone simulation with SIwave
      :padding: 2 2 2 2
      :link: multizone
      :link-type: doc

      .. image:: _static/multizone.png
         :alt: Multizone
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to simulate multiple zones with SIwave.

   .. grid-item-card:: Circuit transient analysis and eye diagram
      :padding: 2 2 2 2
      :link: circuit_transient
      :link-type: doc

      .. image:: _static/circuit_transient.png
         :alt: Circuit transient
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create a circuit design, run a Nexxim time-domain simulation, and create an eye diagram.

   .. grid-item-card:: Circuit schematic creation and analysis
      :padding: 2 2 2 2
      :link: ../../../aedt_general/modeler/circuit_schematic
      :link-type: doc

      .. image:: ../../../aedt_general/modeler/_static/circuit.png
         :alt: Circuit
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to build a circuit schematic and run a transient circuit simulation.

   .. grid-item-card:: Circuit Netlist to Schematic
      :padding: 2 2 2 2
      :link: ../../../aedt_general/modeler/netlist_to_schematic
      :link-type: doc

      .. image:: ../../../aedt_general/modeler/_static/netlist.png
         :alt: Netlist
         :width: 250px
         :height: 250px
         :align: center

      This example shows how to build a circuit schematic and run a transient circuit simulation.

   .. grid-item-card:: Schematic subcircuit management
      :padding: 2 2 2 2
      :link: ../../emc/subcircuit
      :link-type: doc

      .. image:: ../../emc/_static/subcircuit.png
         :alt: Cable
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to add a subcircuit to a circuit design.
      It changes the focus within the hierarchy between the child subcircuit and the parent design.

   .. grid-item-card:: Touchstone files
      :padding: 2 2 2 2
      :link: ../../../aedt_general/report/touchstone_file
      :link-type: doc

      .. image:: ../../../aedt_general/report/_static/touchstone_skitrf.png
         :alt: Touchstone file
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use objects in a Touchstone file without opening AEDT.

   .. grid-item-card:: PCIE virtual compliance
      :padding: 2 2 2 2
      :link: ../../../aedt_general/report/virtual_compliance
      :link-type: doc

      .. image:: ../../../aedt_general/report/_static/virtual_compliance_eye.png
         :alt: Virtual compliance
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to generate a compliance report in PyAEDT using the VirtualCompliance class.

   .. toctree::
      :hidden:

      com_analysis
      pre_layout
      pre_layout_parametrized
      ami
      multizone
      serdes_differential
      circuit_transient

      ../../../aedt_general/modeler/circuit_schematic
      ../../../aedt_general/modeler/netlist_to_schematic
      ../../emc/subcircuit
      ../../../aedt_general/report/touchstone_file
      ../../../aedt_general/report/virtual_compliance
