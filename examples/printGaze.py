import csv

import cv2
import dlib

import numpy as np

GazeFile = 'resources/gaze_id2.txt'
frameSize = (960,1088)
halfFrame = (960,544)
halfFramePepper = (454.5, 483.0)
GazeOfset = (-10.0, 0.0)
face_cascade = dlib.get_frontal_face_detector()

def load_data_set(root):
    data = []
    with open(root, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            data.append(row)

    return data


def transformData(data):
    proportion = [30.0,30.0]
    result =[]
    for r in data:
        result.append((int(((float(r[0] ) + GazeOfset[0])/ proportion[0]) * halfFramePepper[0] ) ,
                       int(((float(r[1]) + GazeOfset[1])/proportion[1]) * halfFramePepper[1])))
    return result


if __name__ == '__main__':
    data = load_data_set(GazeFile)
    tranformedData = transformData(data)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output_id2.avi', fourcc, 9.0, frameSize)
    cap = cv2.VideoCapture('resources/videooutput_id2.mp4')
    img = cv2.imread('resources/workplace.jpg')
    i = 0
    couter = 11
    faces = None
    while (cap.isOpened()):
        ret, frame = cap.read()
        img_copy = np.copy(img)
        if ret == True:
            print tranformedData[i]
            # if couter >10 :
            #     faces = face_cascade(frame)
            #     couter = 0

            # for f in faces:
            faceCenter = (tranformedData[i][0] + int(halfFramePepper[0]),
                          int(halfFramePepper[1]) - tranformedData[i][1])
            # f.center()
            cv2.circle(img_copy, faceCenter, 8, (0, 255, 0), 5)

            resized_image = cv2.resize(frame, halfFrame)
            resized_image_copy = cv2.resize(img_copy, halfFrame)
            vis = np.concatenate((resized_image, resized_image_copy), axis=0)
            i += 1
            # couter += 1

            out.write(vis)

            cv2.imshow('frame', vis)
            if i>= len(tranformedData):
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
