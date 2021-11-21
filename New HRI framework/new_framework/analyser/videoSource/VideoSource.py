
class VideoSource(object):

    def subscribeCamera(self):
        raise NotImplementedError("Should have implemented this")

    def getImage(self):
        raise NotImplementedError("Should have implemented this")

    def releaseImage(self):
        raise NotImplementedError("Should have implemented this")

    def unsubscribe(self):
        raise NotImplementedError("Should have implemented this")



