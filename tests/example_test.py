import os
import tempfile

import pytest


@pytest.fixture
def setup_and_teardown():
    print("Setup...")
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # run tests
    print("Teardown...")
    os.rmdir(temp_dir)


def test_example(setup_and_teardown):
    temp_dir = setup_and_teardown
    print(f"Temp directory is {temp_dir}")
    assert temp_dir != None
