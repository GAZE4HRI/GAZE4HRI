import json

import matplotlib
import zlib
from requests_futures.sessions import FuturesSession

matplotlib.use('Agg')
from Queue import Queue
from collections import deque
from threading import currentThread, Thread

import cv2
import librosa
import numpy as np
import itertools

from keras.engine.saving import load_model
from librosa.display import specshow
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile



base_path = './analyser/questionDetection/trained_models/'
model_path = base_path + "question_model.hdf5"
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


def filter_zeros(t, s, threshold):
    t_indexes = []
    for i, sample in enumerate(t):
        if sum(s[i][:]) > threshold:
            t_indexes.append(i)
    return t_indexes


def isQuestion(t, s, f, window, filter_threshold):
    s = np.reshape(s, (s.shape[1], s.shape[0]))
    t_indexes = filter_zeros(t, s, filter_threshold)
    result = [[t[x], np.average(f, weights=s[x, :])] for x in t_indexes]
    # result = [[t[x], np.mean(s[x,:])] for x in range(0, s.shape[0])]
    time = [result[x][0] for x in range(0, len(result))]
    freq = [result[x][1] for x in range(0, len(result))]
    if len(time) == 0:
        return False
    threshold = max(time) - window
    before = []
    after = []
    for i, x in enumerate(time):
        if x < threshold:
            before.append(freq[i])
        else:
            after.append(freq[i])

    result = np.mean(before) < np.mean(after)
    print "Poczatek: {}".format(np.mean(before))
    print "Koncowka: {}".format(np.mean(after))
    if result:
        print("Pytanie")
    else:
        print("Zdanie twierdzace")
    return result

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class QuestionDetector(object):
    def __init__(self, audioSource, ana):

        self.silence_treshold = 3
        self.audioSource = audioSource
        self.use_service = True
        self.queue = Queue()
        self.worker = None
        self.results = deque(maxlen=50)
        self.micFront = []
        self.analiser = ana
        self.simple = False
        self.sample_rate = 16000
        self.services_address = self.analiser.services_address
        self.silence_counter = 0


    def run_worker(self):
        n = 0
        model = load_model(model_path)
        while True:
            item = self.queue.get()
            if item is None or item == ():
                self.analiser.question_queue.put(None)
                break
            self.results.append(item)

            # self.results.append(item)
            target_size = (221, 223)
            size = len(self.results[0])
            if self.simple and len(self.results) > 30:
                audio = np.array(list(itertools.chain.from_iterable(self.results)))
                # audio = np.frombuffer(data, np.int16)
                # plt.plot(audio[:])
                # plt.show()
                f, t, s = signal.spectrogram(audio, self.sample_rate)
                f = f[:8][:]
                s = s[:8][:]
                if isQuestion(t, s, f, 1, 200):
                    wavfile.write("pyt_" + str(n) + ".wav", self.sample_rate,audio )
                    n+=1
                    self.results = deque(maxlen=50)
                    self.analiser.question_detected = True
                    # plt.pcolormesh(t, f, s)
                    # plt.ylabel('Frequency [Hz]')
                    # plt.xlabel('Time [sec]')
                    # plt.show()
            if not self.use_service and not self.simple and (len(self.results) * size) >= (3 * self.sample_rate):
                audio = np.array(list(itertools.chain.from_iterable(self.results)))
                # audio = np.frombuffer(data, np.int16)
                # plt.plot(audio[:])
                # plt.show()

                float_audio = librosa.util.buf_to_float(audio)
                sig_splits = splitSignal(float_audio, self.sample_rate)

                for i, sig in enumerate(sig_splits):
                    plt.tight_layout(pad=0)
                    plt.margins(0, 0)
                    fig = plt.figure(figsize=[0.72,0.72], dpi=400,  tight_layout={"pad":0,"w_pad":0, "h_pad":0})
                    fig.set_constrained_layout_pads(w_pad=0, h_pad=0)
                    ax = fig.add_subplot(111)
                    ax.axes.get_xaxis().set_visible(False)
                    ax.axes.get_yaxis().set_visible(False)
                    ax.set_frame_on(False)
                    # fig.bbox_inches = 'tight', pad_inches = 0
                    # fig.set_tight_layout({"pad":0})
                    fig.set_dpi(400)

                    S = librosa.feature.melspectrogram(y=sig, sr=self.sample_rate)
                    specshow(librosa.power_to_db(S, ref=np.max))


                    fig.canvas.draw()
                    image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
                    image_from_plot = image_from_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
                    image = image_from_plot[4:-4,4:-4,:]

                    try:
                        image_from_plot = cv2.resize(image, target_size)
                    except:
                        print "impossible to resize image"

                    image_from_plot = preprocess_input(image_from_plot, True)
                    image_from_plot = np.expand_dims(image_from_plot, 0)
                    # image_from_plot = np.expand_dims(image_from_plot, -1)

                    prediction = model.predict(image_from_plot)
                    plt.savefig("spec" + str(n) + "_" + str(i) + ".png")
                    n += 1
                    plt.clf()
                    CLASSES = ['others', 'questions']
                    # get class labels for predictions


                    # sort by confidence and limit results (None returns all results)
                    probability = np.max(prediction)
                    label_arg = np.argmax(prediction)
                    text = CLASSES[label_arg]


                    print text
                    if label_arg == 1:
                        self.analiser.question_detected = True
                for i in range(len(self.results) - 2 * int(self.sample_rate / size)):
                    self.results.popleft()
            if self.use_service and not self.simple and (len(self.results) * size) >= (3 * self.sample_rate):
                session = FuturesSession(max_workers=10)
                audio = np.array(list(itertools.chain.from_iterable(self.results)))

                headers = {'Content-Encoding': 'gzip'}
                json_data = json.dumps({"data": audio, "sample_rate": 16000}, cls=NumpyEncoder)
                request_body = zlib.compress(json_data, 1)

                f = session.post(self.services_address + "/questions", data=request_body, headers=headers,
                                 hooks={'response': self.do_save_response_question_data})
                # print len(self.results) - 2 * int(self.sample_rate / size)
                for i in range(len(self.results) - 2 * int(self.sample_rate / size)):
                    self.results.popleft()

    def do_save_response_question_data(self, response, *args, **kwargs):
        j = response.json()
        if j == None or j == ():
            return
        e = (str(j[0]), float(j[1]))
        self.analiser.question_queue.put(e)


    def run(self):
        t = currentThread()
        self.worker = Thread(target=self.run_worker, args=())
        self.worker.start()

        with self.audioSource as stream:
            while getattr(t, "do_run", True):
                audio_generator = stream.generator()
                for audio in audio_generator:
                    self.micFront = self.convertStr2SignedInt(audio)
                    # compute the rms level on front mic
                    rmsMicFront = self.calcRMSLevel(self.micFront)
                    # print "rms level mic front = " + str(rmsMicFront)
                    if rmsMicFront <= -30:
                        # print "silence"
                        if len(self.micFront) >0:
                            # print len(self.micFront)
                            silence_treshold = float(self.silence_treshold) /(float(len(self.micFront)) / float(self.sample_rate))
                            self.silence_counter += 1
                            if self.silence_counter > silence_treshold:
                                self.analiser.silence_detected = True
                        continue
                    else:
                        self.silence_counter = 0
                        self.queue.put(audio)
                    if getattr(t, "do_run", True) == False:
                        self.audioSource.isProcessingDone = True
            self.queue.put(None)
            self.audioSource.isProcessingDone = True


    def calcRMSLevel(self,data) :
        """
        Calculate RMS level
        """
        rms =   20 * np.log10(np.sqrt( np.sum( np.power(data,2) / len(data)  )))
        return rms

    def convertStr2SignedInt(self, data) :
        """
        This function takes a string containing 16 bits little endian sound
        samples as input and returns a vector containing the 16 bits sound
        samples values converted between -1 and 1.
        """
        signedData=[]
        r = []

        ind=0
        # for i in range (0,len(data)/2) :
        #     signedData.append(data[ind]+data[ind+1]*256)
        #     ind=ind+2

        # d = np.frombuffer(data, np.int16)

        # for i in range (0,len(signedData)) :
        #     if signedData[i]>=32768 :
        #         signedData[i]=signedData[i]-65536

        # for i in range (0,len(data)) :
        #     # signedData[i] = float(signedData[i]) / 32768.0
        #     r.append(float(data[i]) / 32768.0)
        #     # print r[i]
        # # print signedData

        rms_data = np.divide(data, 32768.0)
        return rms_data