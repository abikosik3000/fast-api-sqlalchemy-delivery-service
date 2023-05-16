from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.time_interval_model import TimeInterval


class WorkingHours(TimeInterval):
    __tablename__ = "working_hours"

    courier_id: Mapped[int] = mapped_column(ForeignKey("courier.courier_id"))
    parent = relationship("Courier")
