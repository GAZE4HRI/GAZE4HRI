import random

import almath
import numpy as np
import time

from utils.Utils import transformToDeg


class Motion(object):
    def __init__(self, session):
        self.motion_service = session.service("ALMotion")
        self.lastValue = []

    def moveHeadRads(self, rads):
        # (-50, 50) degrees
        #           --
        #        -- 00 ++
        #           ++
        if not len(rads) == 2:
            raise ValueError("not enough arguments")
        if rads[0] >= 1 or rads[0] <= -1:
            raise ValueError("Illegal yaw angles value")
        if rads[1] >= 1 or rads[1] <= -1:
            raise ValueError("Illegal pitch angles value")
        # maybe use stiffnessInterpolation?
        names = "Head"
        fractionMaxSpeed = 0.02
        self.motion_service.angleInterpolationWithSpeed(names, rads, fractionMaxSpeed)

    def moveHead(self, angles):
        # (-50, 50) degrees
        #           --
        #        -- 00 ++
        #           ++
        if not len(angles) == 2:
            raise ValueError("not enough arguments")
        if angles[0] >= 50 or angles[0] <= -50:
            angles[0] = np.min([50, np.max([-50, angles[0]])])
            # raise ValueError("Illegal yaw angles value")
        if angles[1] >= 35 or angles[1] <= -35:
            angles[1] = np.min([35,np.max([-35,angles[1]])])
            # raise ValueError("Illegal pitch angles value")
        # maybe use stiffnessInterpolation?

        names = "Head"

        # self.motion_service.setStiffnesses("Head", 1.0)
        yaw = float(angles[0] * almath.TO_RAD)
        pitch = float(angles[1] * almath.TO_RAD)
        fractionMaxSpeed = 0.1
        self.motion_service.angleInterpolationWithSpeed(names, [yaw, pitch], fractionMaxSpeed)
        # print [yaw, pitch]
        time.sleep(0.5)
        # self.motion_service.setStiffnesses("Head", 0.0)

    def getHeadPosition(self):
        names = "Head"
        useSensors = True
        return transformToDeg(self.motion_service.getAngles(names, useSensors))

    def makeNoise(self):
        # Example that finds the difference between the command and sensed angles.
        names = "Head"
        useSensors = False
        commandAngles = self.motion_service.getAngles(names, useSensors)
        expectedValues = [0.08726646192371845,-0.1745329238474369]
        ind = self.find_nearest(expectedValues,commandAngles[1])
        if ind == 0:
            commandAngles = [0.0, 0.08726646192371845]
        elif ind == 1:
            commandAngles = [0.0, -0.1745329238474369]
        if not self.lastValue:
            valueYaw = random.uniform(-0.1, 0.1)
            valuePitch = random.uniform(-0.1, 0.1)
            self.lastValue.append(valueYaw)
            self.lastValue.append(valuePitch)
            # print "last 1 " + str(self.lastValue)
            # print commandAngles
            commandAngles = [x + y for x, y in zip(commandAngles, self.lastValue)]
            # print commandAngles
            self.moveHeadRads(commandAngles)
        else:
            # print "last 2 " + str(self.lastValue)
            # print commandAngles
            commandAngles = [x - y for x, y in zip(commandAngles, self.lastValue)]
            # print commandAngles
            self.moveHeadRads(commandAngles)
            self.lastValue = []

    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array) - np.abs(value)).argmin()
        return array[idx]

