import io
from Queue import Queue
from collections import deque
from threading import Thread
import matplotlib.pyplot as plt
import time
from scipy import signal
from scipy.io import wavfile

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
    res = [[t[x], np.average(f, weights=s[x, :])] for x in t_indexes]
    # result = [[t[x], np.mean(s[x,:])] for x in range(0, s.shape[0])]
    time = [res[x][0] for x in range(0, len(res))]
    freq = [res[x][1] for x in range(0, len(res))]
    if len(time) == 0:
        return False
    threshold = max(time) - window
    print len(res)
    before = []
    after = []
    for i, x in enumerate(time):
        if x < threshold:
            before.append(freq[i])
        else:
            after.append(freq[i])
    print len(before)
    result = np.mean(before) < np.mean(after)
    print "Poczatek: {}".format(np.mean(before))
    print "Koncowka: {}".format(np.mean(after))
    if result:
        print("Pytanie")
    else:
        print("Zdanie twierdzace")
    return result





def run_worker():
    global results, queue
    n = 0
    while True:
        item = queue.get()
        if item is None or item == ():
            break
        results.append(np.frombuffer(item, np.int16))
        # self.results.append(item)
        if len(results) > 30:
            audio = np.array(list(itertools.chain.from_iterable(results)))
            # audio = np.frombuffer(data, np.int16)
            # plt.plot(audio[:])
            # plt.show()
            f, t, s = signal.spectrogram(audio, 16000)
            f = f[:8][:]
            s = s[:8][:]
            # print isQuestion(t, s, f, 1, 200)
            if isQuestion(t, s, f, 1, 200):
                # wavfile.write("pyt_" + str(n) + ".wav", 16000, audio)
                # n += 1
                # results = deque(maxlen=50)
                plt.pcolormesh(t, f, s)
                plt.ylabel('Frequency [Hz]')
                plt.xlabel('Time [sec]')
                plt.show()




def calcRMSLevel(data) :
    """
    Calculate RMS level
    """
    rms =   20 * np.log10(np.sqrt( np.sum( np.power(data,2) / len(data)  )))
    return rms


def convertStr2SignedInt( data) :
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
    # print np.max(d)
    # print np.min(d)
    for i in range (0,len(d)) :
        # signedData[i] = float(signedData[i]) / 32768.0
        r.append(float(d[i]) / 32768.0)
        # print r[i]
    # print signedData
    return r

import pyaudio
import wave
import io
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
micFront = []
buff = []
queue = None
worker = None
results = deque(maxlen=50)






if __name__ == "__main__":
    global results, queue, worker, micFront, buff
    queue = Queue()
    worker = Thread(target=run_worker, args=())
    worker.start()
    p = pyaudio.PyAudio()


    wf = wave.open("pyt_3.wav", 'rb')

    data = wf.readframes(CHUNK)
    n = 0
    while data != '':
        micFront = convertStr2SignedInt(data)

        # compute the rms level on front mic
        rmsMicFront = calcRMSLevel(micFront)
        print "rms level mic front = " + str(rmsMicFront)
        print n
        n += 1
        if rmsMicFront <= -37:
            print "silence"

        else:
            queue.put(data)

        data = wf.readframes(CHUNK)
    time.sleep(6)
    queue.put(None)


