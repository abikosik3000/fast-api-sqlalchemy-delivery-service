from datetime import date
import math

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from app.models.courier_model import Courier
from app.models.order_model import Order
from app.models.working_hours_model import WorkingHours
from app.models.region_model import Region
from app.shemas.courier_sheme import CreateCourierDto, CourierTypeEnum
from app.managers.time_interval_mgr import TimeIntervalMgr


class CourierMgr(TimeIntervalMgr):

    @classmethod
    def courier_earnings(
        cls, courier_id: int, startDate: date, endDate: date, db: Session
    ) -> int | None:
        '''calculates the courier's earning for the period'''
        courier = cls.get_by_id(courier_id, db)
        if courier.courier_type == CourierTypeEnum.AUTO:
            EARNING_MUL = 4
        elif courier.courier_type == CourierTypeEnum.BIKE:
            EARNING_MUL = 3
        elif courier.courier_type == CourierTypeEnum.FOOT:
            EARNING_MUL = 2
        q = select(func.sum(Order.cost) * EARNING_MUL).where(
            and_(
                Order.completed_time >= startDate,
                Order.completed_time < endDate,
                Order.complete_courier_id == courier.courier_id
            )
        )
        return db.execute(q).one()[0]

    @classmethod
    def courier_raiting(
        cls, courier_id: int, startDate: date, endDate: date, db: Session
    ) -> float | None:
        '''calculates the courier's rating for the period'''
        courier = cls.get_by_id(courier_id, db)
        if courier.courier_type == CourierTypeEnum.AUTO:
            RAITING_MUL = 1
        elif courier.courier_type == CourierTypeEnum.BIKE:
            RAITING_MUL = 2
        elif courier.courier_type == CourierTypeEnum.FOOT:
            RAITING_MUL = 3
        TOTAL_HOURS = (endDate - startDate).days * 24

        count_completed_orders = db.execute(
            select(func.count(Order.completed_time)).where(
                and_(
                    Order.complete_courier_id == courier_id,
                    Order.completed_time >= startDate,
                    Order.completed_time < endDate
                )
            )
        ).one()[0]
        if count_completed_orders == 0:
            return None

        raiting_double = RAITING_MUL / TOTAL_HOURS * count_completed_orders
        arithmetic_rounding = 0
        if (raiting_double - math.floor(raiting_double) >= 0.5):
            arithmetic_rounding = 1
        return math.floor(raiting_double) + arithmetic_rounding

    @classmethod
    def _create_regions(cls, data: List[int]) -> List[Region]:
        '''prepare to create regions'''
        return [Region(region_num=i) for i in data]

    @classmethod
    def create_courier(cls, data: CreateCourierDto, db: Session) -> Courier:
        '''create model courier and commit to bd'''
        new_courier = Courier(
            courier_type=data.courier_type,
            regions=cls._create_regions(data.regions),
            working_hours=cls._prepare_create(WorkingHours, data.working_hours)
        )
        db.add(new_courier)
        db.commit()
        db.refresh(new_courier)
        return new_courier

    @classmethod
    def create_couriers(cls, data_list: List[CreateCourierDto], db: Session) -> List[Courier]:
        return [cls.create_courier(data, db) for data in data_list]

    @classmethod
    def get_by_id(cls, id: int, db: Session) -> Courier | None:
        return db.query(Courier).get(id)

    @classmethod
    def get_all(cls, db: Session, limit: int = None, offset: int = None) -> list[Courier]:
        '''get list couriers using pagination'''
        if (limit is not None and offset is not None):
            return db.query(Courier).offset(offset).limit(limit).all()
        else:
            return db.query(Courier).all()
