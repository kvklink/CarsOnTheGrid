import math

import numpy as np
from PIL import Image

X_MAX = 50
Y_MAX = X_MAX
NUM_OF_CARS = 25
NUM_OF_MOVES = 100000
PRE_RUN_COUNT = 100
EXCEED_MOVES = False

fig_size = (7, 7)

assert 0 < X_MAX
assert 0 < Y_MAX
assert 1 < NUM_OF_CARS  # We need at least one car next to the source car
assert 0 < NUM_OF_MOVES


def get_dist(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


def get_euclidean_dist(x1, y1, x2, y2):
    comp1 = min(abs(x1 - x2), X_MAX - abs(x1 - x2)) ** 2
    comp2 = min(abs(y1 - y2), Y_MAX - abs(y1 - y2)) ** 2
    return math.sqrt(comp1 + comp2)


def unzip(courses, mod):
    xys = list(zip(*courses))
    if mod:
        xs = list(map(lambda x: x % X_MAX, list(xys[0])))
        ys = list(map(lambda y: y % Y_MAX, list(xys[1])))
    else:
        xs = list(map(lambda x: x, list(xys[0])))
        ys = list(map(lambda y: y, list(xys[1])))
    return xs, ys


def load_heatmap(input_image: str) -> np.matrix:
    """Convert input image into matrix of probabilities

    If none is given, will raise a FileNotFoundError
    Input must be a 100x100 image, otherwise an AttributeError is raised

    :param input_image: str
        Path to image to be converted
    """

    if input_image is None:
        raise FileNotFoundError('Missing input file for probability grid')

    # Open image, and convert to grayscale
    image = Image.open(input_image).convert('L')

    if image.size != (100, 100):
        raise AttributeError('Input image must be 100x100 pixels')

    # Normalize image into a probability matrix where total sum == 1
    image_matrix = np.matrix(image).transpose()
    return image_matrix / image_matrix.sum()


def rwp_1_diagonal():
    pair = [(X_MAX, Y_MAX), (0, 0)]
    trace = []
    for i in range(100):
        trace.extend(pair)
    return trace


def rwp_2_diagonal():
    trace = [(X_MAX * 100, Y_MAX * 100)]
    return trace


def rd_diagonal():
    return rwp_1_diagonal()


def mg_1_diagonal():
    x, y = 0, 0
    trace = []
    for i in range(X_MAX):
        trace.append((x, y))
        x += 1
        trace.append((x, y))
        y += 1
    trace.append((x, y))
    course = []
    for i in range(5):
        course.extend(trace[1:])
        course.extend(list(reversed(trace[:-1])))
    return course


def mg_2_diagonal():
    x, y = 0, 0
    trace = []
    for _ in range(1000 ** 100):
        x += 1
        trace.append((x, y))
        y += 1
        trace.append((x, y))

    return trace


def rwp_2_up():
    return [(25, 5000000) for _ in range(1000)]


def rwp_2_right():
    return [(5000000, 25) for _ in range(1000)]


def rwp_2_zigzag_14():
    targets = []
    for i in range(0, 100000, 5):
        tgts = [(i, i), (i + 1, i + 4), (i + 4, i + 1)]
        targets.extend(tgts)
    return targets[1:]


def rwp_2_zigzag_23():
    targets = []
    for i in range(0, 100000, 5):
        tgts = [(i, i), (i + 2, i + 3), (i + 3, i + 2)]
        targets.extend(tgts)
    return targets[1:]


def rectangle():
    targets = [(25, 25)]
    for _ in range(100000):
        targets.append((25, 10))
        targets.append((40, 10))
        targets.append((40, 40))
        targets.append((10, 40))
        targets.append((10, 10))

    return targets


def diamond():
    targets = [(25, 25)]
    for _ in range(10000):
        targets.append((25, 10))
        targets.append((40, 25))
        targets.append((25, 40))
        targets.append((10, 25))


if __name__ == '__main__':
    print(rwp_2_zigzag_14())
