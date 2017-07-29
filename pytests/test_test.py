import time

import pytest


@pytest.mark.timeout(2)
def test_one():
    time.sleep(1)
    assert True


@pytest.mark.timeout(2)
def test_two():
    time.sleep(3)
    assert True

def test_three():
    time.sleep(3)
    assert True
