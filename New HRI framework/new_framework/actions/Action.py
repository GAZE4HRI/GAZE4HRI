import time
from threading import currentThread, Thread

import numpy as np



from analyser.Analyser import Analyser
from mqtt.MqttHelper import MqttHelper
from utils.Constants import GazeDirection, SystemState


class Action(object):
    def run(self, common_obj):
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def of(actionJson):
        if actionJson is None:
            return EmptyAction()
        elif actionJson['type'] == 'say':
            return SayAction(actionJson['text'])
        elif actionJson['type'] == 'wait':
            return WaitAction(actionJson['waitTime'])
        elif actionJson['type'] == 'waitOrClick':
            return WaitOrClickAction(actionJson['waitTime'])
        elif actionJson['type'] == 'waitGaussian':
            return WaitGaussianAction(actionJson['mean'], actionJson['std'], actionJson['min'])
        elif actionJson['type'] == 'waitGaussianThreaded':
            return WaitGaussianThreadedAction(actionJson['mean'], actionJson['std'], actionJson['min'])
        elif actionJson['type'] == 'waitGaussianOrClick':
            return WaitGaussianOrClickAction(actionJson['mean'], actionJson['std'], actionJson['min'])
        elif actionJson['type'] == 'look':
            return LookAction(actionJson['dir'])
        elif actionJson['type'] == 'playSound':
            return PlaySoundAction(actionJson['path'], bool(actionJson['async']), actionJson['volume'])
        elif actionJson['type'] == 'playSoundAndAnimation':
            return PlaySoundAndAnimationAction(actionJson['path'], bool(actionJson['async']), actionJson['gestures'], actionJson['volume'])
        elif actionJson['type'] == 'sayOnAndroidAndPlayAnimationAction':
            return SayOnAndroidAndPlayAnimationAction(actionJson['text'], actionJson['gestures'])
        elif actionJson['type'] == 'prepareAction':
            return PrepareAction(actionJson['objToPrepare'])
        elif actionJson['type'] == 'cleanAction':
            return CleanAction(actionJson['objToClean'])
        elif actionJson['type'] == 'cleanAllAction':
            return CleanAllAction()
        elif actionJson['type'] == 'startFaceTrackingAction':
            return StartFaceTrackingAction()
        elif actionJson['type'] == 'stopFaceTrackingAction':
            return StopFaceTrackingAction()
        elif actionJson['type'] == 'saveFacePositionAction':
            return SaveFacePositionAction()
        elif actionJson['type'] == 'lookInDirAction':
            return LookInDirAction(actionJson['dir'])
        elif actionJson['type'] == 'setAction':
            return Set(actionJson['var'], actionJson['val'])
        elif actionJson['type'] == 'setOptionAction':
            return SetOption(actionJson['var'], actionJson['val'])
        elif actionJson['type'] == 'resetClick':
            return ResetClick()
        elif actionJson['type'] == 'gazeAction':
            return GazeAction()
        else:
            return UnknownAction()


class EmptyAction(Action):
    def run(self, common_obj):
        pass

class UnknownAction(Action):
    def run(self, common_obj):
        pass


class WaitAction(Action):

    def __init__(self, wait_time):
        self.wait_time = wait_time

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.WAIT, time.time())
        i = int(self.wait_time / 0.5)
        for t in range(i):
            time.sleep(0.5)
        common_obj["options"]["interrupt_lock"].release()
        time.sleep(0.01)
        common_obj["options"]["interrupt_lock"].acquire()
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())


class WaitGaussianAction(Action):

    def __init__(self, mean, std, minimum):
        self.mean = mean
        self.std = std
        self.minimum = minimum

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.WAIT, time.time())
        timeToWait = np.max([self.minimum, np.random.normal(self.mean, self.std)])
        i = int(timeToWait / 0.5)
        for t in range(i):
            time.sleep(timeToWait/float(i))
            common_obj["options"]["interrupt_lock"].release()
            time.sleep(0.01)
            common_obj["options"]["interrupt_lock"].acquire()
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())


class WaitGaussianThreadedAction(Action):

    def __init__(self, mean, std, minimum):
        self.mean = mean
        self.std = std
        self.minimum = minimum

    def run(self, common_obj):
        t = currentThread()
        timeToWait = np.max([self.minimum, np.random.normal(self.mean, self.std)])
        nexttime = time.time() + timeToWait / 10.0
        partTimeStart = time.time()
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


class WaitGaussianOrClickAction(Action):

    def __init__(self, mean, std, minimum):
        self.mean = mean
        self.std = std
        self.minimum = minimum

    def run(self, common_obj):
        timeToWait = np.max([self.minimum, np.random.normal(self.mean, self.std)])
        common_obj["options"]["system_state"] = (SystemState.WAIT, time.time())
        i = int(timeToWait / 0.5)
        for t in range(i):
            time.sleep(timeToWait/float(i))
            if common_obj["click"].clicked:
                break
            common_obj["options"]["interrupt_lock"].release()
            time.sleep(0.01)
            common_obj["options"]["interrupt_lock"].acquire()
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())

        
        
class WaitOrClickAction(Action):
    def __init__(self, wait_time):
        self.wait_time = wait_time

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.WAIT, time.time())
        i = int(self.wait_time / 0.5)
        for t in range(i):
            time.sleep(0.5)
            if common_obj["click"].clicked:
                break
            common_obj["options"]["interrupt_lock"].release()
            time.sleep(0.01)
            common_obj["options"]["interrupt_lock"].acquire()
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())

class Set(Action):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def run(self, common_obj):
        if "click" == self.var:
            common_obj["click"].clicked = self.val
        else:
            common_obj[self.var] = self.val

class SetOption(Action):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def run(self, common_obj):
        common_obj["options"][self.var] = self.val


class ResetClick(Action):
    def run(self, common_obj):
        if not common_obj["click"] == None:
            common_obj["click"].clicked = False



class SayAction(Action):

    def __init__(self, text):
        self.text = text

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())
        common_obj["robot_client"].say(self.text)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time() + 2)


class LookAction(Action):

    def __init__(self, dir):
        self.dir = dir

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_NON_BLOCKING_ACTION, time.time())
        common_obj["robot_client"].lookInDir(self.dir)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time() + 2)


class PlaySoundAction(Action):

    def __init__(self, path, async, volume):
        self.path = path
        self.async = async
        self.vol = volume

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())
        common_obj["robot_client"].playSound(self.path, self.async, self.vol)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time() + 5)

class PlaySoundAndAnimationAction(Action):

    def __init__(self, path, async, gestures, volume):
        self.path = path
        self.async = async
        self.gestures = gestures
        self.vol = volume

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())
        future, vol= common_obj["robot_client"].playSound(self.path, self.async, self.vol)
        common_obj["robot_client"].playAnimation(self.gestures)
        future.value()
        common_obj["robot_client"].setSystemVolume(vol)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())

class SayOnAndroidAndPlayAnimationAction(Action):

    def __init__(self, text, gestures):
        self.text = text
        self.gestures = gestures

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())
        common_obj["robot_client"].sayOnAndroid(self.text)
        common_obj["robot_client"].playAnimation(self.gestures)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())

class GazeAction(Action):
    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_NON_BLOCKING_ACTION, time.time())
        aversionList = [GazeDirection.LOOKING_ON_MIDDLE_UP.value,
                        GazeDirection.LOOKING_ON_MIDDLE_DOWN.value,
                        GazeDirection.LOOKING_ON_LEFT_MIDDLE.value,
                        GazeDirection.LOOKING_ON_RIGHT_MIDDLE.value,
                        GazeDirection.LOOKING_ON_RIGHT_UP.value]

        humanProbabilityModel = common_obj["options"]["humanProbabilityModel"]
        dir = ""
        if common_obj["options"].get("contact_mode", False) :
            dir = GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value
        if common_obj["options"].get("aversion_mode", False) :
            dir = np.random.choice(aversionList)
        if common_obj["options"].get("human_mode", False) :
            dir = np.random.choice(aversionList, p=humanProbabilityModel)
        print "gaze dir " + dir
        common_obj["robot_client"].lookInDir(dir)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())



class StartFaceTrackingAction(Action):
    def run(self, common_obj):
        common_obj["robot_client"].startFaceTracking()


class SaveFacePositionAction(Action):

    def run(self, common_obj):
        common_obj["robot_client"].saveFacePosition()


class StopFaceTrackingAction(Action):
    def run(self, common_obj):
        common_obj["robot_client"].stopFaceTracking()


class LookInDirAction(Action):
    def __init__(self, dir):
        self.dir = dir

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_NON_BLOCKING_ACTION, time.time())
        common_obj["robot_client"].lookInDir(self.dir)
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())


class Click():
    def __init__(self):
        self.lastClicked = time.time()
        self.clicked = False

    def on_click(self, x, y, button, pressed):
        print "mouse pressed"
        now = time.time()
        if now - self.lastClicked > 5:
            self.lastClicked = now
            self.clicked = True

    def on_click_mqtt(self):
        now = time.time()
        if now - self.lastClicked > 5:
            self.lastClicked = now
            self.clicked = True

    def is_clicked(self):
        now = time.time()
        if now - self.lastClicked > 3:
            self.clicked = False
        return self.clicked

    def on_press(self, key):
        print '{0} pressed'.format(key)
        now = time.time()

        # if key.name == "page down":
        from pynput.keyboard import Key
        if key == Key.page_down:
            if now - self.lastClicked > 5:
                self.lastClicked = now
                self.clicked = True


class PrepareAction(Action):

    def __init__(self, obj_to_prepare):
        self.obj_to_prepare = obj_to_prepare

    def lookupMethod(self, command):
        return getattr(self, 'make_' + command.upper(), None)

    def make_VIDEO_RECORDER(self, common_obj):
        if common_obj["android_connection"]:
            common_obj["android_connection"].publishOnTopic(common_obj["options"]["recordingTopic"],
                                                            common_obj["options"]["startRecording"] + " " +
                                                            common_obj["options"]["experimentName"])
        try:
            common_obj["robot_client"].startVideoRecordPepper("/home/nao/experiment-one/videoRecords",
                                                                common_obj["options"]["experimentName"] + ".avi")
        except:
            common_obj["robot_client"].stopVideoRecordPepper()
            print "Video recording problem"

        try:
            common_obj["robot_client"].startDepthRecording("experiment-one/videoRecords" + "/depth_" +
                                             common_obj["options"]["experimentName"] + ".avi")
        except:
            print "depth recording problem"
            common_obj["robot_client"].stopDepthRecording()
        return True


    def make_AUDIO_RECORDER(self, common_obj):
        try:
            common_obj["robot_client"].startAudioRecordPepper(
                "/home/nao/experiment-one/recordings/" + common_obj["options"]["experimentName"] + ".wav")
        except:
            common_obj["robot_client"].stopAudioRecordPepper()
            print "Audio recording problem"
            return False
        return True


    def make_ALL_RECORDER(self, common_obj):
        common_obj["audio_recorder"] = self.make_AUDIO_RECORDER(common_obj)
        common_obj["video_recorder"] = self.make_VIDEO_RECORDER(common_obj)
        return True


    def make_MOUSE_LISTENER(self, common_obj):
        from pynput import mouse, keyboard

        if common_obj.get("click", None) == None:
            common_obj["click"] = Click()
        mouseListener = mouse.Listener(on_click=common_obj["click"].on_click)
        mouseListener.start()
        return mouseListener

    def make_KEY_LISTENER(self, common_obj):
        if common_obj.get("click", None) == None:
            common_obj["click"] = Click()

        # import keyboard
        # keyboardListener = keyboard.on_press(common_obj["click"].on_press)
        from pynput import keyboard
        keyboardListener = keyboard.Listener(on_press=common_obj["click"].on_press)
        keyboardListener.start()
        return keyboardListener

    def make_CLICK_LISTENER(self, common_obj):
        if common_obj.get("click", None) == None:
            common_obj["click"] = Click()
        common_obj["android_connection"].click = common_obj["click"]
        return common_obj["click"]

    def make_ROBOT_CLIENT(self, common_obj):
        common_obj["robot_client"].prepare()
        return common_obj["robot_client"]

    def make_VIDEO_ANALYSER(self, common_obj):
        if common_obj.get("Analyser", None) == None:
            ana = Analyser(common_obj["session"], common_obj["options"])
            common_obj["Analyser"] = ana
        common_obj["Analyser"].start_video_analysis()
        return common_obj["Analyser"]

    def make_QUESTON_DETECTOR(self, common_obj):
        if common_obj.get("Analyser",None) == None:
            ana = Analyser(common_obj["session"], common_obj["options"])
            common_obj["Analyser"] = ana
        common_obj["Analyser"].start_question_detection()
        return common_obj["Analyser"]

    def make_ANDROID_CONNECTION(self, common_obj):
        mqttHelper = MqttHelper(common_obj["options"]["STTEnabled"], common_obj["options"]["ip"])
        mqttHelper.subscribe()
        mqttHelper.setEndOfSpeechHandler(common_obj)
        mqttHelper.startLoop()
        return mqttHelper

    def do_UNKNOWN(self, rest):
        raise NotImplementedError, 'received unknown command'

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())
        for obj in self.obj_to_prepare:
            method = self.lookupMethod(obj) or self.do_UNKNOWN
            try:
                common_obj[obj] = method(common_obj)
            except:
                print "unknown command " + str(obj)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())


class CleanAction(Action):
    def __init__(self, obj_to_clean):
        self.obj_to_clean = obj_to_clean

    def lookupMethod(self, command):
        return getattr(self, 'clean_' + command.upper(), None)

    def clean_VIDEO_RECORDER(self, common_obj):
        if common_obj["android_connection"]:
            common_obj["android_connection"].publishOnTopic(common_obj["options"]["recordingTopic"],
                                                            common_obj["options"]["stopRecording"] + " ")
        common_obj["robot_client"].stopVideoRecordPepper()
        common_obj["robot_client"].stopDepthRecording()
        return True

    def clean_AUDIO_RECORDER(self, common_obj):
        common_obj["robot_client"].stopAudioRecordPepper()
        return True

    def clean_ALL_RECORDER(self, common_obj):
        common_obj["audio_recorder"] = self.clean_AUDIO_RECORDER(common_obj)
        common_obj["video_recorder"] = self.clean_VIDEO_RECORDER(common_obj)
        return True

    def clean_ANDROID_CONNECTION(self, common_obj):
        common_obj["android_connection"].stopLoop()
        return True

    def clean_MOUSE_LISTENER(self, common_obj):
        common_obj["mouse_listener"].stop()
        return True

    def clean_ANALYSER(self, common_obj):
        print "clean_ANALYSER"
        common_obj["Analyser"].stop_video_analysis()
        common_obj["Analyser"].stop_question_detection()
        return True

    def clean_VIDEO_ANALYSER(self, common_obj):
        return True

    def clean_QUESTON_DETECTOR(self, common_obj):
        return True

    def clean_KEY_LISTENER(self, common_obj):

        common_obj["key_listener"].stop()
        return True

    def clean_CLICK_LISTENER(self, common_obj):
        print "clean_CLICK_LISTENER"
        common_obj["click"] = None

    def clean_ROBOT_CLIENT(self, common_obj):
        return common_obj["robot_client"].cleanUp()

    def do_UNKNOWN(self, rest):
        raise NotImplementedError, 'received unknown command'

    def clean_CLICK(self, common_obj):
        common_obj["click"] = None

    def run(self, common_obj):
        common_obj["options"]["system_state"] = (SystemState.IN_BLOCKING_ACTION, time.time())
        for obj in self.obj_to_clean:
            method = self.lookupMethod(obj) or self.do_UNKNOWN
            print "claeaning" + str(obj)
            try:
                method(common_obj)
            except:
                print "unknown command " + str(obj)
        common_obj["options"]["system_state"] = (SystemState.IDLE, time.time())

class CleanAllAction(Action):

    def __clean_android_connection(self, common_obj):
        common_obj["android_connection"].stopLoop()
        return True

    def run(self, common_obj):
        obj_to_clean = {}
        for k,v in common_obj.iteritems():
            if k == "options" or\
                            k == "android_connection" or \
                                                        k == "session":
                continue
            elif "THREAD" in k.upper():
                v.do_run = False
                v.join()
                continue

            obj_to_clean[k] = v
        clean_action = CleanAction(obj_to_clean)
        clean_action.run(common_obj)
        if common_obj.get("android_connection", False):
            self.__clean_android_connection(common_obj)
