Power integrity
~~~~~~~~~~~~~~~

These examples use PyAEDT to show power integrity examples.

.. grid:: 2

   .. grid-item-card:: Via Array
      :padding: 2 2 2 2
      :link: ../../../edb/legacy_standalone/differential_vias
      :link-type: doc

      .. image:: ../../../edb/legacy_standalone/_static/diff_via.png
         :alt: Differential Vias
         :width: 250px
         :height: 200px
         :align: center

      This example shows how you can use EDB to create a layout.

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
      ../../../edb/legacy_standalone/differential_vias