import qi
import time
import sys
import argparse


class HumanGreeter(object):
    """
    A simple class to react to face detection events.
    """

    def __init__(self, session):
        """
        Initialisation of qi framework and event detection.
        """
        super(HumanGreeter, self).__init__()


        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Connect the event callback.
        self.subscriber = self.memory.subscriber("GazeAnalysis/PersonStartsLookingAtRobot")
        self.subscriber.signal.connect(self.onPersonStartsLookingAtRobot)
        self.subscriber2 = self.memory.subscriber("GazeAnalysis/PersonStopsLookingAtRobot")
        self.subscriber2.signal.connect(self.onPersonStopsLookingAtRobot)
        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        self.gaze_detection = session.service("ALGazeAnalysis")
        self.gaze_detection.subscribe("HumanGreeter")
        self.got_face = False
        self.id = None

    def onPersonStartsLookingAtRobot(self, id):
        self.id = id
        print('PersonStartsLookingAtRobot occured: %s ' % id)

    def onPersonStopsLookingAtRobot(self, id):
        """ This will be called each time a person stops looking at robot."""

        self.id = None
        print('PersonStopsLookingAtRobot occured %s' % id)

    def getGazeDirection(self):
        val = None
        if self.id is not None:
            # [yaw, pitch] in radians
            val = self.memory.getData("PeoplePerception/Person/%s/GazeDirection" % self.id)
        return val

    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting HumanGreeter"
        try:
            while True:
                print self.getGazeDirection()
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping HumanGreeter"
            self.gaze_detection.unsubscribe("HumanGreeter")
            #stop
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    human_greeter = HumanGreeter(session)
    human_greeter.run()
