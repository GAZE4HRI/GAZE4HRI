import math


def transformToDeg(direction):
    res = []
    if not direction is None:
        for rad in direction:
           res.append(math.degrees(rad))
    return tuple(res)


def transformToRad(direction):
    res = []
    if not direction is None:
        for deg in direction:
            res.append(math.radians(deg))
    return tuple(res)