# PyAEDT Examples

This repository holds examples for PyAEDT.

## Guidelines for contribution

A list of syntax and code style rules to follow in order to have clean and readable examples:

- Camel case convention
- No upper case letters in variable names, especially when creating new instance of a physics.
  For example:
  ```
     m2d = Maxwell2d()
     hfss = Hfss() 
  ```
- Clearly type the inputs required by methods. For example:
  ```
     m3d.modeler.create_box(position=[7, 4, 22], 
                            dimensions_list=[10, 5, 30], 
                            name="Magnet", 
                            matname="copper")
  ```
- Check if some logic is available as a method in PyAEDT.
- Install pre-commit to help you identify simple issues before submission to code review.
  ```
     pre-commit run --all-files
  ```
- To store temporary files use tempfile module:
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
