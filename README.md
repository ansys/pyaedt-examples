# PyAEDT Examples

This repository holds examples for PyAEDT.

## Guidelines for contribution

The following guidelines help ensure that the examples are consistent, easy tp read and maintain:

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
- Check if some logic is available as a method in PyAEDT.
- Install (pre-commit)[https://[pre-commit](https://pre-commit.com/).com/] to help identify simple issues before submitting your code for review.
  ```
     pre-commit run --all-files
  ```
- Use the ``tempfile`` module to create and clean up the folder where your
  example will run:
  ```
     import tempfile
  ```
  and create a temporary folder at the beginning of the example:
  ```
     temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
  ```
  and at the end remember to clean it up:
  ```
     temp_dir.cleanup()
  ```
- Rely on Jupyter Lab to visualize the example and check the correctness
  of cells layout.
  ```
     pip install .[doc]
     jupyter lab
  ```
  Select the example you would like to open, right click > Open With > Jupytext Notebook.

## Why Jupytext?

Jupytext is available from within Jupyter and lets you save Jupyter Notebooks as text notebooks.
Multiple formats are supported and notebooks can be saved either as *Markdown files* with a ```.md```
extension or *scripts* (for example with a ```.py``` extension).
Text notebooks are conveniently edited and executed in Jupyter as notebooks.
You could also edit them with your favorite text editor and get the changes back in Jupyter by re-loading 
the document.
When a notebook is edited, the code is stored in plain text and this means Git 
will also see the changes as plain text. 

## Code Style

Code style can be checked by running:

```
    tox -e style
```

Previous command will run [pre-commit](https://pre-commit.com/) for checking code quality.


## Documentation

Documentation can be rendered by running:

### Windows

```
    TODO
```

### MacOS/Linux (requires make)

```
    TODO
```

The resultant HTML files can be inspected using your favorite web browser:

```
    <browser> TODO
```

Previous will open the rendered documentation in the desired browser.
