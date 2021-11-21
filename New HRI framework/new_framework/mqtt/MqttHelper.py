import base64
import json
from Queue import Queue
from threading import Thread

import paho.mqtt.client as paho

class MqttHelper():
    def __init__(self, STTEnabled, broker_address="192.168.1.101", subscribtionTopics = ("pepper/speechToText/results", 2),
                 avatarVideoSource = None, avatarAudioSource = None):
        self.data_queue = Queue()
        self.client = paho.Client("robot")
        self.client.connect(broker_address)
        self.topic = "pepper/textToSpeech"
        self.subscribtionTopics = subscribtionTopics
        self.qos = 2
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.endOfSpeechHandler = None
        self.STTEnabled = STTEnabled
        self.raw_data = {"audio": b'', "video": b''}
        self.avatarVideoSource = avatarVideoSource
        self.avatarAudioSource = avatarAudioSource
        self.data_worker = Thread(target=self.run_data_worker, args=())
        self.data_worker.start()
        self.click = None

    def on_connect(self, client, userdata, rc):

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # self.subscribe()
        pass

    def publish(self, message):
        print("publish " + message)
        self.client.publish(self.topic, message, qos=self.qos)

    def publishOnTopic(self, topic, message):
        print("publish topic " + message)
        self.client.publish(topic, message, qos=self.qos)

    def subscribe(self):
        self.client.subscribe(self.subscribtionTopics)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode('utf-8')
        if not msg.topic == "update/":
            print(msg.topic + " " + str(msg.qos) + " " + message)
        if message == "EndOfSpeech":
            self.endOfSpeechHandler.on_endOfSpeech()
        if msg.topic == "click/" and message == "click":
            if self.click:
                self.click.on_click_mqtt()
        else:
            message = json.loads(msg.payload)
            type = message["type"]
            if "raw_data" in message:
                timestamp_raw = message["timestamp"]
                self.data_queue.put((type,message["raw_data"]))
                # self.raw_data[type] = base64.b64decode(message["raw_data"])
                # if type == "video":
                #     self.avatarVideoSource.putImage(self.raw_data[type])
                # elif type == "audio":
                #     self.avatarAudioSource.putAudio(self.raw_data[type])
    def run_data_worker(self):
        while True:
            item = self.data_queue.get()
            if item is None or item == ():
                break
            type = item[0]
            raw_data = base64.b64decode(item[1])
            if type == "video":
                self.avatarVideoSource.put_image(raw_data)
            elif type == "audio":
                self.avatarAudioSource.put_audio(raw_data)
            self.data_queue.task_done()


    def unsubscribe(self):
        self.client.unsubscribe(self.subscribtionTopics)

    def startLoop(self):
        self.client.loop_start()

    def stopLoop(self):
        self.data_queue.put(None)
        self.client.loop_stop()

    def setEndOfSpeechHandler(self, handler):
        if self.STTEnabled:
            self.endOfSpeechHandler = handler


