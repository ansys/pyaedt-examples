Maxwell 3D
~~~~~~~~~~

These examples use PyAEDT to show Maxwell 3D capabilities.

.. grid:: 2

   .. grid-item-card:: Electro DC analysis
      :padding: 2 2 2 2
      :link: ../../low_frequency/general/dc_analysis
      :link-type: doc

      .. image:: ../../low_frequency/general/_static/dc.png
         :alt: Maxwell DC
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a Maxwell DC analysis, compute mass center, and move coordinate systems.


   .. grid-item-card:: Fields export in transient analysis
      :padding: 2 2 2 2
      :link: ../../low_frequency/general/field_export
      :link-type: doc

      .. image:: ../../low_frequency/general/_static/field.png
         :alt: Maxwell field
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to leverage PyAEDT to set up a Maxwell 3D transient analysis and then
      compute the average value of the current density field over a specific coil surface and the magnitude
      of the current density field over all coil surfaces at each time step of the transient analysis.

   .. grid-item-card:: Choke setup
      :padding: 2 2 2 2
      :link: ../../low_frequency/magnetic/choke
      :link-type: doc

      .. image:: ../../low_frequency/magnetic/_static/choke.png
         :alt: Maxwell choke
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a choke setup in Maxwell 3D.

   .. grid-item-card:: Magnet segmentation
      :padding: 2 2 2 2
      :link: ../../low_frequency/motor/aedt_motor/magnet_segmentation
      :link-type: doc

      .. image:: ../../low_frequency/motor/aedt_motor/_static/magnet_segmentation.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to segment magnets of an electric motor. The method is valid and usable for any object you would like to segment.

   .. grid-item-card:: Transformer
      :padding: 2 2 2 2
      :link: ../../low_frequency/motor/aedt_motor/transformer
      :link-type: doc

      .. image:: ../../low_frequency/motor/aedt_motor/_static/transformer.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to set core loss given a set of power-volume [kw/m^3] curves at different frequencies.

   .. grid-item-card:: Maxwell 3D-Icepak electrothermal analysis
      :padding: 2 2 2 2
      :link: ../../low_frequency/multiphysics/maxwell_icepak
      :link-type: doc

      .. image:: ../../low_frequency/multiphysics/_static/charging.png
         :alt: Charging
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up a simple Maxwell design consisting of a coil and a ferrite core.

   .. grid-item-card:: Asymmetric conductor analysis
      :padding: 2 2 2 2
      :link: ../../low_frequency/team_problem/asymmetric_conductor
      :link-type: doc

      .. image:: ../../low_frequency/team_problem/_static/asymmetric_conductor.png
         :alt: Asymmetric conductor
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up the TEAM 7 problem for an asymmetric conductor with a hole and solve it using the Maxwell 3D eddy current solver.

   .. grid-item-card:: Bath plate analysis
      :padding: 2 2 2 2
      :link: ../../low_frequency/team_problem/bath_plate
      :link-type: doc

      .. image:: ../../low_frequency/team_problem/_static/bath.png
         :alt: Bath
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up the TEAM 3 bath plate problem and solve it using the Maxwell 3D eddy current solver.


   .. toctree::
      :hidden:

      ../../low_frequency/general/dc_analysis
      ../../low_frequency/general/field_export
      ../../low_frequency/magnetic/choke
      ../../low_frequency/motor/aedt_motor/magnet_segmentation
      ../../low_frequency/motor/aedt_motor/transformer
      ../../low_frequency/multiphysics/maxwell_icepak
      ../../low_frequency/team_problem/asymmetric_conductor
      ../../low_frequency/team_problem/bath_plate
