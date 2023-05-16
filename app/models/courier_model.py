import enum
from datetime import date

from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.region_model import Region
from app.models.working_hours_model import WorkingHours
from app.models.group_order_model import GroupOrder
from app.models.free_time_model import FreeTime
from app.shemas.courier_sheme import CourierDto
from app.shemas.orders_assign_sheme import CouriersGroupOrders


class CourierTypeEnum(str, enum.Enum):
    FOOT = "FOOT"
    BIKE = "BIKE"
    AUTO = "AUTO"


class Courier(Base):
    __tablename__ = "courier"

    courier_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    courier_type: Mapped[CourierTypeEnum] = mapped_column()

    regions: Mapped[List["Region"]] = relationship()
    working_hours: Mapped[List["WorkingHours"]] = relationship()
    group_orders: Mapped[List["GroupOrder"]
                         ] = relationship(back_populates="courier")
    free_times: Mapped[List["FreeTime"]] = relationship()

    def to_courier_group_orders(self, date: date) -> CouriersGroupOrders:
        '''convert to sheme CouriersGroupOrders'''
        return CouriersGroupOrders(
            courier_id=self.courier_id,
            orders=[
                group_order.to_group_order_dto()
                for group_order in self.group_orders
                if group_order.date == date
            ]
        )

    def to_courier_dto(self) -> CourierDto:
        '''convert to sheme CourierDto'''
        TIME_FORMAT = "%H:%M"
        return CourierDto(
            courier_id=self.courier_id,
            courier_type=self.courier_type,
            regions=[reg.region_num for reg in self.regions],
            working_hours=[
                w_h.time_from.strftime(TIME_FORMAT)
                + "-"
                + w_h.time_before.strftime(TIME_FORMAT)
                for w_h in self.working_hours
            ]
        )
