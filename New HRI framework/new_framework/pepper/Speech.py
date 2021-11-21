class Speech(object):
    def __init__(self, session, configuration = {"bodyLanguageMode": "contextual"}):
        self.tts = session.service("ALAnimatedSpeech")
        self.configuration = configuration

    def say(self, text):
        print(text)
        self.tts.say(str(text), self.configuration)