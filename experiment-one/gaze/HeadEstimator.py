from time import time

from gaze.Estimator import Estimator
import cv2
import numpy as np

from gaze.FaceUtils import Face
from gaze.pyOpenFace.pyOpenFaceStub import PyOpenFaceStub
from utils.Utils import transformToRad, transformToDeg

debug = False
class HeadEstimator(Estimator):
    P3D_RIGHT_SIDE = np.float32([-100.0, -77.5, -5.0])  # 0
    P3D_GONION_RIGHT = np.float32([-110.0, -77.5, -85.0])  # 4
    P3D_MENTON = np.float32([0.0, 0.0, -122.7])  # 8
    P3D_GONION_LEFT = np.float32([-110.0, 77.5, -85.0])  # 12
    P3D_LEFT_SIDE = np.float32([-100.0, 77.5, -5.0])  # 16
    P3D_FRONTAL_BREADTH_RIGHT = np.float32([-20.0, -56.1, 10.0])  # 17
    P3D_FRONTAL_BREADTH_LEFT = np.float32([-20.0, 56.1, 10.0])  # 26
    P3D_SELLION = np.float32([0.0, 0.0, 0.0])  # 27
    P3D_NOSE = np.float32([21.1, 0.0, -48.0])  # 30
    P3D_SUB_NOSE = np.float32([5.0, 0.0, -52.0])  # 33
    P3D_RIGHT_EYE = np.float32([-20.0, -65.5, -5.0])  # 36
    P3D_RIGHT_TEAR = np.float32([-10.0, -40.5, -5.0])  # 39
    P3D_LEFT_TEAR = np.float32([-10.0, 40.5, -5.0])  # 42
    P3D_LEFT_EYE = np.float32([-20.0, 65.5, -5.0])  # 45
    # P3D_LIP_RIGHT = np.float32([-20.0, 65.5,-5.0]) #48
    # P3D_LIP_LEFT = np.float32([-20.0, 65.5,-5.0]) #54
    P3D_STOMION = np.float32([10.0, 0.0, -75.0])  # 62

    # The points to track
    # These points are the ones used by PnP
    # to estimate the 3D pose of the face
    TRACKED_POINTS = (0, 4, 8, 12, 16, 17, 26, 27, 30, 33, 36, 39, 42, 45, 62)


    def __init__(self, pyOpenFaceStub = None):
        predictor_path = "./models/shape_predictor_68_face_landmarks.dat"
        self.face = Face()
        self.landmarks_3D = np.float32([HeadEstimator.P3D_RIGHT_SIDE,
                                   HeadEstimator.P3D_GONION_RIGHT,
                                   HeadEstimator.P3D_MENTON,
                                   HeadEstimator.P3D_GONION_LEFT,
                                   HeadEstimator.P3D_LEFT_SIDE,
                                   HeadEstimator.P3D_FRONTAL_BREADTH_RIGHT,
                                   HeadEstimator.P3D_FRONTAL_BREADTH_LEFT,
                                   HeadEstimator.P3D_SELLION,
                                   HeadEstimator.P3D_NOSE,
                                   HeadEstimator.P3D_SUB_NOSE,
                                   HeadEstimator.P3D_RIGHT_EYE,
                                   HeadEstimator.P3D_RIGHT_TEAR,
                                   HeadEstimator.P3D_LEFT_TEAR,
                                   HeadEstimator.P3D_LEFT_EYE,
                                   HeadEstimator.P3D_STOMION])
        self.pyOpenFaceStub = pyOpenFaceStub

    def estimate(self, frame, useWorldCoordinates = False, externalDetection = False):
        return self.__getHeadPosePyOpenFace(frame, useWorldCoordinates, externalDetection)
        # return self.__getHeadPosePnP(frame)

    def __getHeadPosePnP(self, frame):
        res = []
        cam_w, cam_h = np.shape(frame)
        c_x = cam_w / 2
        c_y = cam_h / 2
        f_x = c_x / np.tan(60 / 2 * np.pi / 180)
        f_y = f_x
        camera_matrix = np.float32([[f_x, 0.0, c_x],
                                    [0.0, f_y, c_y],
                                    [0.0, 0.0, 1.0]])
        if debug:
            print("Estimated camera matrix: \n" + str(camera_matrix) + "\n")
        camera_distortion = np.float32([0.0, 0.0, 0.0, 0.0, 0.0])
        faces_array = self.face.find_faces(frame)
        if debug:
            print("Total Faces: " + str(len(faces_array)))
        for i, pos in enumerate(faces_array):

            # face_x1 = pos.left()
            # face_y1 = pos.top()
            # face_x2 = pos.right()
            # face_y2 = pos.bottom()
            shape = self.face.find_landmarks(frame, pos)
            landmarks_2D = np.zeros((len(HeadEstimator.TRACKED_POINTS), 2), dtype=np.float32)

            for j, k in enumerate(HeadEstimator.TRACKED_POINTS):
                landmarks_2D[j] = [shape.parts()[k].x, shape.parts()[k].y]


                # Applying the PnP solver to find the 3D pose
                # of the head from the 2D position of the
                # landmarks.
                # retval - bool
                # rvec - Output rotation vector that, together with tvec, brings
                # points from the model coordinate system to the camera coordinate system.
                # tvec - Output translation vector.
            retval, rvec, tvec = cv2.solvePnP(self.landmarks_3D,
                                              landmarks_2D,
                                              camera_matrix, camera_distortion)

            rodrigues = cv2.Rodrigues(rvec)
            # ret, mtxR, mtxQ, qx, qy, qz = cv2.RQDecomp3x3(rodrigues[0])

            eulerAngles = cv2.RQDecomp3x3(rodrigues[0])[0]

            # Now we project the 3D points into the image plane
            # Creating a 3-axis to be used as reference in the image.
            # axis = np.float32([[50, 0, 0],
            #                       [0, 50, 0],
            #                       [0, 0, 50]])
            # imgpts, jac = cv2.projectPoints(axis, rvec, tvec, camera_matrix, camera_distortion)
            res.append(transformToRad(eulerAngles))
        return res[0]

    def __getHeadPosePyOpenFace(self, frame , useWorldCoordinates, externalDetection):
        headPose  = self.pyOpenFaceStub.getHeadPose(frame, useWorldCoordinates, externalDetection)

        return headPose[3:]

if __name__ == '__main__':
    face = cv2.imread('samples/frame1.jpg', 3)
    face = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
    # estimator = HeadEstimator()
    estimator = HeadEstimator(PyOpenFaceStub())
    tic = time()
    face = estimator.estimate(face,True,False)
    print transformToDeg(face)
    print 'Time taken to find head pose: %0.3f s' % (time() - tic)


    cv2.waitKey()

