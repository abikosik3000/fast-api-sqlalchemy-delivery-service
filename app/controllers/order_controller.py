import datetime

from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException

from app.controllers.courier_controller import CourierController
from app.managers.order_mgr import OrderMgr
from app.managers.assign_order_mgr import AssignOrdeerMgr
from app.shemas.orders_assign_sheme import OrderAssignResponse
from app.shemas.order_sheme import (
    CreateOrderRequest,
    OrderDto,
    CompleteOrderRequestDto
)


class OrderController:
    @staticmethod
    def validate_complete_order_req(
        complete_order_req: CompleteOrderRequestDto, db: Session
    ) -> bool:
        for complete_order in complete_order_req.complete_info:
            order = OrderMgr.get_by_id(complete_order.order_id, db)
            if order.complete_courier_id is None:
                return False
            if order.complete_courier_id != complete_order.courier_id:
                return False
        return True

    @classmethod
    def post_orders_assign(cls, date: datetime.date, db: Session) -> OrderAssignResponse:
        if date is None:
            date = datetime.datetime.now().date()
        AssignOrdeerMgr.assignments(date, db)
        return CourierController.get_couriers_assigments(date, None, db)

    @classmethod
    def post_orders_complete(
        cls, complete_order_req: CompleteOrderRequestDto, db: Session
    ) -> List[OrderDto]:

        if not cls.validate_complete_order_req(complete_order_req, db):
            raise HTTPException(status_code=400, detail="Bad Request")

        completed_orders = OrderMgr.complete_orders(complete_order_req, db)
        return [order.to_order_dto() for order in completed_orders]

    @classmethod
    def post_orders(
        cls, create_order_req: CreateOrderRequest, db: Session
    ) -> List[OrderDto]:
        pass
        new_orders = OrderMgr.create_orders(create_order_req.orders, db)
        return [order.to_order_dto() for order in new_orders]

    @classmethod
    def get_orders(cls, limit: int, offset: int, db: Session) -> List[OrderDto]:
        orders = OrderMgr.get_all(db, limit=limit, offset=offset)
        return [order.to_order_dto() for order in orders]

    @classmethod
    def get_order(cls, order_id: int, db: Session) -> OrderDto:
        order = OrderMgr.get_by_id(order_id, db)
        if order is None:
            raise HTTPException(status_code=404, detail="Not found")
        return order.to_order_dto()
