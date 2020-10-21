from random import Random

from help import *


class Car:
    def __init__(self, index: int, seed: float, source_pos: (int, int), targets: [(int, int)] = None) -> None:
        assert 0 <= index
        self.index: int = index
        self.when: int = 0 if index == 0 else -1
        self.rand: Random = Random(f"{seed}+{self.index}")
        if self.index == 0:
            pos: (int, int) = source_pos
        else:
            while True:
                x_pos: float = self.rand.uniform(0, X_MAX)  # !
                y_pos: float = self.rand.uniform(0, Y_MAX)
                if x_pos != source_pos[0] or y_pos != source_pos[1]:
                    pos = (x_pos, y_pos)
                    break
        self.courses: [(int, int)] = [pos]
        self.targets: [(int, int)] = [pos]
        if targets is not None:
            self.targets.extend(targets)
        self.target_idx: int = 1

    def set_target(self) -> None:
        assert False, "not implemented"

    def move(self) -> None:
        assert False, "not implemented"

    def get_pos(self) -> (int, int):
        cx = self.courses[-1][0]
        cy = self.courses[-1][1]
        return cx, cy

    def get_target(self) -> (int, int):
        self.set_target()
        tx = self.targets[self.target_idx][0]
        ty = self.targets[self.target_idx][1]
        return tx, ty

    def get_prev_target(self) -> (int, int):
        px = self.targets[self.target_idx - 1][0]
        py = self.targets[self.target_idx - 1][1]
        return px, py

    def truncate(self) -> None:
        self.set_target()
        self.courses = self.courses[-1:]
        self.targets = self.targets[-2:]
        self.target_idx = 1


class SynCar(Car):
    def move(self) -> None:
        step = 1
        while step > 0:
            # if the car sees a repeated target
            # it won't move but stays at the current pos
            px, py = self.get_prev_target()
            tx, ty = self.get_target()
            if tx == px and ty == py:
                self.courses.append((tx, ty))
                return

            cx, cy = self.get_pos()
            dist = get_dist(cx, cy, tx, ty)
            if step >= dist:
                self.courses.append((tx, ty))
                self.target_idx += 1
                step -= dist
            else:
                dx = (tx - cx) * step / dist
                dy = (ty - cy) * step / dist
                cx = cx + dx
                cy = cy + dy
                self.courses.append((cx, cy))
                return


class SynMGCar(Car):
    def __init__(self, index, seed, source_pos, targets=None, car_type=1) -> None:
        super().__init__(index, seed, source_pos, targets)
        if self.index == 0:
            pos = source_pos
        else:
            while True:
                if car_type == 1:
                    x_pos = self.rand.choice([i for i in range(0, X_MAX + 1)])
                    y_pos = self.rand.choice([i for i in range(0, Y_MAX + 1)])
                else:
                    x_pos = self.rand.choice([i for i in range(0, X_MAX)])
                    y_pos = self.rand.choice([i for i in range(0, Y_MAX)])
                if x_pos != source_pos[0] or y_pos != source_pos[1]:
                    pos = (x_pos, y_pos)
                    break
        self.courses = [pos]
        self.targets = [pos]
        if targets is not None: self.targets.extend(targets)

    def move(self) -> None:
        px, py = self.get_prev_target()
        tx, ty = self.get_target()
        if px != tx or py != ty:
            self.target_idx += 1
        self.courses.append((tx, ty))


class Simulation:
    def __init__(self) -> None:
        self.cars: [Car] = []
        self.num_of_broadcasters: [int] = []
        self.neighbor_percentage: [float] = []

    def cars_move(self) -> None:
        [car.move() for car in self.cars]

    def propagate(self, rd) -> None:
        assert False, "not implemented"

    def calculate_num_of_broadcasters(self) -> None:
        num = 0
        for car in self.cars:
            if car.when >= 0:
                num += 1
        self.num_of_broadcasters.append(num)

    def calculate_neighbor_percentage(self) -> None:
        assert False, "not implemented"

    def simulate(self) -> None:
        for _ in range(PRE_RUN_COUNT):
            for car in self.cars[1:]:
                car.move()
        for car in self.cars[1:]:
            car.truncate()
        self.calculate_num_of_broadcasters()
        # self.calculate_neighbor_percentage()  ###

        rd = 1
        while self.num_of_broadcasters[-1] != NUM_OF_CARS:
            self.cars_move()
            self.propagate(rd)
            self.calculate_num_of_broadcasters()
            # self.calculate_neighbor_percentage()  ###
            if not EXCEED_MOVES and rd == NUM_OF_MOVES:
                break
            rd += 1

    def summary(self) -> ([(int, int)], [(int, int)], int, int):
        courses: [(int, int)] = []
        targets: [(int, int)] = []
        for car in self.cars:
            courses.append(car.courses)
            targets.append(car.targets)
        return courses, targets, self.num_of_broadcasters, self.neighbor_percentage


class SynSimulation(Simulation):
    def propagate(self, rd: int) -> None:
        broadcaster_pos_list = [car.get_pos() for car in self.cars if car.when >= 0]
        for car in self.cars:
            if car.when == -1:
                for pos in broadcaster_pos_list:
                    dist = get_dist(*pos, *car.get_pos())
                    if dist <= 1:
                        car.when = rd
                        break

    def calculate_neighbor_percentage(self) -> None:
        rates = []
        for car in self.cars:
            num_of_neighbours = -1
            for c in self.cars:
                if get_dist(*c.get_pos(), *car.get_pos()) <= 1:
                    num_of_neighbours += 1
            rate = num_of_neighbours / NUM_OF_CARS
            rates.append(rate)
        self.neighbor_percentage.append((sum(rates) / NUM_OF_CARS))


class TorSynSimulation(Simulation):
    def propagate(self, rd) -> None:
        broadcaster_pos_list: [(int, int)] = [car.get_pos() for car in self.cars if car.when >= 0]
        mod_pos_list: [(int, int)] = list(map(lambda p: (p[0] % X_MAX, p[1] % Y_MAX), broadcaster_pos_list))
        for car in self.cars:
            if car.when == -1:
                car_x, car_y = car.get_pos()
                car_x, car_y = car_x % X_MAX, car_y % Y_MAX
                for pos in mod_pos_list:
                    dist = get_euclidean_dist(*pos, car_x, car_y)
                    if dist <= 1:
                        car.when = rd
                        break

    def calculate_neighbor_percentage(self) -> None:
        original_positions = [car.get_pos() for car in self.cars]
        mod_positions = list(map(lambda pos: (pos[0] % X_MAX, pos[1] % Y_MAX), original_positions))
        rates = []
        for pos1 in mod_positions:
            num_of_nbrs = -1  # minus itself
            for pos2 in mod_positions:
                if get_euclidean_dist(*pos1, *pos2) <= 1:
                    num_of_nbrs += 1
            rate = num_of_nbrs / NUM_OF_CARS
            rates.append(rate)
        self.neighbor_percentage.append((sum(rates) / NUM_OF_CARS))
