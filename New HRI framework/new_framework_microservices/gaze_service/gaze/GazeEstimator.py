import cv2
import time

import math

from gaze.Estimator import Estimator
from gaze.FaceUtils import Face
from gaze.pyOpenFace.pyOpenFaceStub import PyOpenFaceStub

def transformToDeg(direction):
    res = []
    for rad in direction:
        res.append(math.degrees(rad))
    return tuple(res)


def transformToRad(direction):
    res = []
    for deg in direction:
        res.append(math.radians(deg))
    return tuple(res)


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

    cap = cv2.VideoCapture(0)
    f = open("./samples/gaze_id2.txt", 'w')
    counter = 100
    face = Face()
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:

            img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            time_0 = time.time()
            # f = face.find_faces(img)
            # if len(f) >= 1:

                # p.getLandmarksInImage(img,f[0])
            yaw, pitch = transformToDeg(gazeEstimator.estimate(img))
            print img.shape
            print yaw, pitch
            f.write("{0} {1}\n".format(yaw, pitch))
            f.flush()
            time_1 = time.time()
            # print "detect take {:.4f} Second".format(time_1 - time_0)
            cv2.imshow('frame', img)
            counter += 1
            if counter >=100:
                p.reset()
                counter = 0
            if cv2.waitKey(1) & 0xFF == ord('q'):
                f.close()
                break