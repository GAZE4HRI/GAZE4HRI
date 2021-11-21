import paho.mqtt.client as paho


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    print "mess"
    print(msg.topic + " " + str(msg.qos) + " " + message)


client = paho.Client(client_id="ser")
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("192.168.1.100", 1883)
client.subscribe("pepper/speechToText/results", qos=2)

client.loop_forever()