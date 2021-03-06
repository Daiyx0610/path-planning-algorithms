"""
Field D* 2D
@author: huiming zhou
"""

import os
import sys
import math
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)) +
                "/../../Search-based Planning/")

from Search_2D import plotting
from Search_2D import env


class FieldDStar:
    def __init__(self, s_start, s_goal, heuristic_type):
        self.s_start, self.s_goal = s_start, s_goal
        self.heuristic_type = heuristic_type

        self.Env = env.Env()  # class Env
        self.Plot = plotting.Plotting(s_start, s_goal)

        self.u_set = self.Env.motions  # feasible input set
        self.obs = self.Env.obs  # position of obstacles
        self.x = self.Env.x_range
        self.y = self.Env.y_range

        self.g, self.rhs, self.OPEN = {}, {}, {}
        self.parent = {}
        self.cknbr = {}
        self.ccknbr = {}
        self.bptr = {}
        self.init_table()

        for i in range(self.Env.x_range):
            for j in range(self.Env.y_range):
                self.rhs[(i, j)] = float("inf")
                self.g[(i, j)] = float("inf")
                self.bptr[(i, j)] = (i, j)

        self.rhs[self.s_goal] = 0.0
        self.OPEN[self.s_goal] = self.CalculateKey(self.s_goal)
        self.visited = set()
        self.count = 0
        self.fig = plt.figure()

    def init_table(self):
        for i in range(1, self.Env.x_range - 1):
            for j in range(1, self.Env.y_range - 1):
                s_neighbor = self.get_neighbor_pure((i, j))
                s_neighbor.append(s_neighbor[0])
                for k in range(8):
                    self.cknbr[((i, j), s_neighbor[k])] = s_neighbor[k + 1]
                s_neighbor = list(reversed(s_neighbor))
                for k in range(8):
                    self.ccknbr[((i, j), s_neighbor[k])] = s_neighbor[k + 1]

    def run(self):
        self.Plot.plot_grid("Field D*")
        self.ComputeShortestPath()
        self.plot_path(self.extract_path())
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        plt.show()

    def on_press(self, event):
        x, y = event.xdata, event.ydata
        if x < 0 or x > self.x - 1 or y < 0 or y > self.y - 1:
            print("Please choose right area!")
        else:
            x, y = int(x), int(y)
            print("Change position: x =", x, ",", "y =", y)
            self.visited = set()
            self.count += 1

            if (x, y) not in self.obs:
                self.obs.add((x, y))
                plt.plot(x, y, 'sk')
                sn_list = self.get_neighbor((x, y))
            else:
                self.obs.remove((x, y))
                plt.plot(x, y, marker='s', color='white')
                sn_list = [(x, y)]
                sn_list += self.get_neighbor((x, y))

            for s in sn_list:
                v_list = []
                for sn in self.get_neighbor(s):
                    v_list.append(self.ComputeCost(s, sn, self.ccknbr[(s, sn)]))
                self.rhs[s] = min(v_list)
                self.UpdateVertex(s)

            self.ComputeShortestPath()
            self.plot_visited(self.visited)
            self.plot_path(self.extract_path())
            self.fig.canvas.draw_idle()

    def ComputeShortestPath(self):
        while True:
            s, v = self.TopKey()
            if v >= self.CalculateKey(self.s_start) and \
                    self.rhs[self.s_start] == self.g[self.s_start]:
                break

            if self.g[s] > self.rhs[s]:
                self.g[s] = self.rhs[s]
                self.OPEN.pop(s)
                for sn in self.get_neighbor(s):
                    if self.rhs[sn] > self.ComputeCost(sn, s, self.ccknbr[(sn, s)]):
                        self.rhs[sn] = self.ComputeCost(sn, s, self.ccknbr[(sn, s)])
                        self.bptr[sn] = s
                    if self.rhs[sn] > self.ComputeCost(sn, s, self.cknbr[(sn, s)]):
                        self.rhs[sn] = self.ComputeCost(sn, self.cknbr[(sn, s)], s)
                        self.bptr[sn] = self.cknbr[(sn, s)]
                    self.UpdateVertex(sn)
            else:
                self.g[s] = float("inf")
                for sn in self.get_neighbor(s):
                    if self.bptr[sn] == s or self.bptr[sn] == self.cknbr[(sn, s)]:
                        v_list = []
                        ssn_list = self.get_neighbor(sn)
                        for ssn in ssn_list:
                            v_list.append(self.ComputeCost(sn, ssn, self.ccknbr[(sn, ssn)]))
                        self.rhs[sn] = min(v_list)
                        self.bptr[sn] = ssn_list[v_list.index(min(v_list))]
                        self.UpdateVertex(sn)
                self.UpdateVertex(s)

    def UpdateVertex(self, s):
        if self.g[s] != self.rhs[s]:
            self.OPEN[s] = self.CalculateKey(s)
        elif s in self.OPEN:
            self.OPEN.pop(s)

    def get_neighbor_pure(self, s):
        s_list = []

        for u in self.u_set:
            s_next = tuple([s[i] + u[i] for i in range(2)])
            s_list.append(s_next)

        return s_list

    def CalculateKey(self, s):
        return [min(self.g[s], self.rhs[s]) + self.h(self.s_start, s),
                min(self.g[s], self.rhs[s])]

    def ComputeCost(self, s, sa, sb):
        if sa[0] != s[0] and sa[1] != s[1]:
            s1, s2 = sb, sa
        else:
            s1, s2 = sa, sb

        c = self.cost(s, s2)
        b = self.cost(s, s1)

        if c != float("inf"):
            c = c / math.sqrt(2)

        if min(c, b) == float("inf"):
            vs = float("inf")
        elif self.g[s1] <= self.g[s2]:
            vs = min(c, b) + self.g[s1]
        else:
            f = self.g[s1] - self.g[s2]
            if f <= b:
                if c <= f:
                    vs = math.sqrt(2) * c + self.g[s2]
                else:
                    y = min(f / (math.sqrt(c ** 2 - f ** 2)), 1)
                    vs = c * math.sqrt(1 + y ** 2) + f * (1 - y) + self.g[s2]
            else:
                if c <= b:
                    vs = math.sqrt(2) * c + self.g[s2]
                else:
                    x = 1 - min(b / (math.sqrt(c ** 2 - b ** 2)), 1)
                    vs = c * math.sqrt(1 + (1 - x) ** 2) + b * x + self.g[s2]

        return vs

    def TopKey(self):
        """
        :return: return the min key and its value.
        """

        s = min(self.OPEN, key=self.OPEN.get)
        return s, self.OPEN[s]

    def h(self, s_start, s_goal):
        heuristic_type = self.heuristic_type  # heuristic type

        if heuristic_type == "manhattan":
            return abs(s_goal[0] - s_start[0]) + abs(s_goal[1] - s_start[1])
        else:
            return math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1])

    def cost(self, s_start, s_goal):
        """
        Calculate cost for this motion
        :param s_start: starting node
        :param s_goal: end node
        :return:  cost for this motion
        :note: cost function could be more complicate!
        """

        if self.is_collision(s_start, s_goal):
            return float("inf")

        return math.hypot(s_goal[0] - s_start[0], s_goal[1] - s_start[1])

    def is_collision(self, s_start, s_end):
        if s_start in self.obs or s_end in self.obs:
            return True

        if s_start[0] != s_end[0] and s_start[1] != s_end[1]:
            if s_end[0] - s_start[0] == s_start[1] - s_end[1]:
                s1 = (min(s_start[0], s_end[0]), min(s_start[1], s_end[1]))
                s2 = (max(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
            else:
                s1 = (min(s_start[0], s_end[0]), max(s_start[1], s_end[1]))
                s2 = (max(s_start[0], s_end[0]), min(s_start[1], s_end[1]))

            if s1 in self.obs or s2 in self.obs:
                return True

        return False

    def get_neighbor(self, s):
        s_list = []
        for u in self.u_set:
            s_next = tuple([s[i] + u[i] for i in range(2)])
            if s_next not in self.obs:
                s_list.append(s_next)

        return s_list

    def extract_path(self):
        path = [self.s_start]
        s = self.s_start
        count = 0
        while True:
            count += 1
            s = self.bptr[s]
            path.append(s)

            if s == self.s_goal or count > 100:
                return list(reversed(path))

    def plot_path(self, path):
        px = [x[0] for x in path]
        py = [x[1] for x in path]
        plt.plot(px, py, linewidth=2)
        plt.plot(self.s_start[0], self.s_start[1], "bs")
        plt.plot(self.s_goal[0], self.s_goal[1], "gs")

    def plot_visited(self, visited):
        color = ['gainsboro', 'lightgray', 'silver', 'darkgray',
                 'bisque', 'navajowhite', 'moccasin', 'wheat',
                 'powderblue', 'skyblue', 'lightskyblue', 'cornflowerblue']

        if self.count >= len(color) - 1:
            self.count = 0

        for x in visited:
            plt.plot(x[0], x[1], marker='s', color=color[self.count])


def main():
    s_start = (5, 5)
    s_goal = (45, 25)

    fielddstar = FieldDStar(s_start, s_goal, "euclidean")
    fielddstar.run()


if __name__ == '__main__':
    main()
