from typing import List
from sqlalchemy.orm import Session

from app.models.order_model import Order
from app.models.delivery_hours_model import DeliveryHours
from app.shemas.order_sheme import CreateOrderDto, CompleteOrderRequestDto
from app.managers.time_interval_mgr import TimeIntervalMgr


class OrderMgr(TimeIntervalMgr):

    @classmethod
    def complete_orders(
        cls, complete_order_req: CompleteOrderRequestDto, db: Session
    ) -> list[Order]:
        '''complete orders using CompleteOrderRequestDto
        and return list Orders
        '''
        completed_orders = []
        for completed_info in complete_order_req.complete_info:
            order = cls.get_by_id(completed_info.order_id, db)
            completed_orders.append(
                order.complete(
                    completed_info.complete_time,
                    db
                )
            )
        return completed_orders

    @classmethod
    def create_order(cls, data: CreateOrderDto, db: Session) -> Order:
        '''create Order model and comit it to bd'''
        order = Order(
            weight=data.weight,
            regions=data.regions,
            cost=data.cost,
            delivery_hours=TimeIntervalMgr._prepare_create(
                DeliveryHours, data.delivery_hours)
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @classmethod
    def create_orders(cls, data_list: List[CreateOrderDto], db: Session) -> list[Order]:
        return [cls.create_order(data, db) for data in data_list]

    @classmethod
    def get_by_id(cls, id: int, db: Session) -> Order | None:
        return db.query(Order).get(id)

    @classmethod
    def get_all(cls, db: Session, limit: int = None, offset: int = None) -> list[Order]:
        '''get list orders using pagination'''
        if (limit is not None and offset is not None):
            return db.query(Order).offset(offset).limit(limit).all()
        else:
            return db.query(Order).all()
