from pathlib import Path

from setuptools import setup, find_packages

with open(Path("docs", "dafni_cli.md"), encoding="utf-8") as f:
    long_description = f.read()

# The dynamic metadata for the python pip distributable.
# This is used as the build script for setuptools, telling it about the package and which files to include.
# For more information, see https://packaging.python.org/tutorials/packaging-projects/

setup(
    name="dafni-cli",
    # TODO see if we can use dafni python packaging
    version="0.0.1",
    author="DAFNI Facility",
    author_email="support@dafni.ac.uk",
    url="https://github.com/dafnifacility/cli",
    description="A CLI to access the DAFNI APIs from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    install_requires=["click>=8.1.3", "requests>=2.28.2", "python-dateutil>=2.8.2"],
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
