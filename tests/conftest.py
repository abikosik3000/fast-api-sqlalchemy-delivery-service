import pytest
import datetime
import random

from fastapi.testclient import TestClient
from app.main import app

from tests.fabrics.fabric_order import FabricOrder
from tests.fabrics.fabric_courier import FabricCourier


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture
def fill_orders_db(client: TestClient, count_orders):
    fabric_order = FabricOrder()
    orders_arr = [fabric_order.create() for _ in range(count_orders)]
    response = client.post("/orders", json={"orders": orders_arr})
    assert response.status_code == 200
    yield count_orders
    client.get("/migrate?drop")


@pytest.fixture
def fill_couriers_db(client: TestClient, count_couriers):
    fabric_courier = FabricCourier()
    couriers_arr = [fabric_courier.create() for _ in range(count_couriers)]
    response = client.post("/couriers", json={"couriers": couriers_arr})
    assert response.status_code == 200

    yield count_couriers
    client.get("/migrate?drop")


@pytest.fixture
def fill_db(fill_orders_db, fill_couriers_db, client: TestClient):
    return fill_orders_db, fill_couriers_db


@pytest.fixture
def assign_orders(fill_db, client: TestClient):
    response = client.post("/orders/assign")
    assert response.status_code == 201
    return client.get("/couriers/assigments").json()


@pytest.fixture
def couriers_orders_assign(assign_orders: dict):
    courier_ids = [
        courier["courier_id"] for courier in assign_orders["couriers"]
    ]
    orders_ids = []
    for courier in assign_orders["couriers"]:
        courier_orders = []
        for group_order in courier["orders"]:
            for order in group_order["orders"]:
                courier_orders.append(order["order_id"])
        orders_ids.append(courier_orders)
    return dict(zip(courier_ids, orders_ids))


@pytest.fixture
def order_complete(count_complete, couriers_orders_assign: dict, client: TestClient):
    date = datetime.datetime.now().isoformat()
    pair_to_assingn = set()
    for _ in range(count_complete):
        courier_id = random.choice(list(couriers_orders_assign.keys()))
        if len(couriers_orders_assign[courier_id]) == 0:
            continue
        order_id = random.choice(couriers_orders_assign[courier_id])
        pair_to_assingn.add((courier_id, order_id))

    complete_info = []
    for pair in pair_to_assingn:
        complete_info.append(
            {
                "courier_id": pair[0],
                "order_id": pair[1],
                "complete_time": date,
            }
        )
    response = client.post(
        "/orders/complete", json={"complete_info": complete_info},
    )
    assert response.status_code == 200
    return pair_to_assingn, couriers_orders_assign


@pytest.fixture(autouse=True, scope="session")  # autouse=True scope="session",
def prepare_truncate_db():
    client = TestClient(app)
    client.get("/migrate?drop")
    yield
    client.get("/migrate?drop")
