from random import random, randint, shuffle, randrange

from scenario.Scenario import Scenario
import json

from scenario.Action import Action, LookAction
from utils.Constants import GazeDirection
import numpy as np
class ExperimentOneScenario(Scenario):

    def __init__(self, scenarioPath,gazeCase=None):
        self.greeting, self.groups, self.goodbye = self.loadScenario(scenarioPath)
        self.gazeCases = ["contact_mode", "aversion_mode", "human_gaze_mode"]
        if gazeCase == None:
            self.gazeCase = self.gazeCases[randint(0, (len(self.gazeCases) - 1))]
        else:
            self.gazeCase = gazeCase
        self.curentGroup = 0
        self.curentStage = 0
        self.performedStages = 0


    def getNextStage(self):
        self.performedStages = self.performedStages + 1
        stage = self.groups[self.curentGroup][self.curentStage]
        self.curentStage = self.curentStage + 1
        if self.curentStage >= len(self.groups[self.curentGroup]):
            self.curentGroup = self.curentGroup + 1
            self.curentStage = 0
        return stage

    def hasNextStage(self):
        return self.performedStages < self.getNumberOfStages()

    def shuffle_slice(self, a, start, stop):
        i = start
        while (i < stop - 1):
            idx = randrange(i, stop)
            a[i], a[idx] = a[idx], a[i]
            i += 1

    def shuffleGroups(self):

        if len(self.groups) > 2:
            # self.shuffle_slice(self.groups, 1, len(self.groups))

            self.groups = [self.groups[0], self.groups[1], self.groups[2]]

    def shuffleGazeCase(self):
        self.gazeCase = self.gazeCases[randint(0, (len(self.gazeCases) - 1))]

    def getGazeCase(self):
        return self.gazeCase

    def getStage(self, i):
        stage = None
        if i <= self.getNumberOfStages():
            length = 0
            for group in self.groups:
                length = length + len(group)
                if i <= length:
                    return group[i-length-len(group)]
        return stage

    def getNumberOfStages(self):
        length = 0
        for group in self.groups:
            length = length + len(group)
        return length

    def getGreeting(self):
        return self.greeting

    def getGoodbye(self):
        return self.goodbye

    def loadScenario(self, path):
        config = json.load(open(path))
        greeting = Action.of(config['greeting']['action'])
        greeting_waittime = int(config['greeting']['waitTime'])

        stages = self.__parseStages(config['stages'])

        goodbye = Action.of(config['goodbye']['action'])
        goodbye_waittime = int(config['goodbye']['waitTime'])

        return (greeting, greeting_waittime), stages, (goodbye, goodbye_waittime)

    def getGazeAction(self):
        aversionList = [GazeDirection.LOOKING_ON_MIDDLE_UP.value,
                        GazeDirection.LOOKING_ON_MIDDLE_DOWN.value,
                        GazeDirection.LOOKING_ON_LEFT_MIDDLE.value,
                        GazeDirection.LOOKING_ON_RIGHT_MIDDLE.value,
                        GazeDirection.LOOKING_ON_TOP_RIGHT.value]

        humanProbabilityModel = [0.635, 0.078, 0.074, 0.047, 0.166]

        if self.gazeCase == "contact_mode":
            dir = GazeDirection.LOOKING_ON_MIDDLE_MIDDLE.value
        if self.gazeCase == "aversion_mode":
            dir = np.random.choice(aversionList)
        if self.gazeCase == "human_gaze_mode":
            dir = np.random.choice(aversionList, p=humanProbabilityModel)
        print "gaze dir " + dir
        return LookAction(dir)



    def __parseStages(self, stagesJson):
        groups = []
        for group in stagesJson:
            stages = []
            for stage in group:
                startAction = Action.of(stage['startAction'])
                waitTime = stage['waitTime']
                stages.append((startAction, waitTime))
            groups.append(stages)
        return groups


if __name__ == '__main__':
    sc = ExperimentOneScenario("experiment_one_scenario_pl_android_tts.json")
    sc.shuffleGroups()
    while sc.hasNextStage():
        print sc.getNextStage()