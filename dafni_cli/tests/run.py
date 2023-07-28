import os, unittest


def load_tests(loader, standard_tests, pattern):
    # See https://stackoverflow.com/questions/66651858/run-unittest-against-installed-packages
    this_dir = os.path.dirname(__file__)
    pattern = pattern or "test_*.py"
    top_level_dir = os.path.dirname(os.path.dirname(this_dir))
    package_tests = loader.discover(
        start_dir=this_dir,
        pattern=pattern,
        top_level_dir=top_level_dir,
    )
    standard_tests.addTests(package_tests)
    return standard_tests


if __name__ == "__main__":
    unittest.main()
