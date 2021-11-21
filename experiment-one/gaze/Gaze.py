
class Gaze(object):

    def subscribe(self):
        raise NotImplementedError("Should have implemented this")

    def unsubscribe(self):
        raise NotImplementedError("Should have implemented this")

    def getGazeDirection(self):
        raise NotImplementedError("Should have implemented this")

    def getHeadAngles(self):
        raise NotImplementedError("Should have implemented this")

    def isLookingAtRobot(self):
        raise NotImplementedError("Should have implemented this")

    def lookingAtRobotScore(self):
        raise NotImplementedError("Should have implemented this")
