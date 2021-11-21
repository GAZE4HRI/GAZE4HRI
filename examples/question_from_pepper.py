import io
from Queue import Queue
from collections import deque
from threading import Thread

import qi
import argparse
import sys
import time
from scipy import signal
from scipy.io import wavfile
import sys
import matplotlib.pyplot as plt
import numpy as np
import itertools

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

class SoundProcessingModule(object):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__( self, app):
        """
        Initialise services and variables.
        """
        super(SoundProcessingModule, self).__init__()
        app.start()
        app.session.registerService("SoundProcessingModule", self)
        session = app.session

        # Get the service ALAudioDevice.
        self.audio_service = session.service("ALAudioDevice")
        self.isProcessingDone = False
        self.nbOfFramesToProcess = 200
        self.framesCount=0
        self.micFront = []
        self.buff = []
        self.module_name = "SoundProcessingModule"
        self.file = io.open("rec", 'wb')
        self.queue = None
        self.worker = None
        self.results = deque(maxlen=50)

    def run_worker(self):
        n = 0
        while True:
            item = self.queue.get()
            if item is None or item == ():
                break
            self.results.append(np.frombuffer(item,np.int16))
            # self.results.append(item)
            if len(self.results) > 30:
                audio = np.array(list(itertools.chain.from_iterable(self.results)))
                # audio = np.frombuffer(data, np.int16)
                # plt.plot(audio[:])
                # plt.show()
                f, t, s = signal.spectrogram(audio, 16000)
                f = f[:8][:]
                s = s[:8][:]
                if isQuestion(t, s, f, 1, 200):
                    wavfile.write("pyt_" + str(n) + ".wav", 16000,audio )
                    n+=1
                    self.results = deque(maxlen=50)
                    # plt.pcolormesh(t, f, s)
                    # plt.ylabel('Frequency [Hz]')
                    # plt.xlabel('Time [sec]')
                    # plt.show()

    def startProcessing(self):
        """
        Start processing
        """
        # ask for the front microphone signal sampled at 16kHz
        # if you want the 4 channels call setClientPreferences(self.module_name, 48000, 0, 0)
        self.audio_service.setClientPreferences(self.module_name, 16000, 3, 0)
        self.audio_service.subscribe(self.module_name)
        self.queue = Queue()
        self.worker = Thread(target=self.run_worker, args=())
        self.worker.start()

        while self.isProcessingDone == False:
            time.sleep(1)

        self.audio_service.unsubscribe(self.module_name)

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """
        Compute RMS from mic.
        """
        self.framesCount = self.framesCount + 1

        # print "nchanels {} nsamplech {} buf size {} time {}".format(str(nbOfChannels),str(nbOfSamplesByChannel),str(len(inputBuffer)),str(time.time()))

        if (self.framesCount <= self.nbOfFramesToProcess):
            # convert inputBuffer to signed integer as it is interpreted as a string by python
            self.buff = inputBuffer

            # print inputBuffer
            # self.file.write(inputBuffer)
            self.micFront=self.convertStr2SignedInt(inputBuffer)

            #compute the rms level on front mic
            rmsMicFront = self.calcRMSLevel(self.micFront)
            # print "rms level mic front = " + str(rmsMicFront)
            if rmsMicFront <= -37:
                print "silence"
            else:
                self.queue.put(inputBuffer)



        else :
            self.queue.put(None)
            self.isProcessingDone=True

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

        d = np.frombuffer(data, np.int16)

        # for i in range (0,len(signedData)) :
        #     if signedData[i]>=32768 :
        #         signedData[i]=signedData[i]-65536

        for i in range (0,len(d)) :
            # signedData[i] = float(signedData[i]) / 32768.0
            r.append(float(d[i]) / 32768.0)
            # print r[i]
        # print signedData
        return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.100",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["SoundProcessingModule", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    MySoundProcessingModule = SoundProcessingModule(app)
    # app.session.registerService("SoundProcessingModule", MySoundProcessingModule)
    MySoundProcessingModule.startProcessing()
