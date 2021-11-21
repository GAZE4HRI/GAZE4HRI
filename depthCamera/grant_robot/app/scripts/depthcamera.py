"""
A sample showing how to have a NAOqi service as a Python app.
"""
from threading import currentThread, Thread

import time

__version__ = "0.0.3"



import qi

import stk.runner
import stk.events
import stk.services
import stk.logging
import vision_definitions
import numpy
import cv2

class Depthcamera(object):
    "NAOqi service example (set/get on a simple value)."

    APP_ID = "com.aldebaran.Depthcamera"
    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        # Internal variables
        self.level = 0
        self.resolution = vision_definitions.kQVGA
        self.colorSpace = vision_definitions.kDepthColorSpace
        self.fps = 10
        self.camera = self.s.ALVideoDevice
        self.nameId = None
        self.thread = None


    def getImage(self):
        image = self.camera.getImageRemote(self.nameId)
        image_width = image[0]
        image_height = image[1]

        return numpy.frombuffer(image[6], numpy.uint8).reshape(image_height, image_width, 1)

    def releaseImage(self):
        self.camera.releaseImage(self.nameId)

    def unsubscribe(self):
        self.camera.unsubscribe(self.nameId)

    def subscribeCamera(self):
            # subscribe or subscribeCamera?? - subscribe is deprecated
        self.nameId = self.camera.subscribeCamera("DepthCamera", 2, self.resolution, self.colorSpace, self.fps)

    @qi.bind(returnType=qi.Void, paramsType=[qi.String, qi.Int8])
    def record(self, name, t):
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter("/home/nao/" + name, fourcc, self.fps, (320, 240), 0)
        self.subscribeCamera()
        for i in range(int(t) * self.fps):
            img = self.getImage()
            self.releaseImage()
            out.write(img)
            time.sleep(1.0 / float(self.fps))
        self.unsubscribe()
        out.release()

    def run(self, name):
        """
        Loop on, wait for events until manual interruption.
        """

        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter("/home/nao/" + name, fourcc, self.fps, (320, 240), 0)
        self.subscribeCamera()
        t = currentThread()

        while getattr(t, "do_run", True):
            img = self.getImage()
            self.releaseImage()
            out.write(img)
            time.sleep(1.0 / float(self.fps + 2))

        self.unsubscribe()
        out.release()

    @qi.bind(returnType=qi.Void, paramsType=[qi.String])
    def start_recording(self, name):
        self.thread = Thread(target=self.run,
                        args=(name,))
        self.thread.start()

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop_recording(self):
        self.thread.do_run = False
        self.thread.join()

    @qi.bind(returnType=qi.Void, paramsType=[qi.Int8])
    def set(self, level):
        "Set level"
        self.level = level

    @qi.bind(returnType=qi.Int8, paramsType=[])
    def get(self):
        "Get level"
        return self.level

    @qi.bind(returnType=qi.Void, paramsType=[])
    def reset(self):
        "Reset level to default value"
        return self.set(0)

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        "Stop the service."
        self.logger.info("Depthcamera stopped by user request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        "Cleanup (add yours if needed)"
        self.logger.info("Depthcamera finished.")

####################
# Setup and Run
####################

if __name__ == "__main__":
    stk.runner.run_service(Depthcamera)

