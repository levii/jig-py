import os


test_root_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["PYTEST_TEST_ROOT_DIR"] = test_root_dir
os.environ["PYTEST_ROOT_DIR"] = os.path.dirname(test_root_dir)
