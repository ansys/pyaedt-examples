Power integrity
~~~~~~~~~~~~~~~

These examples use PyAEDT to show power integrity examples.

.. grid:: 2

   .. grid-item-card:: Power integrity analysis
      :padding: 2 2 2 2
      :link: power_integrity
      :link-type: doc

      .. image:: _static/power_integrity.png
         :alt: Power integrity
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use the Ansys Electronics Database (EDB) for power integrity analysis.


   .. grid-item-card:: Via Array
      :padding: 2 2 2 2
      :link: ../../../00_edb/legacy_standalone/differential_vias
      :link-type: doc

      .. image:: ../../../00_edb/legacy_standalone/_static/diff_via.png
         :alt: Differential Vias
         :width: 250px
         :height: 200px
         :align: center

      This example shows how you can use EDB to create a layout.

   .. grid-item-card::  SIwave DC-IR Analysis
      :padding: 2 2 2 2
      :link: ../../../00_edb/legacy_standalone/01_edb_example
      :link-type: doc

      .. image:: ../../../00_edb/legacy_standalone/_static/siwave_dcir.png
         :alt: SIwave DCIR
         :width: 250px
         :height: 200px
         :align: center

      This example demonstrates the use of EDB to interact with a PCB layout and run DC-IR analysis in SIwave.


   .. grid-item-card:: SIwave DC IR analysis (HFSS 3D Layout)
      :padding: 2 2 2 2
      :link: dcir
      :link-type: doc

      .. image:: _static/dcir.png
         :alt: DCIR
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to configure EDB for DC IR analysis and load EDB into the HFSS 3D Layout UI for analysis
      and postprocessing.

   .. grid-item-card:: Q3D DCIR analysis
      :padding: 2 2 2 2
      :link: dcir_q3d
      :link-type: doc

      .. image:: _static/dcir_q3d.png
         :alt: DCIR
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a design in Q3D Extractor and run a DC IR drop simulation starting
      from an EDB project.

   .. grid-item-card:: PCB AC analysis
      :padding: 2 2 2 2
      :link: ac_q3d
      :link-type: doc

      .. image:: _static/ac_q3d.png
         :alt: AC Q3D
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a design in Q3D Extractor and run a simulation starting
      from an EDB project.

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


   .. toctree::
      :hidden:

      power_integrity
      dcir
      dcir_q3d
      ac_q3d
      ../../../aedt_general/modeler/circuit_schematic
      ../../../aedt_general/modeler/netlist_to_schematic
      ../../../aedt_general/report/touchstone_file
      ../../../00_edb/legacy_standalone/differential_vias
      ../../../00_edb/legacy_standalone/01_edb_example