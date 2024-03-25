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
