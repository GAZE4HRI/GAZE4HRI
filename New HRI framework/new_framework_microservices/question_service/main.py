#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json

import numpy as np
import zlib

import time
from flask import Flask, jsonify, request
import scipy.io.wavfile as wave

import logstash
import logging

from questions.question import Question

host = 'localhost'

logger = logging.getLogger('question-service-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 9999, version=1))



app = Flask(__name__)


questions = Question()


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/info')
def info():
    return 'this is question service try POST /questions'

@app.route('/questions', methods=['GET', 'POST'])
def get_emotions():
    if request.method == 'POST':
        # data = np.frombuffer(request.data, np.int16)
        start = time.time()
        print request.headers
        if request.headers.get("Content-Encoding","") == 'gzip' or request.headers.get("Accept-Encoding","") == 'gzip':
            json_load = json.loads(zlib.decompress(request.data))
        else:
            json_load = json.loads(request.data)
        # logger.info( time.time() - start)
        data = np.asarray(json_load["data"], dtype='int16')
        # print data
        # print len(data)
        # logger.info(time.time() - start)
        sr = json_load.get("sample_rate", 16000)
        is_question = questions.is_question(data, sr)
        logger.info(time.time() - start)

        logger.info(is_question)
        return jsonify(is_question)
    else:
        sr, data = wave.read("test.wav")
        print data
        emotion = questions.is_question(data, sr)
        return jsonify(emotion)


if __name__ == '__main__':
    app.run(threaded=True)

