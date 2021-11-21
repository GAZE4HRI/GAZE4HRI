from enum import Enum


class GazeDirection(Enum):
    LOOKING_ON_LEFT_MIDDLE = "looking_on_left"
    LOOKING_ON_RIGHT_MIDDLE = "looking_on_right"
    LOOKING_ON_MIDDLE_UP = "looking_on_up"
    LOOKING_ON_MIDDLE_DOWN = "looking_on_down"
    LOOKING_ON_MIDDLE_MIDDLE = "looking_on_middle"

    LOOKING_ON_ROBOT_FACE = "looking_on_robot_face"
    LOOKING_ON_LEFT_DOWN = "looking_on_left_down"
    LOOKING_ON_RIGHT_DOWN = "looking_on_right_down"
    LOOKING_ON_LEFT_UP = "looking_on_left_up"
    LOOKING_ON_RIGHT_UP = "looking_on_top_right"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, GazeDirection))


class EventType(Enum):
    GAZE_AVERTING = "gaze_averting"
    Emotion_OCCURRED = "emotion_occurred"
    QUESTION_DETECTED = "question_detected"
    SILENCE_DETECTED = "silence_detected"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, EventType))



class SystemState(Enum):
    WAIT = "wait"
    IDLE = "idle"
    IN_BLOCKING_ACTION = "block_action"
    IN_NON_BLOCKING_ACTION = "action"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, EventType))