from datetime import datetime, time, date

from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from sqlalchemy.engine import Result

from app.managers.order_mgr import OrderMgr
from app.managers.courier_mgr import CourierMgr
from app.shemas.courier_sheme import CourierTypeEnum
from app.models.free_time_model import FreeTime
from app.models.group_order_model import GroupOrder
from app.models.courier_model import Courier
from app.models.order_model import Order
from app.models.working_hours_model import WorkingHours


class AssignOrdeerMgr:

    MAX_WEIGHT_TYPES = {"FOOT": 10, "BIKE": 20, "AUTO": 40}
    FIRST_DELIVERY_TIME = {"FOOT": 25, "BIKE": 12, "AUTO": 8}
    NEXT_DELIVERY_TIME = {"FOOT": 10, "BIKE": 8, "AUTO": 4}
    MAX_DELIVERY = {"FOOT": 2, "BIKE": 4, "AUTO": 7}
    MAX_REGIONS = {"FOOT": 1, "BIKE": 2, "AUTO": 3}

    @classmethod
    def init_free_time(cls, db: Session) -> None:
        '''initializate temp table by copy working hours values'''
        FreeTime.truncate(db)
        for w_h in db.execute(
            select(
                WorkingHours.time_from,
                WorkingHours.time_before,
                WorkingHours.courier_id,
            )
        ).all():
            FreeTime.create(w_h[0], w_h[1], w_h[2], db)

    @classmethod
    def get_orders_to_feth(cls, db: Session) -> Result:
        q = (
            select(Order.order_id)
            .where(Order.completed_time.is_(None))
            .order_by(Order.regions)
            .order_by(Order.weight.desc())
            .order_by(Order.order_id)
        )
        return db.execute(q)

    @classmethod
    def get_couriers_to_fech(cls, type, db: Session) -> Result:
        q = (
            select(Courier.courier_id)
            .where(Courier.courier_type == type)
            .order_by(Courier.courier_id)
        )
        return db.execute(q)

    @classmethod
    def open_group_orders_in_region_for_courier(
        cls, region: int, courier_id: int, db: Session
    ) -> list[GroupOrder]:
        return (
            db.query(GroupOrder)
            .where(
                and_(
                    GroupOrder.open == True,
                    GroupOrder.region == region,
                    GroupOrder.courier_id == courier_id,
                )
            )
            .all()
        )

    @classmethod
    def assignments(cls, date: date, db: Session) -> None:
        '''assigns (or reassigns) all outstanding orders on the specified date
        '''
        PRIORITY_ASSIGN = [
            (CourierTypeEnum.FOOT, cls.try_append_first_group_order),
            (CourierTypeEnum.BIKE, cls.try_append_first_group_order),
            (CourierTypeEnum.AUTO, cls.try_append_first_group_order),
            (CourierTypeEnum.AUTO, cls.try_no_indent_free_time),
            (CourierTypeEnum.BIKE, cls.try_no_indent_free_time),
            (CourierTypeEnum.FOOT, cls.try_no_indent_free_time),
            (CourierTypeEnum.AUTO, cls.try_assign_first_freetime),
            (CourierTypeEnum.BIKE, cls.try_assign_first_freetime),
            (CourierTypeEnum.FOOT, cls.try_assign_first_freetime),
        ]
        cls.init_free_time(db)
        GroupOrder.truncate_from_date(date, db)
        order_ids = cls.get_orders_to_feth(db)
        while True:
            order_id = order_ids.fetchone()
            if order_id is None:
                break
            order = OrderMgr.get_by_id(order_id, db)
            for priority in PRIORITY_ASSIGN:
                if order.weight > cls.MAX_WEIGHT_TYPES[priority[0]]:
                    continue

                couriers = cls.get_couriers_to_fech(priority[0], db)
                if cls._try_assign_to_couriers(date, order, couriers, priority[1], db):
                    break
        db.commit()

    @classmethod
    def _try_assign_to_couriers(
        cls,
        date: datetime,
        order: Order,
        couriers: Result,
        try_assign,
        db: Session,
    ) -> bool:
        """tries to assign an order to a courier using the assignment function"""
        while True:
            courier_id = couriers.fetchone()
            if courier_id is None:
                break
            courier = CourierMgr.get_by_id(courier_id, db)
            if try_assign(date, order, courier, db):
                return True
        return False

    @classmethod
    def try_append_first_group_order(
        cls, date: date, order: Order, courier: Courier, db: Session
    ) -> bool:
        """tries to attach an order to the first possible group order"""
        FIRST_DELIVERY_TIME = cls.FIRST_DELIVERY_TIME[courier.courier_type]
        TIME_DELIVERY = cls.NEXT_DELIVERY_TIME[courier.courier_type]
        group_orders = cls.open_group_orders_in_region_for_courier(
            order.regions, courier.courier_id, db
        )
        if len(group_orders) == 0:
            return False

        possible_sections, free_times, _ = cls._posible_sections(
            courier, order, TIME_DELIVERY, db
        )
        sect_group_orders = [
            (g_o.time_before_minutes(), g_o.time_before_minutes() + FIRST_DELIVERY_TIME)
            for g_o in group_orders
        ]
        # we get all the time periods
        # for which an order can be added to an existing group order
        possible_sections, free_times, group_orders = cls._intersect_arr_sections(
            possible_sections, sect_group_orders, free_times, group_orders
        )

        for i in range(len(possible_sections)):
            sect_possible = possible_sections[i]
            free_time = free_times[i]
            group_order = group_orders[i]
            if sect_possible[1] - sect_possible[0] < TIME_DELIVERY:
                continue

            cls._asign_to_group_order(
                order,
                group_order,
                free_time,
                sect_possible[0],
                sect_possible[0] + TIME_DELIVERY,
                db,
            )
            return True
        return False

    @classmethod
    def try_assign_first_freetime(
        cls, date: date, order: Order, courier: Courier, db: Session
    ) -> bool:
        """assigns an order at the first possible free time
        creating new group order
        """
        TIME_DELIVERY = cls.FIRST_DELIVERY_TIME[courier.courier_type]
        possible_sections, free_times, _ = cls._posible_sections(
            courier, order, TIME_DELIVERY, db
        )

        for i in range(len(possible_sections)):
            sect_possible = possible_sections[i]
            free_time = free_times[i]
            if sect_possible[1] - sect_possible[0] < TIME_DELIVERY:
                continue

            group_order = GroupOrder.create(date, courier.courier_id, db)
            cls._asign_to_group_order(
                order,
                group_order,
                free_time,
                sect_possible[0],
                sect_possible[0] + TIME_DELIVERY,
                db,
            )
            return True
        return False

    @classmethod
    def try_no_indent_free_time(
        cls, date: date, order: Order, courier: Courier, db: Session
    ) -> bool:
        """try assigns an order at the first possible free time without indent
        """
        TIME_DELIVERY = cls.FIRST_DELIVERY_TIME[courier.courier_type]
        free_times = FreeTime.get_all_for_courier(courier.courier_id, db)
        delivery_hours = order.delivery_hours
        sect_free_times = [
            (
                f_t.section()[0],
                min(f_t.section()[0] + TIME_DELIVERY, f_t.section()[1])
            )
            for f_t in free_times
        ]
        sect_start_delivery = [
            (
                d_h.section()[0] - TIME_DELIVERY,
                d_h.section()[1] - TIME_DELIVERY
            )
            for d_h in delivery_hours
        ]
        possible_sections, free_times, _ = cls._intersect_arr_sections(
            sect_free_times, sect_start_delivery, free_times, delivery_hours
        )

        for i in range(len(possible_sections)):
            sect_possible = possible_sections[i]
            free_time = free_times[i]
            if sect_possible[1] - sect_possible[0] < TIME_DELIVERY:
                continue

            group_order = GroupOrder.create(date, courier.courier_id, db)
            cls._asign_to_group_order(
                order,
                group_order,
                free_time,
                sect_possible[0],
                sect_possible[0] + TIME_DELIVERY,
                db,
            )
            return True
        return False

    @classmethod
    def _posible_sections(
        cls, courier: Courier, order: Order, time_delivery: int, db: Session
    ):
        """returns all the time intervals from the couriers' free time
        to which the order can be delivered
        """
        free_times = FreeTime.get_all_for_courier(courier.courier_id, db)
        delivery_hours = order.delivery_hours
        sect_free_times = [f_t.section() for f_t in free_times]
        sect_start_delivery = [
            (d_h.section()[0] - time_delivery,
             d_h.section()[1] - time_delivery)
            for d_h in delivery_hours
        ]
        return cls._intersect_arr_sections(
            sect_free_times, sect_start_delivery, free_times, delivery_hours
        )

    @classmethod
    def _asign_to_group_order(
        cls,
        order: Order,
        group_order: GroupOrder,
        f_t: FreeTime,
        planned_time_from: int,
        planned_time_before: int,
        db: Session,
    ):
        '''planned group order and assign it to group order'''
        planned_time = [
            cls._minute_to_time(planned_time_from),
            cls._minute_to_time(planned_time_before),
        ]
        f_t.planned_order(planned_time[0], planned_time[1], db)
        order.assign_to_group_order(
            group_order.courier_id,
            group_order.group_order_id,
            planned_time[0],
            planned_time[1],
            db,
        )
        db.refresh(group_order)
        group_order.region = order.regions
        if (
            len(group_order.planned_orders)
            == cls.MAX_DELIVERY[group_order.courier.courier_type]
        ):
            group_order.close(db)

    @staticmethod
    def _intersect_arr_sections(a: list[int], b: list[int], a_objs: list, b_objs: list):
        a = sorted(zip(a, a_objs))
        b = sorted(zip(b, b_objs))
        ia = 0
        ib = 0
        open_a = False
        open_b = False
        answer = []
        answer_a_objs = []
        answer_b_objs = []
        last_open = None
        while ia // 2 < len(a) and ib // 2 < len(b):
            el_a = a[ia // 2][0][ia % 2]
            el_b = b[ib // 2][0][ib % 2]
            a_obj = a[ia // 2][1]
            b_obj = b[ib // 2][1]
            if el_a <= el_b:
                open_a = not open_a
                ia += 1
            if el_b <= el_a:
                open_b = not open_b
                ib += 1
            if last_open is None and open_a and open_b:
                last_open = min(el_a, el_b)
            elif last_open is not None:
                answer.append((last_open, min(el_a, el_b)))
                answer_a_objs.append(a_obj)
                answer_b_objs.append(b_obj)
                last_open = None
        return answer, answer_a_objs, answer_b_objs

    @staticmethod
    def _minute_to_time(minutes) -> time:
        return time(minutes // 60, minutes % 60)
