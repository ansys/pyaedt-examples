# PyAEDT Examples

This repository holds examples for PyAEDT.

## Guidelines for contribution

The following guidelines help ensure that the examples are consistent, easy to read and maintain:

- Use lower case with underscore for variables, functions and methods.
- Variable instances should use lower case with underscore.
  For example:
  ```
     m2d = Maxwell2d()
     hfss = Hfss() 
  ```
- Explicitly use the named arguments when calling methods or functions. For example:
  ```
     m3d.modeler.create_box(position=[7, 4, 22], 
                            dimensions_list=[10, 5, 30], 
                            name="Magnet", 
                            matname="copper")
  ```
- Keep the syntax in your example simple and easy to read. For example, the logic required for your example may already exist in ``pyaedt`` or other installed packages.
- Install [pre-commit](https://pre-commit.com/) to help identify simple issues before submitting your code for review.
  ```
     pre-commit run --all-files
  ```
- Use the ``tempfile`` module to create and clean up the folder where your example will read and write files:
  ```
     import tempfile
  ```
  Create a temporary folder at the beginning of the example:
  ```
     temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
  ```
  Remove the temporary folder at the end of the example:
  ```
     temp_folder.cleanup()
  ```
- The examples should be formatted, so they are compatible with 
  [jupytext](https://jupytext.readthedocs.io/en/latest/) using the [light format](https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format) and can
  be rendered and run in [Jupyter Lab](https://docs.jupyter.org/en/latest/) as Notebook files. Jupyter can be used to ensure correct
  rendering of markdown, images, and equations.
  ```
     pip install .[doc]
     jupyter lab
  ```
- You can use this [template](./examples/template.py) to help you start creating a new example 
  for publication here.

  If you're creating an example for publication here, you can open
  the file and render it from within Jupyter  
  using _right click > Open With > Jupytext Notebook_.
