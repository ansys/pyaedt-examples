# PyAEDT Examples

This repository holds examples for PyAEDT.

## Getting Started
### Setting Up a Python Environment (Windows & Linux)

This section will guide you through setting up a Python 3.10 environment, installing Git, cloning the repository, creating a virtual environment (venv), activating it, and installing dependencies. Each step is explained for beginners.

#### 1. Install Git

Git is a version control system that lets you download (clone) this repository and manage code changes.

##### Windows
- Download the Git installer from the [official website](https://git-scm.com/download/win).
- Run the installer and follow the default prompts. After installation, you can use Git from Command Prompt or PowerShell.

##### Linux (Ubuntu/Debian)
- Open a terminal and run:
  ```bash
  sudo apt update
  sudo apt install git
  ```
- Verify installation:
  ```bash
  git --version
  ```

#### 2. Install Python

##### Windows
- Go to the [official Python downloads page](https://www.python.org/downloads/) and download Python 3.10 or 3.12 (these are the preferred versions).
- Download the Windows installer (choose the 64-bit version if unsure).
- Run the installer. **Important:** Check the box that says "Add Python to PATH" before clicking "Install Now".
- Complete the installation.

##### Linux (Ubuntu/Debian)
- Open a terminal and run:
  ```bash
  sudo apt update
  sudo apt install python3.10 python3.10-venv python3.10-pip
  ```
- Verify installation:
  ```bash
  python3.10 --version
  ```

#### 3. Clone the Repository

Cloning means downloading the project files to your computer.

- Open Command Prompt, PowerShell, or a terminal.
- Choose a folder where you want to store the project, then run:
  ```bash
  git clone https://github.com/ansys/pyaedt-examples.git
  ```
- Change into the project directory:
  ```bash
  cd pyaedt-examples
  ```

#### 4. Create a Virtual Environment (venv)
A virtual environment is an isolated Python environment where you can install packages without affecting your system Python.

- **Windows:**
  1. Open Command Prompt or PowerShell.
  2. Navigate to your project folder (if not already there):
     ```powershell
     cd path\to\pyaedt-examples
     ```
  3. Create the venv:
     ```powershell
     python -m venv venv
     ```

- **Linux:**
  1. Open a terminal.
  2. Navigate to your project folder (if not already there):
     ```bash
     cd /path/to/pyaedt-examples
     ```
  3. Create the venv:
     ```bash
     python3.10 -m venv venv
     ```

#### 5. Activate the Virtual Environment
Activating the venv ensures you use the isolated Python and packages.

- **Windows:**
  ```powershell
  .\venv\Scripts\activate
  ```
- **Linux:**
  ```bash
  source venv/bin/activate
  ```

When activated, your terminal prompt will change to show `(venv)`.

#### 6. Install Dependencies
Dependencies are listed in `requirements/requirements_doc.txt` or another requirements file.

- With the venv activated, run:
  ```bash
  pip install -r requirements/requirements_doc.txt
  ```

#### What does each step do?
- **Install Git:** Lets you download and manage code from repositories like this one.
- **Clone the repository:** Downloads the project files to your computer.
- **Install Python:** Installs the correct version of Python for this project.
- **Create venv:** Makes a folder (`venv`) with a clean Python installation just for this project.
- **Activate venv:** Switches your terminal to use the venv's Python and packages.
- **Install dependencies:** Installs all the packages your project needs, as listed in the requirements file.

After completing these steps, you will have a Python environment set up with all the necessary tools to work on the PyAEDT examples. Take a look at the [examples](https://examples.aedt.docs.pyansys.com/) to get started.

## Contributing
We welcome contributions to this repository! If you have an example or improvement to share, please follow the guidelines below to ensure consistency and quality.
### Guidelines for contribution

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
     pip install -r requirements/requirements_doc.txt
     jupyter lab
  ```
- You can use this [template](./examples/template.py) to help you start creating a new example 
  for publication here.

  If you're creating an example for publication here, you can open
  the file and render it from within Jupyter  
  using _right click > Open With > Jupytext Notebook_.
