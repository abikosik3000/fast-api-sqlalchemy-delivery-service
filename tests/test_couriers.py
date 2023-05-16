import pytest
import urllib.parse
import datetime
import random

from fastapi.testclient import TestClient

from tests.helpers import _rand_list


ORDERS = 10
COURIERS = 10
COMPLETE = 5


@pytest.mark.parametrize("startDate", [datetime.datetime.today().strftime("%Y-%m-%d")])
@pytest.mark.parametrize(
    "endDate",
    [
        (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    ]
)
@pytest.mark.parametrize("courier_id", [random.randint(1, COURIERS)])
@pytest.mark.parametrize("count_complete", [COMPLETE, 0])
@pytest.mark.parametrize("count_couriers", [COURIERS])
@pytest.mark.parametrize("count_orders", [ORDERS])
def test_courier_metainfo_200(
        startDate: datetime.date,
        endDate: datetime.date,
        courier_id: int,
        order_complete,
        client: TestClient):
    params = {'startDate': startDate, 'endDate': endDate}
    response = client.get(
        f"couriers/meta-info/{str(courier_id)}?"
        + urllib.parse.urlencode(params)
    )
    assert response.status_code == 200


@pytest.mark.parametrize("count_couriers", [COURIERS])
@pytest.mark.parametrize("limit", _rand_list(2, COURIERS))
@pytest.mark.parametrize("offset", _rand_list(2, COURIERS))
def test_couriers_get(fill_couriers_db, limit, offset, client: TestClient):
    params = {"limit": limit, "offset": offset}
    response = client.get("/couriers?" + urllib.parse.urlencode(params))
    assert response.status_code == 200
    assert (
        len(response.json()['couriers'])
        == max(0, min(COURIERS - offset, limit))
    )


@pytest.mark.parametrize("count_couriers", [COURIERS])
@pytest.mark.parametrize("courier_id", _rand_list(2, COURIERS))
def test_courier_get(fill_couriers_db, courier_id, client: TestClient):
    response = client.get("/couriers/" + str(courier_id))
    assert response.status_code == 200
    assert response.json()["courier_id"] == courier_id
