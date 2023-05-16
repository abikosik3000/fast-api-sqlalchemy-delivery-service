import random


class FabricCourier:

    COURIER_TYPES = ["FOOT", "BIKE", "AUTO"]
    MAX_COUNT_REGIONS = 6
    MAX_REGION = 9
    MAX_W_H = 4

    def __init__(self):
        pass

    def _rand_type(self):
        return self.COURIER_TYPES[random.randint(0, 2)]

    def _rand_regions(self):
        lng = random.randint(1, self.MAX_COUNT_REGIONS)
        return [random.randint(0, self.MAX_REGION) for _ in range(lng)]

    def _rand_w_h(self):
        lng = random.randint(1, self.MAX_W_H)
        minutes_points = set([random.randint(1, 1439) for _ in range(lng * 2)])
        minutes_points = list(sorted(minutes_points))
        w_h_arr = []
        for i in range(1, len(minutes_points), 2):
            hours, minutes = divmod(minutes_points[i - 1], 60)
            from_time = f"{hours:02d}:{minutes:02d}"
            hours, minutes = divmod(minutes_points[i], 60)
            begin_time = f"{hours:02d}:{minutes:02d}"
            w_h_arr.append(from_time+"-"+begin_time)
        return w_h_arr

    def create(self):
        return dict({
            "courier_type": self._rand_type(),
            "regions": self._rand_regions(),
            "working_hours": self._rand_w_h()
        })


if __name__ == "__main__":
    import json
    fabric = FabricCourier()
    obj = []
    for i in range(14):
        obj.append(fabric.create())
    print(json.dumps({"couriers": obj}))
