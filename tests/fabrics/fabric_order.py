import random


class FabricOrder:

    orders_arr = [{
        "cost": 100,
        "delivery_hours": [
            "12:23-16:40",
            "18:20-19:40"
        ],
        "regions": 1,
        "weight": 0
    }]

    MAX_REGION = 9
    MAX_W_H = 4
    COST = [50, 500]
    MAX_WEIGHT = 40

    def __init__(self):
        pass

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
            "cost": random.randint(self.COST[0], self.COST[1]),
            "delivery_hours": self._rand_w_h(),
            "regions": random.randint(0, self.MAX_REGION),
            "weight": random.randint(1, self.MAX_WEIGHT),
        })


if __name__ == "__main__":
    import json
    fabric = FabricOrder()
    obj = []
    for i in range(100):
        obj.append(fabric.create())
    print(json.dumps({'orders': obj}))
