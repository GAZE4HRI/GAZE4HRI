import cv2
import numpy as np
from keras.backend import set_session
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
import tensorflow as tf

graph = tf.get_default_graph()
sess = tf.Session()
class Emotions():
    def __init__(self):
        global graph
        global sess
        base_path = os.path.realpath(__file__)
        base_path = base_path[:base_path.find('emotions')]
        emotion_model_path = base_path + 'emotions/models/emotion_model.hdf5'
        self.emotion_labels = get_labels('fer2013')
        # hyper-parameters for bounding boxes shape
        self.frame_window = 10
        self.emotion_offsets = (20, 40)
        # loading models
        self.face_cascade = cv2.CascadeClassifier(base_path + 'emotions/models/haarcascade_frontalface_default.xml')
        set_session(sess)
        self.emotion_classifier = load_model(emotion_model_path)
        # getting input model shapes for inference
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]


    def extract_emotion(self, gray_face):
        global graph
        global sess

        try:
            gray_face = cv2.resize(gray_face, (self.emotion_target_size))
        except:
            print "impossible to resize image"

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        with graph.as_default():
            set_session(sess)
            emotion_prediction = self.emotion_classifier.predict(gray_face)
            emotion_probability = np.max(emotion_prediction)
            emotion_label_arg = np.argmax(emotion_prediction)
            emotion_text = self.emotion_labels[emotion_label_arg]
            return (emotion_text, str(emotion_probability))


if __name__ == '__main__':
    emotion = Emotions()
    face = cv2.imread("/home/ja/Dokumenty/Pepper/NewPepperFramework/emotion_service/test.jpg")
    gray_image = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    print emotion.extract_emotion(gray_image)


def extract_emotions(video_source, output_video, output_data):
    base_path = os.path.realpath(__file__)
    base_path = base_path[:base_path.find('emotions')]
    emotion_model_path = base_path + 'emotions/models/emotion_model.hdf5'
    emotion_labels = get_labels('fer2013')
    # hyper-parameters for bounding boxes shape
    frame_window = 10
    emotion_offsets = (20, 40)
    # loading models
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

    f = open(output_data, 'w')
    while cap.isOpened():  # True:
        ret, bgr_image = cap.read()

        if ret == True:

            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

            faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5,
                                                  minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            for face_coordinates in faces:

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
                f.write("{0} {1} \n".format(emotion_text, emotion_probability))
                f.flush()

                draw_bounding_box(face_coordinates, rgb_image, color)
                draw_text(face_coordinates, rgb_image, emotion_mode,
                          color, 0, -45, 1, 1)

            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            out.write(bgr_image)
        else:
            break

    cap.release()
    out.release()
    f.close()
    cv2.destroyAllWindows()


# parameters for loading data and images
