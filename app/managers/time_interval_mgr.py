from abc import ABC
import datetime

from typing import List

from app.database import Base


class TimeIntervalMgr(ABC):

    @staticmethod
    def _prepare_create(model, data: str) -> List[Base]:
        '''prepari time interval to creating
        by convert str to time objects'''
        time_interval_arr = []
        for t in data:
            times = [
                datetime.datetime.strptime(i, '%H:%M').time()
                for i in t.split("-")
            ]
            time_interval_arr.append(
                model(time_from=times[0], time_before=times[1])
            )
        return time_interval_arr
