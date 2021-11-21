#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np
from flask import Flask, jsonify, request
import cv2

import logstash
import logging

host = 'localhost'

logger = logging.getLogger('emotion-service-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 9999, version=1))

from emotions.emotions import Emotions


app = Flask(__name__)


emotions = Emotions()


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/info')
def info():
    return 'this is emotion service try POST /emotions'

@app.route('/emotions', methods=['GET', 'POST'])
def get_emotions():
    if request.method == 'POST':
        face = np.frombuffer(request.data, np.uint8)
        face = cv2.imdecode(face, cv2.IMREAD_GRAYSCALE)
        emotion = emotions.extract_emotion(face)
        logger.info(emotion)
        return jsonify(emotion)
    else:
        face = cv2.imread('/home/ja/Dokumenty/Pepper/NewPepperFramework/emotion_service/test.jpg')
        gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        emotion = emotions.extract_emotion(gray_face)
        return jsonify(emotion)


if __name__ == '__main__':
    app.run(threaded=True)

