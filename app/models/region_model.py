from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Region(Base):
    __tablename__ = "region"

    region_id: Mapped[int] = mapped_column(primary_key=True)
    region_num: Mapped[int] = mapped_column()
    courier_id: Mapped[int] = mapped_column(ForeignKey("courier.courier_id"))
