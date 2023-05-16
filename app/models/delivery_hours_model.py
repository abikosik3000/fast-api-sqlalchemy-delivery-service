from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.time_interval_model import TimeInterval


class DeliveryHours(TimeInterval):
    __tablename__ = "delivery_hours"

    order_id: Mapped[int] = mapped_column(ForeignKey("order.order_id"))
