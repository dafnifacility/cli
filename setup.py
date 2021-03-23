from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
# The dynamic metadata for the python pip distributable.
# This is used as the build script for setuptools, telling it about the package and which files to include.
# For more information, see https://packaging.python.org/tutorials/packaging-projects/

setup(
    name="dafni-cli",
    version="0.0.1",
    author="DAFNI Facility",
    author_email="support@dafni.ac.uk",
    url="https://github.com/dafnifacility/cli",
    description="A CLI to access the DAFNI APIs from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    install_requires=["click>=7.1.2", "requests>=2.25.1", "python-dateutil>=2.8.1"],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        dafni=dafni_cli.dafni:dafni
    """,
)