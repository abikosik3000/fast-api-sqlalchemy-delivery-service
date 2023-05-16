import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from typing import List

from app.shemas.order_sheme import (
    CreateOrderRequest,
    OrderDto,
    CompleteOrderRequestDto
)
from app.shemas.orders_assign_sheme import OrderAssignResponse
from app.controllers.order_controller import OrderController
from app.dependencies import get_db


router = APIRouter()


@router.post(
    "/orders/assign",
    response_model=OrderAssignResponse,
    status_code=status.HTTP_201_CREATED
)
def post_orders_assign(date: datetime.date = None, db: Session = Depends(get_db)):
    return OrderController.post_orders_assign(date, db)


@router.post(
    "/orders/complete", response_model=List[OrderDto], status_code=status.HTTP_200_OK
)
def post_orders_complete(
    complete_order_req: CompleteOrderRequestDto, db: Session = Depends(get_db)
):
    return OrderController.post_orders_complete(complete_order_req, db)


@router.post("/orders", response_model=List[OrderDto], status_code=status.HTTP_200_OK)
def post_orders(create_order_req: CreateOrderRequest, db: Session = Depends(get_db)):
    return OrderController.post_orders(create_order_req, db)


@router.get("/orders", response_model=List[OrderDto], status_code=status.HTTP_200_OK)
def get_couriers(limit: int = 1, offset: int = 0, db: Session = Depends(get_db)):
    return OrderController.get_orders(limit, offset, db)


@router.get(
    "/orders/{order_id}", response_model=OrderDto, status_code=status.HTTP_200_OK
)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return OrderController.get_order(order_id, db)
