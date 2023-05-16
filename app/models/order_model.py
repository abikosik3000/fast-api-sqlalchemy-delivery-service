import datetime

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.delivery_hours_model import DeliveryHours
from app.shemas.order_sheme import OrderDto


class Order(Base):
    __tablename__ = "order"

    order_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    weight: Mapped[float] = mapped_column()
    regions: Mapped[int] = mapped_column()
    cost: Mapped[int] = mapped_column()
    completed_time: Mapped[datetime.datetime] = mapped_column(
        nullable=True, default=None
    )
    planned_time_from: Mapped[datetime.time] = mapped_column(
        nullable=True, default=None
    )
    planned_time_before: Mapped[datetime.time] = mapped_column(
        nullable=True, default=None
    )

    delivery_hours: Mapped[List["DeliveryHours"]] = relationship(lazy="joined")
    group_order_id: Mapped[int] = mapped_column(
        ForeignKey("group_order.group_order_id", ondelete="SET NULL"),
        nullable=True, default=None
    )
    complete_courier_id: Mapped[int] = mapped_column(
        ForeignKey("courier.courier_id", ondelete="SET NULL"),
        nullable=True, default=None
    )

    def complete(
        self,
        completed_time: datetime.datetime,
        db: Session
    ) -> 'Order':
        '''complete order'''
        self.completed_time = completed_time
        db.commit()
        return self

    def assign_to_group_order(
        self,
        courier_id: int,
        group_order_id: int,
        planned_time_from: int,
        planned_time_before: int,
        db: Session
    ) -> None:
        '''fill planned times and assign to group orders'''
        self.complete_courier_id = courier_id
        self.group_order_id = group_order_id
        self.planned_time_from = planned_time_from
        self.planned_time_before = planned_time_before
        db.commit()

    def to_order_dto(self) -> OrderDto:
        '''convert to OrderDto sheme'''
        TIME_FORMAT = "%H:%M"
        return OrderDto(
            order_id=self.order_id,
            regions=self.regions,
            weight=self.weight,
            cost=self.cost,
            completed_time=self.completed_time,
            delivery_hours=[
                x.time_from.strftime(TIME_FORMAT)
                + "-"
                + x.time_before.strftime(TIME_FORMAT)
                for x in self.delivery_hours
            ]
        )
