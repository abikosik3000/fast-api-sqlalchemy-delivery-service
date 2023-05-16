import re

from pydantic import BaseModel


def time_intervals_validator(intervals: list[str]) -> bool:
    if len(intervals) == 0:
        return intervals

    time_regex = r"^([0-1][0-9]|2[0-3]):([0-5][0-9])-([0-1][0-9]|2[0-3]):([0-5][0-9])$"
    int_intervals = []
    for interval in intervals:
        if not re.match(time_regex, interval):
            raise ValueError("incorrect interval")
        int_intervals.append(
            (
                int(interval[0:2]) * 60 + int(interval[3:5]),
                int(interval[6:8]) * 60 + int(interval[9:11]),
            )
        )

    int_intervals = sorted(int_intervals)
    min_pos = int_intervals[0][0]
    for interval in int_intervals:
        left = interval[0]
        right = interval[1]
        if left > right:
            raise ValueError("incorrect interval")
        if left < min_pos:
            raise ValueError("the intervals should not overlap")
        min_pos = interval[1]

    return intervals


class OrmBaseModel(BaseModel):
    class Config:
        orm_mode = True
