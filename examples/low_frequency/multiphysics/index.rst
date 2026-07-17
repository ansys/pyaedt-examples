Multiphysics
~~~~~~~~~~~~

These examples use PyAEDT to show some multiphysics applications.

.. grid-item-card:: Maxwell 3D-Icepak electrothermal analysis
      :padding: 2 2 2 2
      :link: maxwell_icepak
      :link-type: doc

      .. image:: _static/charging.png
         :alt: Charging
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up a simple Maxwell design consisting of a coil and a ferrite core.

.. toctree::
      :hidden:

.. grid-item-card:: Q3D-Icepak-IcepakFEA electrothermal-structural analysis
      :padding: 2 2 2 2
      :link: em_thermal_structural
      :link-type: doc

      .. image:: _static/displacement.jpeg
         :alt: Charging
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up a 3-physics workflow, where the electrothermal analysis implements a 2-way
      coupling approach with restarting at each time substep.

.. toctree::
      :hidden:

      maxwell_icepak
      em_thermal_structural