import paho.mqtt.client as paho

class MqttHelper():
    def __init__(self, STTEnabled, broker_address="192.168.1.101"):

        self.client = paho.Client("robot")
        self.client.connect(broker_address)
        self.topic = "pepper/textToSpeech"
        self.subscribtionTopics = ("pepper/speechToText/results", 2)
        self.qos = 2
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.endOfSpeechHandler = None
        self.STTEnabled = STTEnabled

    def on_connect(self, client, userdata, rc):

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # self.subscribe()
        pass

    def publish(self, message):
        self.client.publish(self.topic, message, qos=self.qos)

    def publishOnTopic(self, topic, message):
        self.client.publish(topic, message, qos=self.qos)

    def subscribe(self):
        self.client.subscribe(self.subscribtionTopics)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode('utf-8')
        print(msg.topic + " " + str(msg.qos) + " " + message)
        if message == "EndOfSpeech":
            self.endOfSpeechHandler.on_endOfSpeech()


    def startLoop(self):
        self.client.loop_start()

    def stopLoop(self):
        self.client.loop_stop()

    def setEndOfSpeechHandler(self, handler):
        if self.STTEnabled:
            self.endOfSpeechHandler = handler


