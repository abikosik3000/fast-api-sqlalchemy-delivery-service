import datetime

from pydantic import StrictInt, StrictStr, validator
from typing import List, Optional

from app.shemas.base_sheme import OrmBaseModel, time_intervals_validator


class CompleteOrder(OrmBaseModel):
    courier_id: StrictInt
    order_id: StrictInt
    complete_time: datetime.datetime


class CompleteOrderRequestDto(OrmBaseModel):
    complete_info: List[CompleteOrder]


class OrderBase(OrmBaseModel):
    cost: StrictInt
    delivery_hours: List[StrictStr]
    regions: StrictInt
    weight: float

    _validate_interval = validator("delivery_hours", allow_reuse=True)(
        time_intervals_validator
    )


class CreateOrderDto(OrderBase):
    pass


class CreateOrderRequest(OrmBaseModel):
    orders: List[CreateOrderDto]


class OrderDto(OrderBase):
    order_id: StrictInt
    completed_time: Optional[datetime.datetime]
