import cv2
import numpy as np
from keras.models import load_model
from statistics import mode
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input
import os
import dlib
import cvlib as cv


USE_WEBCAM = False # If false, loads video file source


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and  grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the original image
    if  width is None and height is None:
        return image

    # check to see if the width is None
    if  width is None:
        # calculate the ratio of the height and construct the dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def largest_indices(ary, n):
    """Returns the n largest indices from a numpy array."""
    flat = ary.flatten()
    indices = np.argpartition(flat, -n)[-n:]
    indices = indices[np.argsort(-flat[indices])]
    return np.unravel_index(indices, ary.shape)

def extract_emotions(video_source, output_video, output_data, n):
    base_path = os.path.realpath(__file__)
    # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    # os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    base_path = base_path[:base_path.find('emotions')]
    emotion_model_path = base_path + 'emotions/models/emotion_model.hdf5'
    emotion_labels = get_labels('fer2013')



    # hyper-parameters for bounding boxes shape
    frame_window = 10
    emotion_offsets = (20, 40)
    # loading models
    cnn_face_detector = dlib.cnn_face_detection_model_v1(base_path + 'emotions/models/mmod_human_face_detector.dat')
    face_cascade = cv2.CascadeClassifier(base_path + 'emotions/models/haarcascade_frontalface_default.xml')
    emotion_classifier = load_model(emotion_model_path)
    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]
    # starting lists for calculating modes
    emotion_window = []
    # starting video streaming

    video_capture = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_video, fourcc, 9.0, (1920, 1088))
    # Select video or webcam feed
    cap = cv2.VideoCapture(video_source)
    count = 0.
    miss = 0.
    f = open(output_data, 'w')
    while cap.isOpened():  # True:
        ret, bgr_image = cap.read()

        if ret == True:

            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

            # faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5,
            #                                       minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            # gray_image = cv2.resize(gray_image,(1280,720))
            # print gray_image.shape
            faces = cnn_face_detector(gray_image, 1)
            # faces, confidences = cv.detect_face(gray_image)
            count += 1.
            if len(faces) == 0:
                miss += 1.
            for face_coordinates in faces:
                x = face_coordinates.rect.left()
                y = face_coordinates.rect.top()
                w = face_coordinates.rect.right() - x
                h = face_coordinates.rect.bottom() - y
                # x = face_coordinates[0]
                # y = face_coordinates[1]
                # w = face_coordinates[2] - x
                # h = face_coordinates[3] - y
                face_coordinates = (x, y, w, h)
                x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
                gray_face = gray_image[y1:y2, x1:x2]
                try:
                    gray_face = cv2.resize(gray_face, (emotion_target_size))
                except:
                    continue

                gray_face = preprocess_input(gray_face, True)
                gray_face = np.expand_dims(gray_face, 0)
                gray_face = np.expand_dims(gray_face, -1)
                emotion_prediction = emotion_classifier.predict(gray_face)
                emotion_probability = np.max(emotion_prediction)
                emotion_label_arg = np.argmax(emotion_prediction)
                emotion_text = emotion_labels[emotion_label_arg]
                emotion_window.append(emotion_text)

                emotion_label_args = largest_indices(emotion_prediction, n)
                emotion_probabilitis = emotion_prediction[emotion_label_args]
                emotion_texts = [emotion_labels.get(key) for key in emotion_label_args[1]]
                if len(emotion_window) > frame_window:
                    emotion_window.pop(0)
                try:
                    emotion_mode = mode(emotion_window)
                except:
                    continue

                if emotion_text == 'angry':
                    color = emotion_probability * np.asarray((255, 0, 0))
                elif emotion_text == 'sad':
                    color = emotion_probability * np.asarray((0, 0, 255))
                elif emotion_text == 'happy':
                    color = emotion_probability * np.asarray((255, 255, 0))
                elif emotion_text == 'surprise':
                    color = emotion_probability * np.asarray((0, 255, 255))
                else:
                    color = emotion_probability * np.asarray((0, 255, 0))

                color = color.astype(int)
                color = color.tolist()
                emotion_text = " ".join(emotion_texts)
                f.write("{0} {1} \n".format(emotion_text, " ".join(str(item) for item in emotion_probabilitis)))
                f.flush()

                draw_bounding_box(face_coordinates, rgb_image, color)
                draw_text(face_coordinates, rgb_image, emotion_mode,
                          color, 0, -45, 1, 1)

            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            out.write(bgr_image)
        else:
            break
    print miss
    print count
    print miss/count
    cap.release()
    out.release()
    f.close()
    cv2.destroyAllWindows()


# parameters for loading data and images
