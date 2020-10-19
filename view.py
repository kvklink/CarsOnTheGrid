import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np

from base import Simulation
from help import unzip, X_MAX, Y_MAX, fig_size, NUM_OF_CARS, NUM_OF_MOVES, get_dist


class GUI:
    @staticmethod
    def show() -> None:
        plt.show()
        plt.clf()
        plt.close()

    @staticmethod
    def save(name: str) -> None:
        plt.tight_layout()
        plt.savefig(f"{name}.png")
        plt.clf()
        plt.close()


class GUIFinalPos(GUI):
    def __init__(self, sim: Simulation, mod, solo: bool) -> None:
        self.sim: Simulation = sim
        self.mod = mod
        self.solo: bool = solo
        if solo:
            self.fig = plt.figure(figsize=fig_size)
        else:
            self.fig = plt.figure(figsize=(fig_size[0] * 2, fig_size[1]))
            self.ax1 = self.fig.add_subplot(121, xlim=[0, X_MAX], ylim=[0, Y_MAX])
            self.ax1.set_xticks(np.arange(0, X_MAX + 1, 5))
            self.ax1.set_yticks(np.arange(0, Y_MAX + 1, 5))

    def draw(self) -> None:
        # draw all final positions:
        for car in self.sim.cars:
            fx, fy = car.courses[-1]
            if self.mod:
                self.ax1.plot(fx % X_MAX, fy % X_MAX, "go", markersize=2)
            else:
                self.ax1.plot(fx, fy, "go", markersize=2)

        # for RD, to validate target positions
        # for car in self.sim.cars:
        #     self.ax1.plot(*unzip(car.targets[1:], False), "ro", markersize=2)

        source_courses = self.sim.cars[0].courses
        self.ax1.plot(*unzip(source_courses, self.mod), "bo", markersize=2)
        source_targets = self.sim.cars[0].targets
        self.ax1.plot(*unzip(source_targets, self.mod), "ro", markersize=4)

        self.ax1.set_xlabel("x axis", fontdict={"size": 12})
        self.ax1.set_ylabel("y axis", fontdict={"size": 12})
        self.ax1.set_title("final positions and the source's trace")
        blue_line = mlines.Line2D([], [], color='blue', marker='o', markersize=8, label="source's trace")
        red_line = mlines.Line2D([], [], color='red', marker='o', markersize=8, label="source's targets")
        green_line = mlines.Line2D([], [], color='green', marker='o', markersize=8, label="peers' final positions")
        self.ax1.legend(handles=[blue_line, red_line, green_line], loc='upper left')
        self.ax1.grid(True)


class GUIHeatMap(GUIFinalPos):
    def __init__(self, sim: Simulation, mod, solo):
        super().__init__(sim, mod, solo)
        if not solo:
            self.ax3 = self.fig.add_subplot(122)
        else:
            self.ax3 = self.fig.add_subplot(111)
        self.ax3.set_xticks(np.arange(0, X_MAX + 1, 5))
        self.ax3.set_yticks(np.arange(0, Y_MAX + 1, 5))

    def draw(self):
        if not self.solo:
            super().draw()

        hot_map = [[0 for _ in range(X_MAX + 1)] for _ in range(Y_MAX + 1)]
        for car in self.sim.cars[1:]:
            for target in car.courses:
                if self.mod:
                    int_target_x = int(target[0]) % X_MAX
                    int_target_y = int(target[1]) % Y_MAX
                else:
                    int_target_x = int(target[0])
                    int_target_y = int(target[1])
                hot_map[int_target_y][int_target_x] += 1
        # hot_map = list(reversed(hot_map))
        im = self.ax3.imshow(hot_map)
        c_bar = self.fig.colorbar(im, ax=self.ax3)
        c_bar.ax.set_ylabel("frequencies", rotation=-90, va="bottom", fontsize=20)
        self.ax3.set_title("the heat map of all cars' paths", fontsize=20)


class GUINumBro(GUIFinalPos):
    def __init__(self, sim: Simulation, mod, solo):
        super().__init__(sim, mod, solo)
        x_max = NUM_OF_MOVES if len(self.sim.num_of_broadcasters) <= NUM_OF_MOVES else len(self.sim.num_of_broadcasters)
        if not solo:
            self.ax3 = self.fig.add_subplot(122, xlim=[x_max - 500, x_max], ylim=[0, NUM_OF_CARS])
        else:
            self.ax3 = self.fig.add_subplot(111, xlim=[x_max - 500, x_max], ylim=[0, NUM_OF_CARS])

    def draw(self):
        if not self.solo:
            super().draw()

        xs = [i for i in range(len(self.sim.num_of_broadcasters))]
        self.ax3.plot(xs, self.sim.num_of_broadcasters, marker='o', markersize=3)

        self.ax3.set_xlabel("rounds", fontdict={"size": 12})
        self.ax3.set_ylabel("# of msg receivers", fontdict={"size": 12})
        self.ax3.set_title("rounds vs. # of msg receivers")
        self.ax3.grid(True)


class GUINumNei(GUIFinalPos):
    def __init__(self, sim: Simulation, mod, solo):
        super().__init__(sim, mod, solo)
        if not solo:
            self.ax2 = self.fig.add_subplot(122, xlim=[0, NUM_OF_MOVES], ylim=[0, 0.002])
        else:
            self.ax2 = self.fig.add_subplot(111, xlim=[0, NUM_OF_MOVES], ylim=[0, 0.002])

    def draw(self):
        if not self.solo:
            super().draw()

        xs = [i for i in range(len(self.sim.neighbor_percentage))]
        self.ax2.plot(xs, self.sim.neighbor_percentage, marker='o')
        self.ax2.grid(True)


class GUISnapshot(GUI):
    def __init__(self, sim: Simulation, count=6, interval=10):
        assert count in [6, 12, 150]
        assert interval > 0
        self.sim = sim
        self.axs = []
        self.interval = interval
        if count == 6:
            self.fig = plt.figure(figsize=(fig_size[0] * 4, fig_size[1] * 2))
            for i in range(6):
                axi = self.fig.add_subplot(2, 3, i + 1, xlim=[0, X_MAX], ylim=[0, Y_MAX])
                self.axs.append(axi)
        elif count == 12:
            self.fig = plt.figure(figsize=(fig_size[0] * 3, fig_size[1] * 4))
            for i in range(12):
                axi = self.fig.add_subplot(4, 3, i + 1, xlim=[0, X_MAX], ylim=[0, Y_MAX])
                self.axs.append(axi)
        else:
            self.fig = plt.figure(figsize=(fig_size[0] * 10, fig_size[1] * 15))
            for i in range(150):
                axi = self.fig.add_subplot(15, 10, i + 1, xlim=[0, X_MAX], ylim=[0, Y_MAX])
                self.axs.append(axi)
        for axi in self.axs:
            axi.set_xticks(np.arange(0, X_MAX + 1, 5))
            axi.set_yticks(np.arange(0, Y_MAX + 1, 5))

    def draw(self):
        for i, axi in enumerate(self.axs):
            target_length = i * self.interval

            axi.set_title(f"at round {i * self.interval}")
            source_acc_length = 0
            for j, pos in enumerate(self.sim.cars[0].courses[1:]):
                source_acc_length += get_dist(*pos, *self.sim.cars[0].courses[j])
                if source_acc_length >= target_length:
                    source_courses = self.sim.cars[0].courses[:j + 1]
                    break
            else:
                raise Exception
            xys = list(zip(*source_courses))
            xs = list(map(lambda x: x % X_MAX, list(xys[0])))
            ys = list(map(lambda y: y % Y_MAX, list(xys[1])))
            self.axs[i].plot(xs, ys, "bo", markersize=2)
            self.axs[i].grid(True)

            for car in self.sim.cars:
                acc_length = 0
                for j, pos in enumerate(car.courses[1:]):
                    acc_length += get_dist(*pos, *car.courses[j])
                    if acc_length >= target_length:
                        x = pos[0] % X_MAX
                        y = pos[1] % Y_MAX
                        if car.when <= i * self.interval:
                            self.axs[i].plot(x, y, "go", markersize=4)
                        else:
                            self.axs[i].plot(x, y, "ro", markersize=4)
                        break


class GUISnapshot2(GUI):
    def __init__(self, sim: Simulation, rd=1):
        self.sim = sim
        self.i = rd
        self.fig = plt.figure(figsize=fig_size)
        self.axi = self.fig.add_subplot(1, 1, 1, xlim=[0, X_MAX], ylim=[0, Y_MAX])
        self.axi.set_xticks(np.arange(0, X_MAX + 1, 5))
        self.axi.set_yticks(np.arange(0, Y_MAX + 1, 5))

    def draw(self):
        i = self.i
        target_length = i

        self.axi.set_title(f"at round {i}")
        source_acc_length = 0
        for j, pos in enumerate(self.sim.cars[0].courses[1:]):
            source_acc_length += get_dist(*pos, *self.sim.cars[0].courses[j])
            if source_acc_length >= target_length:
                source_courses = self.sim.cars[0].courses[:j + 1]
                break
        else:
            raise Exception
        xys = list(zip(*source_courses))
        xs = list(map(lambda x: x % X_MAX, list(xys[0])))
        ys = list(map(lambda y: y % Y_MAX, list(xys[1])))
        self.axi.plot(xs, ys, "bo", markersize=4)
        self.axi.grid(True)

        for car in self.sim.cars:
            acc_length = 0
            for j, pos in enumerate(car.courses[1:]):
                acc_length += get_dist(*pos, *car.courses[j])
                if acc_length >= target_length:
                    x = pos[0] % X_MAX
                    y = pos[1] % Y_MAX
                    if car.when <= i:
                        self.axi.plot(x, y, "go", markersize=8)
                    else:
                        self.axi.plot(x, y, "ro", markersize=8)
                    break
