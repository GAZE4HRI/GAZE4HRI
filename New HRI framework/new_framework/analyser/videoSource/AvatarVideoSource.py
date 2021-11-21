from Queue import Queue, Empty

import cv2

from analyser.videoSource.VideoSource import VideoSource
import numpy as np

class AvatarVideoSource(VideoSource):

    def __init__(self):
        self.nr = 1
        self.frame = None
        self.queue = Queue()

    def put_image(self, item):
        image_as_np = np.fromstring(item, np.uint8)
        image = cv2.imdecode(image_as_np, cv2.IMREAD_COLOR)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # cv2.imwrite("frame" + str(self.nr) + ".png", image)
        # self.nr += 1

        self.queue.put(image)

    def subscribeCamera(self):
        pass

    def getImage(self):
        try:
            item = self.queue.get_nowait()
            self.frame = item
        except Empty:
            pass
        return self.frame


    def releaseImage(self):
        self.queue.task_done()

    def unsubscribe(self):
        pass