import pytest
import urllib.parse
import datetime

from fastapi.testclient import TestClient

from tests.helpers import _rand_list

ORDERS = 10
COURIERS = 10
COMPLETE = 5


@pytest.mark.parametrize("count_complete", [COMPLETE])
@pytest.mark.parametrize("count_couriers", [COURIERS])
@pytest.mark.parametrize("count_orders", [ORDERS])
def test_order_complete(order_complete, client: TestClient):

    # and test code 400 if order not assign
    complete_info = {
        "courier_id": COURIERS + 1,
        "order_id": ORDERS + 1,
        "complete_time": datetime.datetime.now().isoformat()
    }
    response = client.post(
        "/orders/complete", json={"complete_info": complete_info},
    )
    assert response.status_code == 400


@pytest.mark.parametrize("count_orders", [ORDERS])
@pytest.mark.parametrize("limit", _rand_list(2, ORDERS))
@pytest.mark.parametrize("offset", _rand_list(2, ORDERS))
def test_orders_get(fill_orders_db, limit, offset, client: TestClient):
    params = {"limit": limit, "offset": offset}
    response = client.get("/orders?" + urllib.parse.urlencode(params))
    assert response.status_code == 200
    assert len(response.json()) == max(0, min(ORDERS - offset, limit))


@pytest.mark.parametrize("count_orders", [ORDERS])
@pytest.mark.parametrize("order_id", _rand_list(2, ORDERS))
def test_order_get(fill_orders_db, order_id, client: TestClient):
    response = client.get("/orders/" + str(order_id))
    assert response.status_code == 200
    assert response.json()["order_id"] == order_id
