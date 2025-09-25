General
~~~~~~~

These examples use PyAEDT to show some general applications.

.. grid:: 2

   .. grid-item-card:: Control program enablement
      :padding: 2 2 2 2
      :link: control_program
      :link-type: doc

      .. image:: _static/control_program.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to enable a control program in a Maxwell 2D project.


   .. grid-item-card:: Resistance calculation
      :padding: 2 2 2 2
      :link: resistance
      :link-type: doc

      .. image:: _static/resistance.png
         :alt: Maxwell resistance
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up a resistance calculation and solve it using the Maxwell 2D DCConduction solver.


   .. grid-item-card:: Eddy current analysis and reduced matrix
      :padding: 2 2 2 2
      :link: eddy_current
      :link-type: doc

      .. image:: _static/eddy_current.png
         :alt: Maxwell Eddy current
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to leverage PyAEDT to assign a matrix and perform series or parallel connections in a Maxwell 2D design.


   .. grid-item-card:: Electrostatic analysis
      :padding: 2 2 2 2
      :link: electrostatic
      :link-type: doc

      .. image:: _static/electrostatic.png
         :alt: Maxwell electrostatic
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a Maxwell 2D electrostatic analysis.


   .. grid-item-card:: External delta circuit
      :padding: 2 2 2 2
      :link: external_circuit
      :link-type: doc

      .. image:: _static/external_circuit.png
         :alt: External circuit
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create an external delta circuit and connect it with a Maxwell 2D design.


   .. grid-item-card:: Electro DC analysis
      :padding: 2 2 2 2
      :link: dc_analysis
      :link-type: doc

      .. image:: _static/dc.png
         :alt: Maxwell DC
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a Maxwell DC analysis, compute mass center, and move coordinate systems.


   .. grid-item-card:: Fields export in transient analysis
      :padding: 2 2 2 2
      :link: field_export
      :link-type: doc

      .. image:: _static/field.png
         :alt: Maxwell field
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to leverage PyAEDT to set up a Maxwell 3D transient analysis and then
      compute the average value of the current density field over a specific coil surface and the magnitude
      of the current density field over all coil surfaces at each time step of the transient analysis.

   .. grid-item-card:: Twin builder
      :padding: 2 2 2 2
      :link: twin_builder/index
      :link-type: doc

      .. image:: twin_builder/_static/rectifier.png
         :alt: Rectifier
         :width: 250px
         :height: 200px
         :align: center

      Twin builder examples.

   .. grid-item-card:: 3-Phase Cable with Neutral
      :padding: 2 2 2 2
      :link: maxwell_3_phase_cable
      :link-type: doc

      .. image:: _static/three_phase_cable.png
         :alt: Maxwell cable
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to create a 3-phase cable with neutral
      and solve it using Maxwell 2D AC Magnetic (Eddy Current) solver.

   .. toctree::
      :hidden:

      control_program
      resistance
      eddy_current
      electrostatic
      external_circuit
      dc_analysis
      field_export
      twin_builder/index
      maxwell_3_phase_cable
