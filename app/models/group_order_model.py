import datetime

from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base
from sqlalchemy.orm import Session
from app.models.order_model import Order
from app.shemas.orders_assign_sheme import GroupOrders


class GroupOrder(Base):
    __tablename__ = "group_order"

    group_order_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime.date] = mapped_column()
    region: Mapped[int] = mapped_column(nullable=True, default=None)
    open: Mapped[bool] = mapped_column(default=True)

    planned_orders: Mapped[List["Order"]
                           ] = relationship()
    courier_id: Mapped[int] = mapped_column(
        ForeignKey("courier.courier_id"),
        nullable=True,
        default=None
    )
    courier = relationship("Courier", back_populates="group_orders")

    def time_from(self) -> datetime.time | None:
        '''returns the minimum start time of the orders included in it
        '''
        if len(self.planned_orders) == 0:
            return None
        start_time = self.planned_orders[0].planned_time_from
        for order in self.planned_orders:
            start_time = min(start_time, order.planned_time_from)
        return start_time

    def time_before(self) -> datetime.time | None:
        '''returns the maximum end time of the orders included in it
        '''
        if len(self.planned_orders) == 0:
            return None
        start_time = self.planned_orders[0].planned_time_before
        for order in self.planned_orders:
            start_time = max(start_time, order.planned_time_before)
        return start_time

    def time_before_minutes(self) -> int:
        '''returns the maximum end time of the orders included in it
        in minutes'''
        time_before = self.time_before()
        return (time_before.hour * 60 + time_before.minute)

    def time_from_minutes(self) -> int:
        '''returns the minimum start time of the orders included in it
        in minutes'''
        time_from = self.time_from()
        return (time_from.hour * 60 + time_from.minute)

    def close(self, db: Session) -> None:
        '''close group order'''
        self.open = False
        db.commit()

    def to_group_order_dto(self) -> GroupOrders:
        '''convert to GroupOrders sheme'''
        return GroupOrders(
            group_order_id=self.group_order_id,
            orders=[order.to_order_dto() for order in self.planned_orders]
        )

    @classmethod
    def get_by_id(cls, id: int, db: Session) -> 'GroupOrder':
        return db.query(cls).get(id)

    @classmethod
    def create(cls, date: datetime.date, courier_id: int, db: Session) -> 'GroupOrder':
        group_order = cls(courier_id=courier_id, date=date)
        db.add(group_order)
        db.commit()
        db.refresh(group_order)
        return group_order

    @classmethod
    def truncate_from_date(cls, date: datetime.date, db: Session) -> None:
        '''delete all group orders from date'''
        db.query(cls).where(cls.date >= date).delete()
        db.commit()
