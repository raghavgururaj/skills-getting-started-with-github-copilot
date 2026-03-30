import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(scope="session")
def original_activities():
    return copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities(original_activities):
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    return TestClient(app_module.app)
