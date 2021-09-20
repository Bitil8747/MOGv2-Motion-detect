import numpy as np


class VisibleObject:

    dist_arr = np.zeros(15)
    angle_arr = np.zeros(15)
    size = 0

    def __init__(self, dist='def', angle='def'):
        if dist != 'def':
            self.add_point(dist, angle)
            self.size = 1

    def add_point(self, dist, angle):
        self.dist_arr = np.roll(self.dist_arr, -1)
        self.angle_arr = np.roll(self.angle_arr, -1)
        self.dist_arr[14] = dist
        self.angle_arr[14] = angle
        self.size += 1

    def __len__(self):
        if self.size > 15:
            return 15
        else:
            return self.size
