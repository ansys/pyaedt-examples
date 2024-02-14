import os

from setuptools import find_namespace_packages, setup

root = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(root, "ansys", "rep", "template", "__version__.py"), "r") as f:
    exec(f.read(), about)


def setup_package():
    metadata = dict(
        name="ansys-rep-template",
        version="0.1.0",
        packages=find_namespace_packages(include=["ansys.*"]),
        author="ANSYS, Inc.",
        description="REP python repo template",
        long_description="See README.md",
        long_description_content_type="text/x-markdown",
        project_urls={},
        python_requires=">=3.7",
        install_requires=[
            "ansys-rep-common[falcon,crypto,redis,otel] @ \
                git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common",
        ],
        package_data={"": ["*.json", "*_job.sh"]},
        include_package_data=True,
        extras_require={},
    )

    setup(**metadata)


if __name__ == "__main__":
    setup_package()
