import json
import sys
from mqtt.MqttHelper import MqttHelper



class ConfigReader():
    def loadConfig(self, path):
        config = json.load(open(path))
        config = self.__parse_config(config['platform'])
        return config



    def make_ANDROID_CONNECTION(self, common_obj):
        if len(common_obj["options"]["subscriptionTopics"]) > 0:
            if common_obj["options"]["robot_name"] == "avatar":
                from analyser.AudioSource.avatarAudioSource import AvatarAudioSource
                from analyser.videoSource.AvatarVideoSource import AvatarVideoSource
                vid = common_obj["options"].get("AvatarVideoSource", None)
                if vid is None:
                    vid = AvatarVideoSource()
                    common_obj["options"]["AvatarVideoSource"] = vid
                au = common_obj["options"].get("AvatarAudioSource", None)
                if au is None:
                    au = AvatarAudioSource()
                    common_obj["options"]["AvatarAudioSource"] = au
                mqttHelper = MqttHelper(common_obj["options"]["STTEnabled"], common_obj["options"]["ip"],
                                        common_obj["options"]["subscriptionTopics"], vid, au)
            else:
                mqttHelper = MqttHelper(common_obj["options"]["STTEnabled"], common_obj["options"]["ip"], common_obj["options"]["subscriptionTopics"])

        else:
            mqttHelper = MqttHelper(common_obj["options"]["STTEnabled"], common_obj["options"]["ip"])
        mqttHelper.subscribe()
        mqttHelper.setEndOfSpeechHandler(common_obj)
        mqttHelper.startLoop()
        return mqttHelper


    def make_PEPPER(self, common_obj):
        import qi
        from pepper.PepperClient import PepperClient
        session = qi.Session()
        try:
            session.connect("tcp://" + common_obj["options"]["ip"] + ":" + common_obj["options"]["port"])
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + common_obj["options"]["ip"] + "\" on port " + common_obj["options"]["port"] + ".\n"
                                                                                   "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)
        common_obj["session"] = session
        pepper_client = PepperClient(common_obj["session"],
                                     common_obj["options"]["gesturesEnabled"],
                                     common_obj["android_connection"],
                                     common_obj["options"]["humanTracking"])
        return pepper_client

    def make_AVATAR(self, common_obj):
        from avatar.AvatarClient import AvatarClient
        avatar_client = AvatarClient(common_obj["android_connection"], common_obj["options"]["unityTopic"], common_obj["options"]["configTopic"])
        common_obj["session"] = None
        return avatar_client

    def lookupMethod(self, command):
        return getattr(self, 'make_' + command.upper(), None)

    def create_robot_client(self, common_obj):

        for module in self.modules:
            common_obj[module] = self.lookupMethod(module)(common_obj)
        common_obj["robot_client"] = self.lookupMethod(self.robot_name)(common_obj)


    def __parse_config(self, config_json):
        common_obj = {}
        common_obj["options"] = config_json["options"]
        self.robot_name = config_json["robot_name"]
        self.modules = config_json["modules"]
        return common_obj

if __name__ == '__main__':

    cr = ConfigReader()
    print cr.loadConfig("platform/pepper.json")