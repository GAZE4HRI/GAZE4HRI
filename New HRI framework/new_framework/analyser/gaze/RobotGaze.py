import time
from threading import currentThread

from utils.Utils import transformToDeg


class RobotGaze(object):
    def __init__(self, session):
        super(RobotGaze, self).__init__()

        # Get the service ALMemory.
        self.period = 0.05
        self.memory = session.service("ALMemory")
        # Connect the event callback.
        self.subscriber = self.memory.subscriber("GazeAnalysis/PersonStartsLookingAtRobot")
        self.subscriber.signal.connect(self.onPersonStartsLookingAtRobot)
        self.subscriber2 = self.memory.subscriber("GazeAnalysis/PersonStopsLookingAtRobot")
        self.subscriber2.signal.connect(self.onPersonStopsLookingAtRobot)
        self.subscriber3 = self.memory.subscriber("GazeAnalysis/PeopleLookingAtRobot")
        self.subscriber3.signal.connect(self.onPeopleLookingAtRobot)

        self.gaze_detection = session.service("ALGazeAnalysis")
        self.gaze_detection.subscribe("Gaze")
        self.id = None

    def onPersonStartsLookingAtRobot(self, id):
        """ This will be called each time a person starts looking at robot."""

        self.id = id
        print('PersonStartsLookingAtRobot occured: %s ' % id)

    def onPersonStopsLookingAtRobot(self, id):
        """ This will be called each time a person stops looking at robot."""

        self.id = None
        print('PersonStopsLookingAtRobot occured %s' % id)

    def onPeopleLookingAtRobot(self, idList):
        """ This will be called each time people looking at robot changes."""

        print('PeopleLookingAtRobot occured %s' % idList)
        # TODO - should we handle this somehow or assume only one person interacts with a robot?


    def unsubscribe(self):
        self.gaze_detection.unsubscribe("Gaze")

    def getHeadAngles(self):
        val = None
        if self.id is not None:
            # (yaw, pitch, roll) in radians
            val = self.memory.getData("PeoplePerception/Person/%s/HeadAngles" % self.id)
        return val

    def getGazeDirection(self):
        val = None
        if self.id is not None:
            # [yaw, pitch] in radians
            val = self.memory.getData("PeoplePerception/Person/%s/GazeDirection" % self.id)
        return val

    def isLookingAtRobot(self):
        val = self.memory.getData("PeoplePerception/Person/%s/IsLookingAtRobot" % self.id)
        return val

    def lookingAtRobotScore(self):
        val = self.memory.getData("PeoplePerception/Person/%s/LookingAtRobotScore" % self.id)
        return val

    def run(self, name):
        """
        Loop on, wait for events until manual interruption.
        """
        f = open(name, 'w')
        print "Starting Gaze Record"
        # num = int(waitTime / self.period)
        t = currentThread()
        while getattr(t, "do_run", True):
            try:
                headAngles = self.getHeadAngles()
                gazeDirection = self.getGazeDirection()
                direction = self.sum(gazeDirection, headAngles)
                f.write( str(transformToDeg(headAngles)) + " " + str(transformToDeg(gazeDirection)) +
                        " " + str(transformToDeg(direction)) + " \n")
            except:
                f.write("(0.0,0.0,0.0) (0.0,0.0) (0.0,0.0,0.0)")
                print "Robot gaze couldn't perform gaze analysis sorry, please contact administrator"

            time.sleep(self.period)

    def sum(self, gazeDirection, headAngles):
        if gazeDirection is None or headAngles is None or not gazeDirection or not headAngles:
            return []
        return (gazeDirection[0] + headAngles[0], gazeDirection[1] + headAngles[1], headAngles[2])

