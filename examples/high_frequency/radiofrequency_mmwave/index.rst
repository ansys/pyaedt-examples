Radio frequency and millimeter wave
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These examples use PyAEDT to show some radio frequency and millimeter wave applications.


.. grid:: 2

   .. grid-item-card:: Inductive iris waveguide filter
      :padding: 2 2 2 2
      :link: iris_filter
      :link-type: doc

      .. image:: _static/wgf.png
         :alt: Waveguide filter
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to build and analyze a four-pole X-Band waveguide filter using inductive irises.

   .. grid-item-card:: Spiral inductor
      :padding: 2 2 2 2
      :link: spiral
      :link-type: doc

      .. image:: _static/spiral.png
         :alt: Spiral
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a spiral inductor, solve it, and plot results.

   .. grid-item-card:: CPWG analysis
      :padding: 2 2 2 2
      :link: coplanar_waveguide
      :link-type: doc

      .. image:: _static/cpwg.png
         :alt: CPWG
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a CPWG (coplanar waveguide with ground) design in 2D Extractor and run a simulation.


   .. grid-item-card:: Stripline analysis
      :padding: 2 2 2 2
      :link: stripline
      :link-type: doc

      .. image:: _static/stripline.png
         :alt: Stripline
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a differential stripline design in 2D Extractor and run a simulation.

   .. grid-item-card:: Lumped element filter design
      :padding: 2 2 2 2
      :link: lumped_element
      :link-type: doc

      .. image:: _static/lumped_filter.png
         :alt: Lumped element filter
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to use the FilterSolutions module to design and visualize the frequency
      response of a band-pass Butterworth filter.


   .. grid-item-card:: Distributed filter design
      :padding: 2 2 2 2
      :link: distributed
      :link-type: doc

      .. image:: _static/distributed_filter.png
         :alt: Distributed filter
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to use the FilterSolutions module to design a 
      band-pass Elliptic filter and export the distributed model to HFSS.

   .. grid-item-card:: Flex cable CPWG
      :padding: 2 2 2 2
      :link: ../emc/flex_cable
      :link-type: doc

      .. image:: ../emc/_static/flex_cable.png
         :alt: Flex cable
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a flex cable CPWG (coplanar waveguide with ground).

   .. grid-item-card:: Eigenmode filter
      :padding: 2 2 2 2
      :link: ../emc/eigenmode
      :link-type: doc

      .. image:: ../emc/_static/eigenmode.png
         :alt: Eigenmode
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to automate the Eigenmode solver in HFSS.

   .. grid-item-card:: FSS unit cell simulation
      :padding: 2 2 2 2
      :link: ../antenna/fss_unitcell
      :link-type: doc

      .. image:: ../antenna/_static/unitcell.png
         :alt: FSS
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to model and simulate a unit cell for a frequency-selective surface in HFSS.

   .. grid-item-card:: RF interference
      :padding: 2 2 2 2
      :link: ../antenna/interferences/index
      :link-type: doc

      .. image:: ../antenna/interferences/_static/emit_simple_cosite.png
         :alt: EMIT logo
         :width: 250px
         :height: 200px
         :align: center

      These examples use PyAEDT to show some general capabilities of EMIT for RF interference.

   .. toctree::
      :hidden:

      iris_filter
      spiral
      coplanar_waveguide
      stripline
      lumped_element
      ../emc/flex_cable
      ../emc/eigenmode
      ../antenna/fss_unitcell
      ../antenna/interferences/index
