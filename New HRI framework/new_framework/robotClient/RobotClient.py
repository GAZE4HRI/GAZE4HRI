
class RobotClient(object):

    def turnOffTablet(self):
        raise NotImplementedError("Should have implemented this")

    def turnOnTablet(self):
        raise NotImplementedError("Should have implemented this")

    def say(self, text):
        raise NotImplementedError("Should have implemented this")

    def setSystemVolume(self, vol):
        raise NotImplementedError("Should have implemented this")

    def sayOnAndroid(self, text):
        raise NotImplementedError("Should have implemented this")

    def playSound(self, path, async, vol):
        raise NotImplementedError("Should have implemented this")

    def playAnimation(self,gestures):
        raise NotImplementedError("Should have implemented this")

    def startAudioRecordPepper(self, name):
        raise NotImplementedError("Should have implemented this")

    def stopAudioRecordPepper(self):
        raise NotImplementedError("Should have implemented this")

    def startVideoRecordPepper(self, path, name):
        raise NotImplementedError("Should have implemented this")

    def stopVideoRecordPepper(self):
        raise NotImplementedError("Should have implemented this")

    def startFaceTracking(self):
        raise NotImplementedError("Should have implemented this")

    def stopFaceTracking(self):
        raise NotImplementedError("Should have implemented this")

    def saveFacePosition(self):
        raise NotImplementedError("Should have implemented this")

    def lookInDir(self, dir):
        raise NotImplementedError("Should have implemented this")

    def cleanUp(self):
        raise NotImplementedError("Should have implemented this")

    def prepare(self):
        raise NotImplementedError("Should have implemented this")

    def startDepthRecording(self, name):
        raise NotImplementedError("Should have implemented this")

    def stopDepthRecording(self):
        raise NotImplementedError("Should have implemented this")