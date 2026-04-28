Icepak
~~~~~~

These examples use PyAEDT to show Icepak capabilities.

.. grid:: 2

   .. grid-item-card:: PCB component definition from CSV file and model image exports
      :padding: 2 2 2 2
      :link: ../../electrothermal/components_csv
      :link-type: doc

      .. image:: ../../electrothermal/_static/icepak_csv.png
         :alt: Icepak CSV
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create different types of blocks and assign power and material to them using a CSV input file.


   .. grid-item-card:: Import of a PCB and its components via IDF and EDB
      :padding: 2 2 2 2
      :link: ../../electrothermal/ecad_import
      :link-type: doc

      .. image:: ../../electrothermal/_static/ecad.png
         :alt: Icepak ECAD
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to import a PCB and its components using IDF files (LDB and BDF).
      You can also use a combination of EMN and EMP files in a similar way.


   .. grid-item-card:: Thermal analysis with 3D components
      :padding: 2 2 2 2
      :link: ../../electrothermal/component_3d
      :link-type: doc

      .. image:: ../../electrothermal/_static/component.png
         :alt: Thermal component
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create a thermal analysis of an electronic package by taking advantage of 3D components with advanced features added by PyAEDT.


   .. grid-item-card:: Graphic card thermal analysis
      :padding: 2 2 2 2
      :link: ../../electrothermal/graphic_card
      :link-type: doc

      .. image:: ../../electrothermal/_static/graphic.png
         :alt: Graphic card
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use pyAEDT to create a graphic card setup in Icepak and postprocess the results.
      The example file is an Icepak project with a model that is already created and has materials assigned.


   .. grid-item-card:: Coaxial
      :padding: 2 2 2 2
      :link: ../../electrothermal/coaxial_hfss_icepak
      :link-type: doc

      .. image:: ../../electrothermal/_static/coaxial.png
         :alt: Coaxial
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create a project from scratch in HFSS and Icepak.


   .. grid-item-card:: Setup from Sherlock inputs
      :padding: 2 2 2 2
      :link: ../../electrothermal/sherlock
      :link-type: doc

      .. image:: ../../electrothermal/_static/sherlock.png
         :alt: PyAEDT logo
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create an Icepak project from Sherlock files (STEP and CSV) and an AEDB board.

   .. grid-item-card:: Circuit-HFSS-Icepak coupling workflow
      :padding: 2 2 2 2
      :link: ../../electrothermal/icepak_circuit_hfss_coupling
      :link-type: doc

      .. image:: ../../electrothermal/_static/ring.png
         :alt: Ring
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to create a two-way coupling between HFSS and Icepak.


   .. grid-item-card:: Electrothermal analysis
      :padding: 2 2 2 2
      :link: ../../electrothermal/electrothermal
      :link-type: doc

      .. image:: ../../electrothermal/_static/electrothermal.png
         :alt: Electrothermal
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use the EDB for DC IR analysis and electrothermal analysis.
      The EDB is loaded into SIwave for analysis and postprocessing.
      In the end, an Icepak project is exported from SIwave.


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

    .. grid-item-card:: HFSS-Icepak microwave oven analysis
      :padding: 2 2 2 2
      :link: ../../high_frequency/multiphysics/microwave_oven
      :link-type: doc

      .. image:: ../../high_frequency/multiphysics/_static/oven.png
         :alt: Microwave Oven
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to couple together HFSS and Icepak to run multiphysics
      analysis on a well know problem of microwave oven.

   .. toctree::
      :hidden:

      ../../electrothermal/components_csv
      ../../electrothermal/ecad_import
      ../../electrothermal/component_3d
      ../../electrothermal/graphic_card
      ../../electrothermal/coaxial_hfss_icepak
      ../../electrothermal/sherlock
      ../../electrothermal/icepak_circuit_hfss_coupling
      ../../electrothermal/electrothermal
      ../../low_frequency/multiphysics/maxwell_icepak
      ../../high_frequency/multiphysics/microwave_oven
