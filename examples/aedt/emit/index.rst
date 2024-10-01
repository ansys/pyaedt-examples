EMIT
~~~~

These examples use PyAEDT to show EMIT capabilities.

.. grid:: 2

   .. grid-item-card:: Antenna
      :padding: 2 2 2 2
      :link: ../../high_frequency/antenna/interferences/antenna
      :link-type: doc

      .. image:: ../../high_frequency/antenna/interferences/_static/emit.png
         :alt: Antenna
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create a project in EMIT for the simulation of an antenna using HFSS.

   .. grid-item-card:: HFSS to EMIT coupling
      :padding: 2 2 2 2
      :link: ../../high_frequency/antenna/interferences/hfss_emit
      :link-type: doc

      .. image:: ../../high_frequency/antenna/interferences/_static/emit_hfss.png
         :alt: EMIT HFSS
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to link an HFSS design to EMIT and model RF interference among various components.

   .. grid-item-card:: Interference type classification
      :padding: 2 2 2 2
      :link: ../../high_frequency/antenna/interferences/interference
      :link-type: doc

      .. image:: ../../high_frequency/antenna/interferences/_static/interference.png
         :alt: EMIT HFSS
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to load an existing AEDT EMIT design and analyze the results to classify the worst-case interference.

   .. grid-item-card:: Compute receiver protection levels
      :padding: 2 2 2 2
      :link: ../../high_frequency/antenna/interferences/interference_type
      :link-type: doc

      .. image:: ../../high_frequency/antenna/interferences/_static/protection.png
         :alt: EMIT protection
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to open an AEDT project with an EMIT design and analyze the results to determine if
      the received power at the input to each receiver exceeds the specified protection levels.

   .. grid-item-card:: Interference type classification using a GUI
      :padding: 2 2 2 2
      :link: ../../high_frequency/antenna/interferences/interference_type
      :link-type: doc

      .. image:: ../../high_frequency/antenna/interferences/_static/interference_type.png
         :alt: EMIT protection
         :width: 250px
         :height: 200px
         :align: center

      This example uses a GUI to open an AEDT project with an EMIT design and analyze the results to classify
      the worst-case interference.

   .. toctree::
      :hidden:

      ../../high_frequency/antenna/interferences/antenna
      ../../high_frequency/antenna/interferences/hfss_emit
      ../../high_frequency/antenna/interferences/interference
      ../../high_frequency/antenna/interferences/protection
      ../../high_frequency/antenna/interferences/interference_type
