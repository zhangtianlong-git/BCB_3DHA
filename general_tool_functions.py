
import math
import json
import numpy as np


def intersection(x1, y1, radian1, x2, y2, radian2):
    """
    Given the coordinates and azimuths of two vectors, calculate the intersection
    point coordinates
    """
    v1 = np.array([np.cos(radian1), np.sin(radian1)])
    v2 = np.array([np.cos(radian2), np.sin(radian2)])

    p1 = np.array([x1, y1])
    p2 = np.array([x2, y2])

    cross = np.cross(v2, v1)

    t = np.cross(p1 - p2, v2) / cross

    inter = p1 + t * v1
    return inter


def distance_point_to_line(A, B):
    """
    A is a tuple containing the x, y coordinates and azimuth of vector A. B is
    a tuple containing the x, y coordinates of point B. The function returns
    the distance from the vertical line of the point B to the vector A
    """
    x1, y1, angle = A
    x2, y2 = B
    k = math.tan(angle)
    if k == 0:
        return abs(y2 - y1)
    else:
        k2 = -1 / k
        b1 = y1 - k * x1
        b2 = y2 - k2 * x2
        x = (b2 - b1) / (k - k2)
        y = k * x + b1
        return math.sqrt((x - x2) ** 2 + (y - y2) ** 2)


def distance_point_to_point(A, B):
    x1, y1 = A
    x2, y2 = B
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def save_dict(dictionary, file_path):
    with open(file_path, "w") as file:
        json.dump(dictionary, file)


def load_dict(file_path):
    with open(file_path, "r") as file:
        dictionary = json.load(file)
    return dictionary


def read_txt_to_lists(file_path):
    x = []
    y = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            x.append(float(parts[0]))
            y.append(float(parts[1]))
    return x, y


def write_lists_to_txt(x, y, file_path):
    with open(file_path, 'w') as f:
        for i in range(len(x)):
            f.write(f"{x[i]},{y[i]}\n")