import random
import time
from threading import currentThread


from threading import Thread


from pepper.Motion import Motion
from pepper.Speech import Speech
from robotClient.RobotClient import RobotClient
from utils.Constants import GazeDirection
import numpy as np



class PepperClient(RobotClient):
    def __init__(self, session, gesturesEnabled, mqttHelper, humanTracking):


        self.speech = Speech(session)
        self.motion = Motion(session)


        # self.configuration = {"bodyLanguageMode":"contextual"}

        self.ba_service = session.service("ALBasicAwareness")
        self.posture = session.service("ALRobotPosture")
        self.record = session.service("ALAudioRecorder")
        self.audioPlayerService = session.service("ALAudioPlayer")
        self.animationPlayerService = session.service("ALAnimationPlayer")
        self.audioDeviceService = session.service("ALAudioDevice")
        self.tabletService = session.service("ALTabletService")
        self.videoService = session.service("ALVideoRecorder")
        self.depthRec = session.service("Depthcamera")
        self.tracker_service = session.service("ALTracker")
        self.targetName = "Face"
        self.faceWidth = 0.05
        self.facePosition = None
        self.headAngles = [0.0, -10.0]



        self.mqttHelper = mqttHelper
        self.gesturesEnabled = gesturesEnabled
        self.humanTracking = humanTracking
        self.isNoiceRuning = False

        self.leds_service = session.service("ALLeds")



        self.thread = None

    def turnOffTablet(self):
        self.tabletService.goToSleep()

    def turnOnTablet(self):
        self.tabletService.wakeUp()

    def say(self, text):
        self.speech.say(text)

    def setSystemVolume(self, vol):
        self.audioDeviceService.setOutputVolume(vol)

    def sayOnAndroid(self, text):
        self.mqttHelper.publish(text)


    def playSound(self, path, async, vol):
        print path
        balance = 0.0
        val = self.audioDeviceService.getOutputVolume()
        self.setSystemVolume(95)
        fileId = self.audioPlayerService.loadFile(path)
        return self.audioPlayerService.play(fileId, vol, balance, _async=async), val


    def playAnimation(self,gestures):
        if self.gesturesEnabled == True:
            for gesture in gestures:
                future = self.animationPlayerService.run(gesture[0],_async=True)
                # wait the end of the animation
                future.value()
                time.sleep(gesture[1])




    def makeRecordPepper(self, name):

        self.record.startMicrophonesRecording(name, "wav", 48000, (1,1,1,1))
        time.sleep(time)
        self.record.stopMicrophonesRecording()

    def startAudioRecordPepper(self, name):
        self.record.startMicrophonesRecording(name, "wav", 48000, (1,1,1,1))

    def stopAudioRecordPepper(self):
        self.record.stopMicrophonesRecording()


    def startVideoRecordPepper(self, path, name):
        self.videoService.setResolution(2)
        self.videoService.startRecording(path, name, True)

    def stopVideoRecordPepper(self):
        self.videoService.stopRecording()

    def stopBasicAwareness(self):
        if self.ba_service.isEnabled():
            self.ba_service.setEnabled(False)
            time.sleep(0.3)
        if not self.isNoiceRuning:
            self.startHeadNoise()

    def startBasicAwareness(self):
        if not self.ba_service.isEnabled():
            self.motion.moveHead([0.0, -10.0])
            time.sleep(0.3)
            self.ba_service.setEnabled(True)
            self.ba_service.setTrackingMode("Head")
            self.ba_service.setEngagementMode("FullyEngaged")
            # self.ba_service.setEngagementMode("SemiEngaged")
            self.ba_service.setStimulusDetectionEnabled("People",True)
            time.sleep(0.3)
        if self.isNoiceRuning:
            self.stopHeadNoise()


    def startFaceTracking(self):
        if not self.tracker_service.isActive():

            self.tracker_service.track(self.targetName)
        if self.isNoiceRuning:
            self.stopHeadNoise()


    def stopFaceTracking(self):
        if self.tracker_service.isActive():
            self.tracker_service.stopTracker()


    def saveFacePosition(self):
        self.facePosition = self.tracker_service.getTargetPosition(0)
        self.headAngles = self.motion.getHeadPosition()


    def lookAtFace(self):
        try:
            self.tracker_service.lookAt(self.facePosition,0,0.1,False)
        except:
            self.facePosition = None
            self.motion.moveHead([0.0, -10.0])

    def lookInDir(self, dir):
        name = 'FaceLeds'
        self.leds_service.fade(name, 0.4, 0.3)
        if dir == GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value:
            n = 'FaceLeds'
            # if self.ba_service.isEnabled():
            self.leds_service.fade(n, 0.8 , 0.3)
            # self.startBasicAwareness()

            if not self.facePosition == None:
                self.lookAtFace()
            else:
                self.motion.moveHead(self.headAngles)
            # self.startFaceTrackng()

            # else:
            #     self.ba_service.setEnabled(True)
            #     self.ba_service.setTrackingMode("Head")

        if dir == GazeDirection.LOOKING_ON_RIGHT_MIDDLE.value:

            # self.stopFaceTracking()
            n = 'RightFaceLed2'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            n = 'FaceLedLeft2'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            self.motion.moveHead(np.add([-15.0, 0.0], self.headAngles))
        if dir == GazeDirection.LOOKING_ON_LEFT_MIDDLE.value:

            # self.stopFaceTracking()
            n = 'RightFaceLed6'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            n = 'FaceLedLeft6'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            self.motion.moveHead(np.add([15.0, 0.0], self.headAngles))
        if dir == GazeDirection.LOOKING_ON_MIDDLE_UP.value:
            # self.stopFaceTracking()
            n = 'FaceLedRight0'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            n = 'FaceLedLeft0'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            self.motion.moveHead(np.add([0.0, -5.0], self.headAngles))
            # print "dupa"
        if dir == GazeDirection.LOOKING_ON_MIDDLE_DOWN.value:

            # self.stopFaceTracking()
            n = 'FaceLedRight4'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            n = 'FaceLedLeft4'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            self.motion.moveHead(np.add([0.0, 5.0], self.headAngles))
        if dir == GazeDirection.LOOKING_ON_RIGHT_UP.value:

            # self.stopFaceTracking()
            n = 'FaceLedRight7'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            n = 'FaceLedLeft1'
            self.leds_service.fadeRGB(n, "blue", 0.3)
            self.motion.moveHead(np.add([-15.0, -5.0], self.headAngles))

    def cleanUp(self):
        self.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)
        self.stopFaceTracking()
        self.ba_service.setEnabled(False)
        self.posture.goToPosture("Stand", 0.3)
        self.tracker_service.unregisterAllTargets()
        # if self.gesturesEnabled == True:
            # self.stopHeadNoise()
        # self.mqttHelper.stopLoop()
        self.turnOnTablet()

    def prepare(self):
        self.posture.goToPosture("Stand", 0.3)
        self.tracker_service.registerTarget(self.targetName, self.faceWidth)
        self.ba_service.setEnabled(False)
        # if self.gesturesEnabled == True:
        #     self.startHeadNoise()
        # self.mqttHelper.startLoop()
        self.turnOffTablet()


    def doMakeNoise(self):
        t = currentThread()
        while getattr(t, "do_run", True):
            self.motion.makeNoise()
            time.sleep(random.uniform(0.3, 0.8))


    def startHeadNoise(self):
        self.isNoiceRuning = True
        self.thread = Thread(target=self.doMakeNoise, args=())
        self.thread.start()
        # pass


    def stopHeadNoise(self):
        self.isNoiceRuning = False
        self.thread.do_run = False
        self.thread.join()
        # pass

    def startDepthRecording(self, name):
        self.depthRec.start_recording(name)

    def stopDepthRecording(self):
        self.depthRec.stop_recording()



