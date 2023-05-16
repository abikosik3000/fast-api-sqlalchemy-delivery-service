import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TimeInterval(Base):
    '''abstract class for tabels having time interval fields
    '''
    __abstract__ = True

    time_interval_id: Mapped[int] = mapped_column(primary_key=True)
    time_from: Mapped[datetime.time] = mapped_column()
    time_before: Mapped[datetime.time] = mapped_column()

    def section(self) -> tuple[int, int]:
        '''return section start and ending interval in minutes'''
        return (
            self.time_from.minute + self.time_from.hour * 60,
            self.time_before.minute + self.time_before.hour * 60,
        )

    def __repr__(self) -> str:
        return str(self.section()[0]) + " " + str(self.section()[1])
