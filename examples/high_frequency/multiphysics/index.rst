Multiphysics
~~~~~~~~~~~~

These examples use PyAEDT to show some multiphysics applications.


.. grid:: 2

   .. grid-item-card:: HFSS-Mechanical MRI analysis
      :padding: 2 2 2 2
      :link: mri
      :link-type: doc

      .. image:: _static/mri.png
         :alt: MRI
         :width: 250px
         :height: 200px
         :align: center

      This example uses a coil tuned to 63.8 MHz to determine the temperature rise in a gel phantom near
      an implant given a background SAR of 1 W/kg.

   .. grid-item-card:: HFSS-Mechanical multiphysics analysis
      :padding: 2 2 2 2
      :link: hfss_mechanical
      :link-type: doc

      .. image:: _static/hfss_mechanical.png
         :alt: HFSS Mechanical
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to use PyAEDT to create a multiphysics workflow that includes Circuit, HFSS, and Mechanical.


   .. grid-item-card:: Import of a PCB and its components via IDF and EDB
      :padding: 2 2 2 2
      :link: ../../electrothermal/ecad_import
      :link-type: doc

      .. image:: ../../electrothermal/_statc/ecad.png
         :alt: Icepak ECAD
         :width: 250px
         :height: 200px
         :align: center

      This example shows how to import a PCB and its components using IDF files (LDB and BDF).
      You can also use a combination of EMN and EMP files in a similar way.

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


   .. toctree::
      :hidden:

      mri
      hfss_mechanical
      ../../electrothermal/ecad_import
      ../../electrothermal/coaxial_hfss_icepak
      ../../electrothermal/electrothermal
      ../../electrothermal/icepak_circuit_hfss_coupling

