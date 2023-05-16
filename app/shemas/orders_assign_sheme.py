from datetime import date

from pydantic import StrictInt
from typing import List

from app.shemas.base_sheme import OrmBaseModel
from app.shemas.order_sheme import OrderDto


class GroupOrders(OrmBaseModel):
    group_order_id: StrictInt
    orders: List[OrderDto]


class CouriersGroupOrders(OrmBaseModel):
    courier_id: StrictInt
    orders: List[GroupOrders]


class OrderAssignResponse(OrmBaseModel):
    date: date
    couriers: List[CouriersGroupOrders]
