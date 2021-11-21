
class Action(object):
    def run(self, nao_client):
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def of(actionJson):
        if actionJson is None:
            return EmptyAction()
        elif actionJson['type'] == 'say':
            return SayAction(actionJson['text'])
        elif actionJson['type'] == 'look':
            return LookAction(actionJson['dir'])
        elif actionJson['type'] == 'playSound':
            return PlaySoundAction(actionJson['path'], bool(actionJson['async']), actionJson['volume'])
        elif actionJson['type'] == 'playSoundAndAnimation':
            return PlaySoundAndAnimationAction(actionJson['path'], bool(actionJson['async']), actionJson['gestures'], actionJson['volume'])
        elif actionJson['type'] == 'sayOnAndroidAndPlayAnimationAction':
            return SayOnAndroidAndPlayAnimationAction(actionJson['text'], actionJson['gestures'])


class EmptyAction(Action):
    def run(self, nao_client):
        pass


class SayAction(Action):

    def __init__(self, text):
        self.text = text

    def run(self, pepper_client):
        pepper_client.say(self.text)


class LookAction(Action):

    def __init__(self, dir):
        self.dir = dir

    def run(self, pepper_client):
        pepper_client.lookInDir(self.dir)


class PlaySoundAction(Action):

    def __init__(self, path, async, volume):
        self.path = path
        self.async = async
        self.vol = volume

    def run(self, pepper_client):
        pepper_client.playSound(self.path, self.async, self.vol)

class PlaySoundAndAnimationAction(Action):

    def __init__(self, path, async, gestures, volume):
        self.path = path
        self.async = async
        self.gestures = gestures
        self.vol = volume

    def run(self, pepper_client):
        future, vol= pepper_client.playSound(self.path, self.async, self.vol)
        pepper_client.playAnimation(self.gestures)
        future.value()
        pepper_client.setSystemVolume(vol)

class SayOnAndroidAndPlayAnimationAction(Action):

    def __init__(self, text, gestures):
        self.text = text
        self.gestures = gestures

    def run(self, pepper_client):
        pepper_client.sayOnAndroid(self.text)
        pepper_client.playAnimation(self.gestures)
