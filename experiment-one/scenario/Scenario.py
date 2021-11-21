


class Scenario(object):
    def getNumberOfStages(self):
        raise NotImplementedError("Should have implemented this")

    def getGreeting(self):
        raise NotImplementedError("Should have implemented this")

    def getStage(self, i):
        raise NotImplementedError("Should have implemented this")

    def loadScenario(self, path):
        raise NotImplementedError("Should have implemented this")

    def getGoodbye(self):
        raise NotImplementedError("Should have implemented this")

    def getNextStage(self):
        raise NotImplementedError("Should have implemented this")

    def hasNextStage(self):
        raise NotImplementedError("Should have implemented this")