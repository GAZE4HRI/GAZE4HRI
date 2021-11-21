
import random
import time
from threading import Thread, currentThread

from gaze.CustomGaze import CustomGaze
from gaze.RobotGaze import RobotGaze

from mqtt.MqttHelper import MqttHelper
from pepper.PepperClient import PepperClient
from scenario.ExperimentOneScenario import ExperimentOneScenario


import pynput.mouse as mouse
from pynput.keyboard import Key, Listener
from speechRecognition.GoogleCloud import GoogleCloud
from utils.Constants import GazeDirection
import numpy as np


class ScenarioControler(object):
    def __init__(self, session, scenarioPath, options):
        self.STTEnabled = options['SpeechToTextEnabled']
        self.gesturesEnabled = options['gesturesEnabled']
        self.gazeCase = options['gazeCase']
        self.STTAndroid = options['SpeechToTextAndroid']
        self.experimentName = options['experimentName']
        self.directory = options['directory']
        self.pepperIP = options['pepperIP']
        self.debugMode = options['debugMode']
        self.humanTracking = options['humanTracking']

        self.mqttHelper = MqttHelper(self.STTEnabled, self.pepperIP)
        self.mqttHelper.subscribe()
        self.mqttHelper.setEndOfSpeechHandler(self)
        self.period = [0.6, 1]
        self.scenario = ExperimentOneScenario(scenarioPath,self.gazeCase)
        self.pepperClient = PepperClient(session, self.gesturesEnabled, self.mqttHelper, self.humanTracking)
        # self.RobotGaze = RobotGaze(session)
        self.CustomGaze = CustomGaze(session)
        self.CustomGaze.subscribe()

        self.mouseListener = None
        if self.debugMode:
            self.mouseListener =  mouse.Listener(on_click = self.on_click)
            self.mouseListener.start()

        self.keyListener = Listener(on_press=self.on_press)
        self.keyListener.start()

        self.waitTimesDict = {
            "contact_mode": ((5, 1), (5, 1)),
            "aversion_mode": ((5, 1), (5, 1)),
            "human_gaze_mode":((4.4, 1), (0.3, 0.22))
        }



        self.speachTopic = "pepper/speechToText"
        self.recordingTopic = "pepper/video"
        self.startRecording = "start_recording"
        self.stopRecording = "stop_recording"
        self.startRecognition = "start recognition"
        self.stopRecognition = "stop recognition"
        if self.STTEnabled:
            if not self.STTAndroid:
                self.googleCloud = GoogleCloud(session)
        self.clicked = False
        self.lastClicked = time.time()
        self.gazeRutineThread = None
        self.isGazeRutineStarted = False


    def on_click(self, x, y, button, pressed):
        print "mouse pressed"
        now = time.time()
        if now - self.lastClicked > 5:
            self.lastClicked = now
            self.clicked = True

    def on_press(self, key):
        print '{0} pressed'.format(key)
        now = time.time()
        if key == Key.page_down:
            if now - self.lastClicked > 5:
                self.lastClicked = now
                self.clicked = True


    def on_endOfSpeech(self):
        self.clicked = True





    def run(self):



        numOfStages = self.scenario.getNumberOfStages()
        action, waitTime = self.scenario.getGreeting()



        # try:
        #     self.pepperClient.startVideoRecordPepper("/home/nao/experiment-one/videoRecords",
        #                                              self.experimentName + ".avi")
        # except:
        #     self.pepperClient.stopVideoRecordPepper()
        #     print "Video recording problem"
        # try:
        #     self.pepperClient.startAudioRecordPepper(
        #         "/home/nao/experiment-one/recordings/" + self.experimentName + ".wav")
        # except:
        #     self.pepperClient.stopAudioRecordPepper()
        #     print "Audio recording problem"
        # try:
        #     self.pepperClient.startDepthRecording("experiment-one/videoRecords" + "/depth_" +
        #                                              self.experimentName + ".avi")
        #
        # except:
        #     print "depth recording problem"
        #     self.pepperClient.stopDepthRecording()

        thread = Thread(target=self.CustomGaze.run,
                        args=(self.directory + "/" + self.experimentName + "_gaze" + ".txt",))
        thread.start()


        self.mqttHelper.publishOnTopic(self.recordingTopic, self.startRecording + " " + self.experimentName)


        self.pepperClient.prepare()

        if self.gazeCase in ['human_gaze_mode','contact_mode', 'aversion_mode']:
            self.pepperClient.startFaceTrackng()
            self.pepperClient.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)


        self.__react(action)

        time.sleep(waitTime)
        self.pepperClient.saveFacePosition()
        if self.gazeCase == 'aversion_mode':
            self.pepperClient.stopFaceTracking()
            self.startGazeRutine()

        # if self.humanTracking == 'half':
        #     self.pepperClient.stopBasicAwareness()

        self.scenario.shuffleGroups()

        if self.gazeCase == None:
            self.scenario.shuffleGazeCase()
        f = open(self.directory + "/" + self.experimentName + "_GazeCase" + ".txt", "w")
        f.write(self.scenario.getGazeCase())
        f.close()

        i=0
        while self.scenario.hasNextStage():
            i = i + 1
            threadRecognition = None
            if self.STTEnabled:
                if self.STTAndroid:
                    self.mqttHelper.publishOnTopic(self.speachTopic, self.startRecognition)
                else:
                    threadRecognition = Thread(target=self.googleCloud.run,
                                       args=(self.directory + "/" + self.experimentName + "_speech_" + str(i) + ".txt",))
                    threadRecognition.start()

            # thread = Thread(target=make_record, args=(self.directory + "/" + self.experimentName + "_" + str(i) + ".wav", waitTime))




            action, waitTime = self.scenario.getNextStage()
            start = time.time()
            if self.gazeCase in 'human_gaze_mode':
                # self.stopGazeRutine()
                self.pepperClient.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)
                self.pepperClient.startFaceTrackng()

            self.__react(action)
            stop = time.time()

            if self.gazeCase == 'human_gaze_mode':
                self.pepperClient.saveFacePosition()
                self.pepperClient.stopFaceTracking()
                # self.startGazeRutine()


            startTime = time.time()
            self.clicked = False
            if self.gazeCase == 'human_gaze_mode':
                self.gazeLoop(waitTime)
            else:
                while self.clicked == False:
                    time.sleep(0.5)
                    now = time.time()
                    if now - startTime > waitTime:
                        break


            if self.STTEnabled:
                if self.STTAndroid:
                    self.mqttHelper.publishOnTopic(self.speachTopic, self.stopRecognition)
                else:
                    threadRecognition.do_run = False



            # threadRecognition.join()



        action, waitTime = self.scenario.getGoodbye()
        if self.gazeCase in 'human_gaze_mode':
            self.stopGazeRutine()
            self.pepperClient.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)
            self.pepperClient.startFaceTrackng()
        self.__react(action)
        time.sleep(waitTime)

        # self.pepperClient.stopAudioRecordPepper()
        # self.pepperClient.stopVideoRecordPepper()
        # self.pepperClient.stopDepthRecording()
        thread.do_run = False

        thread.join()

        if  self.isGazeRutineStarted:
            self.stopGazeRutine()

        self.mqttHelper.publishOnTopic(self.recordingTopic, self.stopRecording + " ")
        self.pepperClient.cleanUp()
        self.CustomGaze.unsubscribe()

        if self.debugMode:
            self.mouseListener.stop()
        self.keyListener.stop()
        time.sleep(2)


    def startGazeRutine(self):
        self.isGazeRutineStarted = True
        self.gazeRutineThread = Thread(target=self.runGazeRutine, args=())
        self.gazeRutineThread.start()

    def stopGazeRutine(self):
        if self.gazeRutineThread == None:
            return
        self.isGazeRutineStarted = False
        self.gazeRutineThread.do_run = False
        self.gazeRutineThread.join()

    def runGazeRutine(self):
        t = currentThread()
        while getattr(t, "do_run", True):

            mean, std = self.waitTimesDict[self.gazeCase][0]
            timeToWait = np.max([0.1, np.random.normal(mean, std)])
            if getattr(t, "do_run", True):
                self.pepperClient.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)
            partTimeStart = time.time()
            nexttime = time.time() + timeToWait / 10.0
            now = time.time()
            while getattr(t, "do_run", True):
                now = time.time()
                tosleep = nexttime - now
                if tosleep > 0:
                    time.sleep(tosleep)
                    nexttime += timeToWait / 10.0
                else:
                    nexttime += timeToWait / 10.0
                if now - partTimeStart > timeToWait:
                    break

            mean, std = self.waitTimesDict[self.gazeCase][1]

            timeToWait = np.max([0.1, np.random.normal(mean, std)])
            if getattr(t, "do_run", True):
                gazeAction = self.scenario.getGazeAction()
                self.__react(gazeAction)
            if self.gazeCase == 'human_gaze_mode' and getattr(t, "do_run", True):
                time.sleep(timeToWait)
            else:
                partTimeStart = time.time()
                nexttime = time.time() + timeToWait / 10.0
                while getattr(t, "do_run", True):
                    now = time.time()
                    tosleep = nexttime - now
                    if tosleep > 0:
                        time.sleep(tosleep)
                        nexttime += timeToWait / 10.0
                    else:
                        nexttime += timeToWait / 10.0
                    if now - partTimeStart > timeToWait:
                        break


    def gazeLoop(self, waitTime):
        startTime = time.time()
        self.clicked = False
        while self.clicked == False:
            mean, std = self.waitTimesDict[self.gazeCase][0]
            timeToWait = np.max([0.1, np.random.normal(mean, std)])
            if self.clicked == False:
                self.pepperClient.lookInDir(GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value)
            partTimeStart = time.time()
            nexttime = time.time() + timeToWait / 10.0

            while self.clicked == False:
                now = time.time()
                if now - startTime > waitTime:
                    break
                tosleep = nexttime - now
                if tosleep > 0:
                    time.sleep(tosleep)
                    nexttime += timeToWait / 10.0
                else:
                    nexttime += timeToWait / 10.0
                if now - partTimeStart > timeToWait:
                    break



            mean, std = self.waitTimesDict[self.gazeCase][1]
            if self.clicked == False:
                timeToWait = np.max([0.1, np.random.normal(mean, std)])
                gazeAction = self.scenario.getGazeAction()
                self.__react(gazeAction)
            if self.gazeCase == 'human_gaze_mode' and self.clicked == False:
                time.sleep(timeToWait)
            else:
                partTimeStart = time.time()
                nexttime = time.time() + timeToWait / 10.0
                while self.clicked == False:
                    now = time.time()
                    if now - startTime > waitTime:
                        break

                    tosleep = nexttime - now
                    if tosleep > 0:
                        time.sleep(tosleep)
                        nexttime += timeToWait / 10.0
                    else:
                        nexttime += timeToWait / 10.0
                    if now - partTimeStart > timeToWait:
                        break


            now = time.time()
            if now - startTime > waitTime:
                break

    def __react(self, action):
        action.run(self.pepperClient)
