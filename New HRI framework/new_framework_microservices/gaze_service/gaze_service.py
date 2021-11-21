import math

import numpy as np
from flask import Flask, jsonify, request
import cv2
import py_eureka_client.eureka_client as eureka_client

from gaze.FaceUtils import Face
from gaze.GazeEstimator import GazeEstimator
from gaze.pyOpenFace.pyOpenFaceStub import PyOpenFaceStub

app = Flask(__name__)
p = PyOpenFaceStub()
estimator = GazeEstimator(p)

import logstash
import logging

host = 'localhost'

logger = logging.getLogger('gaze-service-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler(host, 9999, version=1))

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/info')
def info():
    return 'this is gaze service try POST /gaze'

# faces = Face()
@app.route('/gaze', methods=['GET', 'POST'])
def gaze():
    if request.method == 'POST':
        face = np.frombuffer(request.data, np.uint8)
        face = cv2.imdecode(face, cv2.IMREAD_GRAYSCALE)
        yaw, pitch = transformToDeg(estimator.estimate(face))
        logger.info(((yaw, pitch)))
        return jsonify((yaw, pitch))
    else:
        face = cv2.imread('/home/ja/Dokumenty/Pepper/gaze_service/test.jpg', 3)
        face = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
        yaw, pitch = transformToDeg(estimator.estimate(face))
        return jsonify((yaw, pitch))

@app.route('/reset')
def reset():
    p.reset()
    return 'done'

@app.route('/gaze_single', methods=['POST'])
def gaze_single():
    face = np.frombuffer(request.data, np.uint8)
    face = cv2.imdecode(face, cv2.IMREAD_GRAYSCALE)
    height, width = face.shape
    p.getLandmarksInImage(face, [0, 0, width, height])
    yaw, pitch = transformToDeg(estimator.estimate(face, True))
    logger.info(((yaw, pitch)))
    return jsonify((yaw, pitch))

def transformToDeg(direction):
    res = []
    for rad in direction:
        res.append(math.degrees(rad))
    return tuple(res)

if __name__ == '__main__':
    your_rest_server_port = 6000
    # The flowing code will register your server to eureka server and also start to send heartbeat every 30 seconds
    # eureka_client.init(eureka_server="http://127.0.0.1:8761/eureka",
    #                    app_name="my-gaze-service",
    #                    instance_port=your_rest_server_port)
    app.run()
