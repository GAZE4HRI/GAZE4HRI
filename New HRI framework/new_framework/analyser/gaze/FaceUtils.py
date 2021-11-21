from time import time

import dlib
import cv2
import numpy as np
import os
from scipy.spatial import distance as dist


eye_part_ratios = [0.05, 0.3, 0.3, 0.3, 0.05]
EYE_AR_THRESH = 0.14
class Face:
    def __init__(self):
        base_path = os.path.realpath(__file__)
        base_path = base_path[:base_path.find('gaze')]
        predictor_path = "gaze/models/shape_predictor_68_face_landmarks.dat"
        path_face_cass = 'gaze/models/haarcascade_frontalface_default.xml'
        path_eye_pair_cass = 'gaze/models/haarcascade_mcs_eyepair_big.xml'
        path_left_eye = 'gaze/models/haarcascade_mcs_lefteye.xml'
        path_right_eye = 'gaze/models/haarcascade_mcs_righteye.xml'

        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(base_path + predictor_path)
        self.face_cascade = cv2.CascadeClassifier(base_path + path_face_cass)
        self.l_eye_cass = cv2.CascadeClassifier(base_path + path_left_eye)
        self.r_eye_cass = cv2.CascadeClassifier(base_path + path_right_eye)

        self.angles_to_try = [0, 15, -15, 30, -30]
        self.classifier_pair = cv2.CascadeClassifier(base_path + path_eye_pair_cass)
        self.l_eye_land = range(36,42)
        self.r_eye_land = range(42,48)


    def find_faces(self, frame):
        return self.detector(frame)


    def find_landmarks(self,frame, face):
        return self.predictor(frame, face)
    def find_faces_openCV(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        res = []
        for (x,y,w,h) in faces:
            res.append(dlib.rectangle((long)(x), (long)(y), (long)(x+w), (long)(y+h)))
        return res


    def get_eye_rois(self , frame):
        for angle in self.angles_to_try:
            res = self.get_eye_rois_at_angle(frame, angle)
            if res is not None:
                return res

    def get_eye_rois_at_angle(self, frame, angle):


        pyr_img = frame.copy()


        # Rotate down-scaled frame for potential non-horizontal eye-pairs
        if angle != 0:
            rot_center = (pyr_img.shape[1] / 2, pyr_img.shape[0] / 2)
            rot_mat_fwd = cv2.getRotationMatrix2D(rot_center, angle, 1)
            pyr_img = cv2.warpAffine(pyr_img, rot_mat_fwd, (pyr_img.shape[1], pyr_img.shape[0]))

        min_eye_pair_size = (10, 10)


        pyr_img_grey = cv2.cvtColor(pyr_img, cv2.COLOR_BGR2GRAY)

        eye_pair_rects = self.classifier_pair.detectMultiScale(pyr_img_grey,
                                                          scaleFactor=1.1,
                                                          minSize=min_eye_pair_size)

        if eye_pair_rects is ():
            return self.get_eye_rois_default(frame)
        if len(eye_pair_rects) == 1:
            best_eye_pair_rect = eye_pair_rects[0]
        else:
            best_eye_pair_rect = self.choose_best_eye_pair(eye_pair_rects, pyr_img)

        roi_x0, roi_y0, roi_w, roi_h = best_eye_pair_rect

        # Get origin and sizes of eye-pairs found in image (possibly rotated)
        eye_1_x0 = int(roi_x0 + roi_w * eye_part_ratios[0])
        eye_1_w = int(roi_w * eye_part_ratios[1])
        eye_2_x0 = int(roi_x0 + roi_w * sum(eye_part_ratios[:3]))
        eye_2_w = int(roi_w * eye_part_ratios[3])

        if angle == 0:
            eye_1_img = frame[roi_y0:(roi_y0 + roi_h), eye_1_x0:eye_1_x0 + eye_1_w]
            eye_2_img = frame[roi_y0:(roi_y0 + roi_h), eye_2_x0:eye_2_x0 + eye_2_w]
            eye_roi_1, eye_roi_2 = ((eye_1_x0, roi_y0), eye_1_img), ((eye_2_x0, roi_y0), eye_2_img)

        else:

            # Find currently rotated middles of eye ROIs
            eye_1_mid_rot = [[eye_1_x0 + eye_1_w / 2], [roi_y0 + roi_h / 2]]
            eye_2_mid_rot = [[eye_2_x0 + eye_2_w / 2], [roi_y0 + roi_h / 2]]

            # Un-rotate them to match original frame
            rot_mat_inv = cv2.getRotationMatrix2D(rot_center, -angle, 1)
            eye_1_mid_x, eye_1_mid_y = np.ravel(np.dot(rot_mat_inv, eye_1_mid_rot))
            eye_2_mid_x, eye_2_mid_y = np.ravel(np.dot(rot_mat_inv, eye_2_mid_rot))

            # Get ROIs of un-rotated full-frame
            eye_1_x0, eye_1_y0 = eye_1_mid_x - eye_1_w / 2, eye_1_mid_y - roi_h / 2
            eye_2_x0, eye_2_y0 = eye_2_mid_x - eye_2_w / 2, eye_2_mid_y - roi_h / 2
            eye_1_img = frame[eye_1_y0:(eye_1_y0 + roi_h), eye_1_x0:eye_1_x0 + eye_1_w]
            eye_2_img = frame[eye_2_y0:(eye_2_y0 + roi_h), eye_2_x0:eye_2_x0 + eye_2_w]

            eye_roi_1, eye_roi_2 = ((eye_1_x0, eye_1_y0), eye_1_img), ((eye_2_x0, eye_2_y0), eye_2_img)

        return eye_roi_1, eye_roi_2

    # Default behaviour if fail to get eyepair
    def get_eye_rois_default(self , frame):

        """ Returns a pair of EyeRois - one for each eye in an eye pair
        """

        pyr_img = frame.copy()

        pyr_img_grey = cv2.cvtColor(pyr_img, cv2.COLOR_BGR2GRAY)

        _, img_w = pyr_img_grey.shape[:2]
        roi_r, roi_l = pyr_img_grey.copy(), pyr_img_grey.copy()
        roi_r[:, 0:img_w / 2] = 0
        roi_l[:, img_w / 2:img_w] = 0
        min_eye_size = (pyr_img.shape[0] / 6, pyr_img.shape[0] / 9)

        eye_l_rects = self.l_eye_cass.detectMultiScale(roi_l, scaleFactor=1.1, minSize=min_eye_size)
        eye_r_rects = self.r_eye_cass.detectMultiScale(roi_r, scaleFactor=1.1, minSize=min_eye_size)

        if len(eye_l_rects) == 0 or len(eye_r_rects) == 0:
            print ('Did not find eyes with default behaviour')
            return None
        if len(eye_l_rects) == 1:
            best_eye_l_rect = eye_l_rects[0]
        else:
            best_eye_l_rect = self.choose_best_eye_pair(eye_l_rects, pyr_img)
        roi_l_x0, roi_l_y0, roi_l_w, roi_l_h = best_eye_l_rect


        if len(eye_r_rects) == 1:
            best_eye_r_rect = eye_r_rects[0]
        else:
            best_eye_r_rect = self.choose_best_eye_pair(eye_r_rects, pyr_img)
        roi_r_x0, roi_r_y0, roi_r_w, roi_r_h = best_eye_r_rect


        eye_1_img = frame[roi_l_y0:(roi_l_y0 + roi_l_h), roi_l_x0:roi_l_x0 + roi_l_w]
        eye_2_img = frame[roi_r_y0:(roi_r_y0 + roi_r_h), roi_r_x0:roi_r_x0 + roi_r_w]
        eye_roi_1, eye_roi_2 = ((roi_l_x0, roi_l_y0), eye_1_img), ((roi_r_x0, roi_r_y0), eye_2_img)


        return eye_roi_1, eye_roi_2



    def get_eye_rois_by_landmarks(self, frame, shape):

        l_land, r_land = self.get_eye_landmarks(shape)

        x_1 = min(l_land.items(), key=lambda (k, v): v[0])[1][0]
        y_1 = min(l_land.items(), key=lambda (k, v): v[1])[1][1]
        x_2 = max(l_land.items(), key=lambda (k, v): v[0])[1][0]
        y_2 = max(l_land.items(), key=lambda (k, v): v[1])[1][1]
        dist = ((x_2 - x_1 ) - (y_2 - y_1) + 20) / 2
        y_1 = y_1 - dist
        y_2 = y_2 + dist
        x_1 = x_1 - 10
        x_2 = x_2 + 10
        eye_1_img = frame[y_1:y_2, x_1:x_2]

        r_x_1 = min(r_land.items(), key=lambda (k, v): v[0])[1][0]
        r_y_1 = min(r_land.items(), key=lambda (k, v): v[1])[1][1]
        r_x_2 = max(r_land.items(), key=lambda (k, v): v[0])[1][0]
        r_y_2 = max(r_land.items(), key=lambda (k, v): v[1])[1][1]
        dist = ((r_x_2 - r_x_1 ) - (r_y_2 - r_y_1) + 20) / 2
        r_y_1 = r_y_1 - dist
        r_y_2 = r_y_2 + dist
        r_x_1 = r_x_1 - 10
        r_x_2 = r_x_2 + 10
        eye_2_img = frame[r_y_1:r_y_2, r_x_1:r_x_2]

        return ((x_1, y_1), eye_1_img), ((r_x_1, r_y_1), eye_2_img)

    def get_eye_landmarks(self, shape):
        l_land = {}
        for l in self.l_eye_land:
            l_land[l] = (shape.parts()[l].x, shape.parts()[l].y)
        r_land = {}
        for r in self.r_eye_land:
            r_land[r] = (shape.parts()[r].x, shape.parts()[r].y)
        return l_land, r_land

    def eye_aspect_ratio(self, eye):
        # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear


    def get_Blinks(self, land):
        eye_land_l, eye_land_r = face.get_eye_landmarks(land)
        leftEAR = face.eye_aspect_ratio(eye_land_l.values())
        rightEAR = face.eye_aspect_ratio(eye_land_r.values())
        ear = (leftEAR + rightEAR) / 2.0
        if leftEAR < EYE_AR_THRESH < rightEAR:
            return "Left Eye Blinked"
        elif leftEAR > EYE_AR_THRESH > rightEAR:
            return "Right Eye Blinked"
        if leftEAR < EYE_AR_THRESH and rightEAR < EYE_AR_THRESH:
            return "Both Eyes Blinked"


if __name__ == '__main__':
    head = cv2.imread('./samples/sample4.jpg', 3)
    face = Face()
    tic = time()
    faces = face.find_faces(head)
    for f in faces:
        face_roi = head[f.top() :f.bottom(),f.left():f.right()]
        land = face.find_landmarks(head,f)
        print face.get_Blinks(land)
        eye_roi_1, eye_roi_2 = face.get_eye_rois_by_landmarks(head,land)
    print 'Time taken to find head pose: %0.3f s' % (time() - tic)

    cv2.waitKey()