from operator import itemgetter

import matplotlib
from keras.backend import set_session

matplotlib.use('Agg')
import cv2
import librosa
from collections import  Counter
from keras.models import load_model
from librosa.display import specshow
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import os

# base_path = 'trained_models/'
# model_path = base_path + "cleaned_residual_model2.89-0.86.hdf5"
SPEC_LENGTH = 3 #seconds
SPEC_OVERLAP = 2 #seconds


def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x


def splitSignal(sig, rate, seconds=SPEC_LENGTH, overlap=SPEC_OVERLAP):

    #split signal with ovelap
    sig_splits = []
    for i in range(0, len(sig), int((seconds - overlap) * rate)):
        split = sig[i:i + seconds * rate]
        if len(split) >= 1 * rate:
            sig_splits.append(split)
        if len(sig) <= (i + seconds * rate):
            break

    #is signal too short for segmentation?
    if len(sig_splits) == 0:
        sig_splits.append(sig)

    return sig_splits


def most_common(lst):
    data = Counter(lst)
    return max(lst, key=data.get)

def predictionPooling(p):
    # You can test different prediction pooling strategies here
    # We only use average pooling
    if p.ndim == 2:
        p_pool = np.mean(p, axis=0)
    else:
        p_pool = p

    return p_pool

graph = tf.get_default_graph()
sess = tf.Session()


class Question(object):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__( self):
        global graph
        global sess
        """
        Initialise services and variables.
        """
        base_path = os.path.realpath(__file__)
        base_path = base_path[:base_path.find('questions')]
        model_path = base_path + 'questions/model/question_model.hdf5'
        set_session(sess)
        self.sample_rate = 16000
        self.model = load_model(model_path)
        self.target_size = (221, 223)

    def preprocess_input(self, x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x

    def is_question(self, audio, sr, confidence_threshold=0.01, num_results = 5):
        global graph
        global sess
        texts = []
        proba = []
        predictions = []

        float_audio = librosa.util.buf_to_float(audio)
        if not sr == self.sample_rate:
            float_audio = librosa.resample(float_audio, sr, 16000)
        sig_splits = splitSignal(float_audio, self.sample_rate)
        # librosa.output.write_wav('/home/ja/Dokumenty/Pepper/NewPepperFramework/new_framework_microservices/question_service/file1.wav', float_audio, sr)

        for i, sig in enumerate(sig_splits):
            plt.tight_layout(pad=0)
            plt.margins(0, 0)
            fig = plt.figure(figsize=[0.72, 0.72], dpi=400, tight_layout={"pad": 0, "w_pad": 0, "h_pad": 0})
            fig.set_constrained_layout_pads(w_pad=0, h_pad=0)
            ax = fig.add_subplot(111)
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)
            ax.set_frame_on(False)
            # fig.bbox_inches = 'tight', pad_inches = 0
            # fig.set_tight_layout({"pad":0})
            fig.set_dpi(400)

            S = librosa.feature.melspectrogram(y=sig, sr=sr)
            specshow(librosa.power_to_db(S, ref=np.max))

            fig.canvas.draw()
            image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            image_from_plot = image_from_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            image = image_from_plot[4:-4, 4:-4, :]

            try:
                image_from_plot = cv2.resize(image, (221, 223))
            except:
                print
                "impossible to resize image"

            # make prediction
            spec = preprocess_input(image_from_plot)
            # target_size = model.input_shape[1:3]
            # spec = cv2.resize(spec, (target_size))
            spec = np.expand_dims(spec, 0)
            # spec = np.expand_dims(spec, -1)
            with graph.as_default():
                set_session(sess)
                p = self.model.predict(spec)
                plt.clf()
            print(p)

            # stack predictions
            if len(predictions):
                predictions = np.vstack([predictions, p])
            else:
                predictions = p

                # prediction pooling
        p_pool = predictionPooling(predictions)
        CLASSES = ['others', 'questions']
        # get class labels for predictions
        p_labels = {}
        for i in range(p_pool.shape[0]):
            if p_pool[i] >= confidence_threshold:
                p_labels[CLASSES[i]] = p_pool[i]

        # sort by confidence and limit results (None returns all results)
        p_sorted = sorted(p_labels.items(), key=itemgetter(1), reverse=True)[:num_results]


        # text = most_common(texts)
        # ind = [i for i, j in enumerate(texts) if j == text]
        # probability = np.mean([proba[k] for k in ind])
        print p_sorted
        return (p_sorted[0][0], str(p_sorted[0][1]))
