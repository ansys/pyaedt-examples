Use configuration
~~~~~~~~~~~~~~~~~

Workflow
--------

The following examples illustrate the use of configuration files in PyEDB.
PyAEDT offers a GUI which utilizes config file. Please refer to `Configure Layout extension`_ for details.

.. _Configure Layout extension : https://aedt.docs.pyansys.com/version/stable/User_guide/pyaedt_extensions_doc/project/configure_layout.html


.. grid:: 2

   .. grid-item-card:: Power Integrity PDN analysis
      :padding: 2 2 2 2
      :link: pdn_analysis
      :link-type: doc

      .. image:: _static/pi.png
         :alt: Configurator
         :width: 250px
         :height: 200px
         :align: center

   .. grid-item-card:: PCB Power Integrity DCIR analysis
      :padding: 2 2 2 2
      :link: pcb_dc_ir
      :link-type: doc

      .. image:: _static/dcir_pcb.png
         :alt: Configurator
         :width: 250px
         :height: 200px
         :align: center

   .. grid-item-card:: Package Power Integrity DCIR analysis
      :padding: 2 2 2 2
      :link: dcir
      :link-type: doc

      .. image:: _static/dcir.png
         :alt: Configurator
         :width: 250px
         :height: 200px
         :align: center

   .. grid-item-card:: Create Transmission Line
      :padding: 2 2 2 2
      :link: modeler_simple_transmission_line
      :link-type: doc

      .. image:: _static/tline.png
         :alt: Configurator
         :width: 250px
         :height: 200px
         :align: center

.. toctree::
   :hidden:

   pdn_analysis
   pcb_dc_ir
   dcir
   modeler_simple_transmission_line


Guideline
---------

:doc:`Material management <import_material>`

:doc:`Ports setup <import_ports>`

:doc:`Simulation setup management <import_setup_ac>`

:doc:`Padstack Definition management <import_padstack_definitions>`

:doc:`Components management <import_components>`

:doc:`Sources management <import_sources>`

:doc:`Operations management <import_operations>`

.. toctree::
   :hidden:

   import_material
   import_ports
   import_setup_ac
   import_padstack_definitions
   import_components
   import_sources
   import_operations