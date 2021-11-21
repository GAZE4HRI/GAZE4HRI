from naoqi import ALProxy

# create proxy on ALMemory
memProxy = ALProxy("ALMemory","192.168.1.100",9559)

#get data. Val can be int, float, list, string
val = memProxy.getData("Device/DeviceList/ChestBoard/BodyId")
print val