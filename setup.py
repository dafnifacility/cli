from setuptools import setup, find_packages

# The dynamic metadata for the python pip distributable.
# This is used as the build script for setuptools, telling it about the package and which files to include.
# For more information, see https://packaging.python.org/tutorials/packaging-projects/

setup(
    name='dafni',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'typing',
        'datetime'
    ],
    entry_points='''
        [console_scripts]
        login=dafni_cli.login:login
        get=dafni_cli.get:get
    ''',
)