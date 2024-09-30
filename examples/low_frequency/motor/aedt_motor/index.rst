AEDT Motor
~~~~~~~~~~

These examples use PyAEDT to show some motor applications in AEDT.

.. grid:: 2

   .. grid-item-card:: PM synchronous motor transient analysis
      :padding: 2 2 2 2
      :link: pm_synchronous
      :link-type: doc

      .. image:: _static/pm_synchronous.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a Maxwell 2D transient analysis for an interior permanent magnet (PM) electric motor.

   .. grid-item-card:: Magnet segmentation
      :padding: 2 2 2 2
      :link: magnet_segmentation
      :link-type: doc

      .. image:: _static/magnet_segmentation.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to segment magnets of an electric motor. The method is valid and usable for any object you would like to segment.

   .. grid-item-card:: Transformer
      :padding: 2 2 2 2
      :link: transformer
      :link-type: doc

      .. image:: _static/transformer.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to set core loss given a set of power-volume [kw/m^3] curves at different frequencies.


   .. grid-item-card:: Transformer leakage inductance calculation
      :padding: 2 2 2 2
      :link: transformer_inductance
      :link-type: doc

      .. image:: _static/transformer2.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a Maxwell 2D magnetostatic analysis to calculate transformer leakage inductance and reactance.


   .. grid-item-card:: Motor creation and export
      :padding: 2 2 2 2
      :link: rmxpert
      :link-type: doc

      .. image:: _static/rmxpert.png
         :alt: Maxwell general
         :width: 250px
         :height: 200px
         :align: center

      This example uses PyAEDT to create a RMxprt project and export it to Maxwell 2D.


   .. toctree::
      :hidden:

      pm_synchronous
      magnet_segmentation
      transformer
      transformer_inductance
      rmxpert
