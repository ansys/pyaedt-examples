# PyAEDT Examples

This repository holds examples for PyAEDT.

# ## Code Style
#
# Code style can be checked by running:

```
    tox -e style
```

Previous command will run `pre-commit`_ for checking code quality.


# ## Documentation
#
# Documentation can be rendered by running:

Windows

```
    tox -e doc-win
```

MacOS/Linux (requires make)

```
    tox -e doc-linux
```

The resultant HTML files can be inspected using your favorite web browser:

```
    <browser> .tox/doc_out_html/index.html
```

Previous will open the rendered documentation in the desired browser.

.. LINKS AND REFERENCES
.. _pre-commit: https://pre-commit.com/
