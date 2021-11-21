import json

import librosa
import scipy.io.wavfile as wave

import cv2
import requests
import time
import numpy as np
import difflib

import zlib


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def ser():
    # print wave.read("test.wav")
    y,s = librosa.load("test.wav", 44100)
    z = librosa.resample(y,s,16000)
    data = np.round(z * 32767).astype('int16')
    json_data = json.dumps(data, cls=NumpyEncoder)
    import pandas as pd
    # print data
    pd_data = pd.Series(data).to_json(orient='values')
    print json_data[:1000]
    print pd_data[:1000]
    for i, s in enumerate(difflib.ndiff(json_data[:1000], pd_data[:1000])):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            print(u'Delete "{}" from position {}'.format(s[-1], i))
        elif s[0] == '+':
            print(u'Add "{}" to position {}'.format(s[-1], i))
            # print data

def send():

    #
    # files = {'file': ('test.jpg',open('test.jpg', 'rb'))}
    # files2 = {'file': ('test.jpg',face.tobytes())}
    # sr, data = wave.read("test.wav")

    y, s = librosa.load("other.wav", 44100)
    z = librosa.resample(y, s, 16000)

    data = np.round(z * 32767).astype('int16')
    float_audio = librosa.util.buf_to_float(data)
    librosa.output.write_wav(
        '/home/ja/Dokumenty/Pepper/NewPepperFramework/new_framework_microservices/question_service/file2.wav',
        float_audio, 16000)

    # data = open('test.jpg','rb').read()

    # import pandas as pd
    # # print data
    # pd_data = pd.Series({"data": data, "sample_rate": 16000}).to_json(orient='values')
    # # print json_data
    # print json_data==pd_data
    content_type = 'image/jpeg'
    headers = {'Content-Encoding': 'gzip'}
    json_data = json.dumps({"data": data, "sample_rate": 16000}, cls=NumpyEncoder)
    request_body = zlib.compress(json_data,1)

    start = time.time()
    r = requests.post("http://127.0.0.1:5000/questions",data=request_body, headers=headers)
    print r.text
    print time.time() - start

    print len(json_data)
    # print len(request_body)
    print type(json_data)
    # print type(request_body)




if __name__ == "__main__":
    send()