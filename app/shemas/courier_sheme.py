import enum

from pydantic import StrictInt, StrictStr, validator
from typing import List, Optional

from app.shemas.base_sheme import OrmBaseModel, time_intervals_validator


class CourierTypeEnum(str, enum.Enum):
    FOOT = "FOOT"
    BIKE = "BIKE"
    AUTO = "AUTO"


class CourierBase(OrmBaseModel):
    courier_type: CourierTypeEnum
    regions: List[StrictInt]
    working_hours: List[StrictStr]

    _validate_interval = validator("working_hours", allow_reuse=True)(
        time_intervals_validator
    )


class CourierDto(CourierBase):
    courier_id: StrictInt


class CreateCouriersResponse(OrmBaseModel):
    couriers: List[CourierDto]


class CreateCourierDto(CourierBase):
    pass


class CreateCourierRequest(OrmBaseModel):
    couriers: List[CreateCourierDto]


class GetCourierResponse(OrmBaseModel):
    limit: StrictInt
    offset: StrictInt
    couriers: List[CourierDto]


class GetCourierMetaInfoResponse(CourierDto):
    earnings: Optional[StrictInt]
    raiting: Optional[StrictInt]
