from enum import Enum


class GazeDirection(Enum):
    LOOKING_ON_LEFT_MIDDLE = "looking_on_left"
    LOOKING_ON_RIGHT_MIDDLE = "looking_on_right"
    LOOKING_ON_MIDDLE_UP = "looking_on_up"
    LOOKING_ON_MIDDLE_DOWN = "looking_on_down"
    LOOKING_ON_MIDDLE_MIDDLE = "looking_on_middle"
    LOOKING_ON_TOP_RIGHT = "looking_on_top_right"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, GazeDirection))





