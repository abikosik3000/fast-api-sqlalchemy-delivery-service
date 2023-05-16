import pytest

from fastapi.testclient import TestClient


ORDERS = 30
COURIERS = 30


@pytest.mark.parametrize("count_couriers", [COURIERS])
@pytest.mark.parametrize("count_orders", [ORDERS])
def test_assign_201(assign_orders):
    pass


def test_ping(client: TestClient):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
