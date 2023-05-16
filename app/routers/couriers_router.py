from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.shemas.courier_sheme import (
    CreateCourierRequest,
    CreateCouriersResponse,
    GetCourierResponse,
    CourierDto,
    GetCourierMetaInfoResponse,
)
from app.shemas.orders_assign_sheme import OrderAssignResponse
from app.controllers.courier_controller import CourierController
from app.dependencies import get_db


router = APIRouter()


@router.get(
    "/couriers/meta-info/{courier_id}",
    response_model=GetCourierMetaInfoResponse,
    status_code=status.HTTP_200_OK,
)
def get_courier_metainfo(
    courier_id: int, startDate: date, endDate: date, db: Session = Depends(get_db)
):
    return CourierController.get_courier_metainfo(courier_id, startDate, endDate, db)


@router.get(
    "/couriers/assigments",
    response_model=OrderAssignResponse,
    status_code=status.HTTP_200_OK,
)
def get_couriers_assigments(
    date: date = None, courier_id: int = None, db: Session = Depends(get_db)
):
    return CourierController.get_couriers_assigments(date, courier_id, db)


@router.post(
    "/couriers", response_model=CreateCouriersResponse, status_code=status.HTTP_200_OK
)
def post_couriers(
    create_courier_req: CreateCourierRequest, db: Session = Depends(get_db)
):
    return CourierController.post_couriers(create_courier_req, db)


@router.get(
    "/couriers", response_model=GetCourierResponse, status_code=status.HTTP_200_OK
)
def get_couriers(limit: int = 1, offset: int = 0, db: Session = Depends(get_db)):
    return CourierController.get_couriers(limit, offset, db)


@router.get(
    "/couriers/{courier_id}", response_model=CourierDto, status_code=status.HTTP_200_OK
)
def get_courier(courier_id: int, db: Session = Depends(get_db)):
    return CourierController.get_courier(courier_id, db)
