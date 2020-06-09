import os

os.environ["PYTEST"] = "true"
os.environ["PYTEST_FIXTURES_PATH"] = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)
