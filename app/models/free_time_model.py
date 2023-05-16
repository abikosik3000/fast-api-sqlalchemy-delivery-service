from datetime import time

from sqlalchemy import ForeignKey, delete
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import Session
from app.models.time_interval_model import TimeInterval


class FreeTime(TimeInterval):
    '''temp table, helps assign orders'''
    __tablename__ = "free_time"

    courier_id: Mapped[int] = mapped_column(
        ForeignKey("courier.courier_id"), nullable=True
    )

    def planned_order(self, time_from: time, time_before: time, db: Session) -> None:
        FreeTime.create(self.time_from, time_from, self.courier_id, db)
        FreeTime.create(time_before, self.time_before, self.courier_id, db)
        db.execute(
            delete(FreeTime).where(
                FreeTime.time_interval_id == self.time_interval_id)
        )
        db.commit()

    @staticmethod
    def get_all_for_courier(courier_id: int, db: Session) -> list['FreeTime']:
        return db.query(FreeTime).where(FreeTime.courier_id == courier_id).all()

    @classmethod
    def create(cls, time_from: time, time_before: time, courier_id: int, db: Session) -> 'FreeTime':
        if time_before == time_from:
            return None
        f_t = cls(time_from=time_from, time_before=time_before,
                  courier_id=courier_id)
        db.add(f_t)
        db.commit()
        return f_t

    @classmethod
    def truncate(cls, db: Session) -> None:
        db.query(cls).delete()
        db.commit()
