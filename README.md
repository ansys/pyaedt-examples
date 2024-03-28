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
- Install (pre-commit)[https://[pre-commit](https://pre-commit.com/).com/] to help identify simple issues before submitting your code for review.
  ```
     pre-commit run --all-files
  ```
- Use the ``tempfile`` module to create and clean up the folder where your
  example will read and write files:
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
- The examples should be formatted, so they are compatible with jupytext using the (light format)[https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format] and can
be rendered and run in (Jupyter Lab)[https://docs.jupyter.org/en/latest/] as Notebook files. Jupyter can be used to ensure correct rendering of markdown, images, and equations.
  ```
     pip install .[doc]
     jupyter lab
  ```
  Notebook files can be opened, edited and run from within Jupyter using _right click > Open With > Jupytext Notebook_.

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
