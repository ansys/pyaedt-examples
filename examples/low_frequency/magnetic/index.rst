Magnetics
~~~~~~~~~

These examples use PyAEDT to show some magnetics applications.

.. grid:: 2

   .. grid-item-card:: Transient winding analysis
      :padding: 2 2 2 2
      :link: transient_winding
      :link-type: doc

      .. image:: _static/transient.png
         :alt: Maxwell transient
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a project in Maxwell 2D and run a transient simulation.

   .. grid-item-card:: Choke setup
      :padding: 2 2 2 2
      :link: choke
      :link-type: doc

      .. image:: _static/choke.png
         :alt: Maxwell choke
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a choke setup in Maxwell 3D.


   .. grid-item-card:: Magnetomotive force
      :padding: 2 2 2 2
      :link: magneto_motive_line
      :link-type: doc

      .. image:: _static/magneto.png
         :alt: Maxwell magneto force
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to calculate the magnetomotive force.


   .. grid-item-card:: Lorentz actuator
      :padding: 2 2 2 2
      :link: lorentz_actuator
      :link-type: doc

      .. image:: _static/lorentz_actuator.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to set up a Lorentz actuator and solve it using the Maxwell 2D transient solver.


   .. grid-item-card:: 2D Axi-symmetric Actuator
      :padding: 2 2 2 2
      :link: lorentz_actuator
      :link-type: doc

      .. image:: _static/2d-axi_magnetostatic_actuator.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example demonstrates how to leverage axi-symmetry and the magnetostatic solver in actuator analysis.

   .. toctree::
      :hidden:

      transient_winding
      choke
      magneto_motive_line
      lorentz_actuator
      2d-axi_magnetostatic_actuator
