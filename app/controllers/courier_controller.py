from datetime import date, datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.managers.courier_mgr import CourierMgr
from app.shemas.orders_assign_sheme import OrderAssignResponse
from app.shemas.courier_sheme import (
    CreateCourierRequest,
    CreateCouriersResponse,
    GetCourierResponse,
    GetCourierMetaInfoResponse,
    CourierDto
)


class CourierController:
    def get_courier_metainfo(
        courier_id: int, startDate: date, endDate: date, db: Session
    ) -> GetCourierMetaInfoResponse:
        courier = CourierMgr.get_by_id(courier_id, db)
        if courier is None:
            raise HTTPException(status_code=404, detail="Not found")

        earnings = CourierMgr.courier_earnings(
            courier_id, startDate, endDate, db)
        raiting = CourierMgr.courier_raiting(
            courier_id, startDate, endDate, db)

        courier_meta_info_response = GetCourierMetaInfoResponse(
            **courier.to_courier_dto().dict()
        )
        if earnings is not None:
            courier_meta_info_response.earnings = earnings
        if raiting is not None:
            courier_meta_info_response.raiting = raiting
        return courier_meta_info_response

    def get_couriers_assigments(
        date: date, courier_id: int, db: Session
    ) -> OrderAssignResponse:
        if date is None:
            date = datetime.now().date()
        if courier_id is None:
            couriers = CourierMgr.get_all(db)
        else:
            couriers = [CourierMgr.get_by_id(courier_id, db)]
        return OrderAssignResponse(
            date=date,
            couriers=[
                courier.to_courier_group_orders(date)
                for courier in couriers
            ],
        )

    def post_couriers(
        create_courier_req: CreateCourierRequest, db: Session
    ) -> CreateCouriersResponse:
        new_couriers = CourierMgr.create_couriers(
            create_courier_req.couriers, db
        )
        return CreateCouriersResponse(
            couriers=[courier.to_courier_dto() for courier in new_couriers]
        )

    def get_couriers(limit: int, offset: int, db: Session) -> GetCourierResponse:
        couriers = CourierMgr.get_all(db, limit=limit, offset=offset)
        return GetCourierResponse(
            offset=offset,
            limit=limit,
            couriers=[courier.to_courier_dto() for courier in couriers],
        )

    def get_courier(courier_id: int, db: Session) -> CourierDto:
        courier = CourierMgr.get_by_id(courier_id, db)
        if courier is None:
            raise HTTPException(status_code=404, detail="Not found")
        return courier.to_courier_dto()
