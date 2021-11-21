import cv2
import time

from gaze.Estimator import Estimator
from gaze.pyOpenFace.pyOpenFaceStub import PyOpenFaceStub
from utils.Utils import transformToDeg


class GazeEstimator(Estimator):
    def __init__(self, pyOpenFaceStub):
        self.pyOpenFaceStub = pyOpenFaceStub
        self.debug = True
    def estimate(self, frame, externalDetection = False):
        gaze = self.pyOpenFaceStub.getGaze(frame, externalDetection, self.debug)
        if self.debug:
            print "gaze" + str(gaze)
        angles = self.pyOpenFaceStub.getGazeAngle(gaze)
        if self.debug:
            print "angles" + str(transformToDeg(angles))
        return angles





if __name__ == "__main__":
    p = PyOpenFaceStub()
    gazeEstimator = GazeEstimator(p)

    face = cv2.imread('../test.jpg', 3)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    time_0 = time.time()
    yaw, pitch = transformToDeg(gazeEstimator.estimate(face))

    print yaw, pitch




    # cap = cv2.VideoCapture(0)
    # while (cap.isOpened()):
    #     ret, frame = cap.read()
    #     if ret == True:
    #         img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    #         time_0 = time.time()
    #         yaw, pitch = transformToDeg(gazeEstimator.estimate(img))
    #
    #         print yaw, pitch
    #         time_1 = time.time()
    #         print "detect take {:.4f} Second".format(time_1 - time_0)
            # cv2.imshow('frame', img)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break