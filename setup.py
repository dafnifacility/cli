from setuptools import setup, find_packages

setup(
    name="dafni",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click", "requests", "typing", "datetime"],
    entry_points="""
        [console_scripts]
        login=dafni_cli.login:login
        get=dafni_cli.get:get
    """,
)
