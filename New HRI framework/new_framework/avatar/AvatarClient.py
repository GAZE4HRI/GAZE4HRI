from robotClient.RobotClient import RobotClient
from utils.Constants import GazeDirection


class AvatarClient(RobotClient):
    def __init__(self, mqtt_helper, unity_topic="unity/", config_topic="config/"):
        self.config_topic = config_topic
        self.mqtt_helper = mqtt_helper
        self.unity_topic = unity_topic


    def turnOffTablet(self):
        pass

    def turnOnTablet(self):
        pass

    def say(self, text):
        self.mqtt_helper.publish(text)

    def setSystemVolume(self, vol):
        pass

    def sayOnAndroid(self, text):
        self.mqtt_helper.publish(text)

    def playSound(self, path, async, vol):
        pass

    def playAnimation(self,gestures):
        pass

    def startAudioRecordPepper(self, name):
        pass

    def stopAudioRecordPepper(self):
        pass

    def startVideoRecordPepper(self, path, name):
        pass

    def stopVideoRecordPepper(self):
        pass

    def startFaceTracking(self):
        self.mqtt_helper.publishOnTopic(self.config_topic, "detect start")
        # self.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)

    def stopFaceTracking(self):
        self.mqtt_helper.publishOnTopic(self.config_topic, "detect stop")

    def saveFacePosition(self):
        pass

    def lookInDir(self, dir):
        if dir == GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value:
            self.mqtt_helper.publishOnTopic(self.unity_topic, "lookStraight")
        if dir == GazeDirection.LOOKING_ON_RIGHT_MIDDLE.value:
            self.mqtt_helper.publishOnTopic(self.unity_topic, "LookRight")
        if dir == GazeDirection.LOOKING_ON_LEFT_MIDDLE.value:
            self.mqtt_helper.publishOnTopic(self.unity_topic, "LookLeft")
        if dir == GazeDirection.LOOKING_ON_MIDDLE_UP.value:
            self.mqtt_helper.publishOnTopic(self.unity_topic, "lookStraightUp")
        if dir == GazeDirection.LOOKING_ON_MIDDLE_DOWN.value:
            self.mqtt_helper.publishOnTopic(self.unity_topic, "lookStraightDown")
        if dir == GazeDirection.LOOKING_ON_RIGHT_UP.value:
            self.mqtt_helper.publishOnTopic(self.unity_topic, "LookRightUp")

    def cleanUp(self):
        pass

    def prepare(self):
        pass

    def startDepthRecording(self, name):
        pass

    def stopDepthRecording(self):
        pass