from threading import currentThread

import cv2
import time

from gaze.FaceUtils import Face
from gaze.Gaze import Gaze
from gaze.GazeEstimator import GazeEstimator
from gaze.HeadEstimator import HeadEstimator
from gaze.NaoVideoSource import NaoVideoSourceRemote
from gaze.pyOpenFace.pyOpenFaceStub import PyOpenFaceStub
from utils.Utils import transformToDeg


class CustomGaze(Gaze):
    def __init__(self, session):
        self.pyOpenFaceStub = PyOpenFaceStub()
        self.gazeEstimator = GazeEstimator(self.pyOpenFaceStub)
        self.headEstimator = HeadEstimator(self.pyOpenFaceStub)
        self.videoSource = NaoVideoSourceRemote(session)
        self.frame = None
        self.countGaze = 0
        self.countHead = 0
        self.n = 1
        self.face = Face()
        self.period = 0.1

    def subscribe(self):
        self.videoSource.subscribeCamera()

    def lookingAtRobotScore(self):
        self.videoSource.unsubscribe()

    def getGazeDirection(self):
        self.countGaze = self.countGaze + 1
        if self.countGaze > 1 or self.countHead > 1:
            self.frame = None
            self.countGaze = 0
            self.countHead = 0

        if self.frame is None:
            frame = self.videoSource.getImage()
            self.videoSource.releaseImage()
            self.frame = frame
            # self.frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB)
            # self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)

        # cv2.imwrite('frame' + str(self.n) + '.jpg', self.frame)
        # self.n = self.n + 1
        # print type(self.frame)
        # face_rect = self.face.find_faces(self.frame)[0]
        # self.pyOpenFaceStub.getLandmarksInImage(self.frame,[face_rect.left(), face_rect.top(), face_rect.right(), face_rect.bottom()])
        gazeData = self.gazeEstimator.estimate(self.frame)
        return gazeData

    def isLookingAtRobot(self):
        pass

    def getHeadAngles(self):
        self.countHead = self.countHead + 1
        if self.countHead > 1 or self.countGaze > 1:
            self.frame = None
            self.countGaze = 0
            self.countHead = 0

        if self.frame is None:
            frame = self.videoSource.getImage()
            self.videoSource.releaseImage()
            self.frame = frame
            # self.frame = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB)
            # self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)

        headAngles = self.headEstimator.estimate(self.frame)


        return headAngles

    def reset(self):
        self.pyOpenFaceStub.reset()


    def unsubscribe(self):
        self.videoSource.unsubscribe()

    def run(self, name):
        """
        Loop on, wait for events until manual interruption.
        """
        # f = open(name, 'w')
        print "Starting Gaze Record"
        # num = int(waitTime / self.period)
        t = currentThread()
        while getattr(t, "do_run", True):
                frame = self.videoSource.getImage()
                self.videoSource.releaseImage()
                print type(frame)
                # headAngles = self.getHeadAngles()
                # gazeDirection = self.getGazeDirection()
                # direction = self.sum(gazeDirection, headAngles)
                # print direction
                # f.write( str(transformToDeg(headAngles)) + " " + str(transformToDeg(gazeDirection)) +
                #         " " + str(transformToDeg(direction)) + " \n")


            # time.sleep(self.period)


    def sum(self, gazeDirection, headAngles):
        if gazeDirection is None or headAngles is None or not gazeDirection or not headAngles:
            return []
        return (gazeDirection[0] , gazeDirection[1] , headAngles[2])

