from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

import qi
import sys
import datetime
import errno
import os

from scenario.ScenarioControler import ScenarioControler
from utils.DownloadData import DownloadData

ip = '192.168.1.100'
port = '9559'
# scenarioPath = "./scenario/experiment_one_scenario_pl_android_tts.json"
scenarioPath = "./scenario/experiment_one_scenario_pl_android_tts_short.json"
# scenarioPath = "./scenario/experiment_one_scenario_pl_audio_short.json"

experimentName = 'exp1'

options = {'gesturesEnabled': True,'SpeechToTextEnabled': False, 'gazeCase': None, 'SpeechToTextAndroid': False, 'experimentName': experimentName}



class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 3
        self.add_widget(Label(text='User id'))
        self.userid = TextInput(multiline=False)
        self.runButton = Button(text='run')
        self.text = ''
        self.userid.bind(text=self.setText)
        self.runButton.bind(on_press=self.run)
        self.add_widget(self.userid)
        self.add_widget(self.runButton)

    def setText(self, textHandler, text):
        self.text = text

    def run(self, button):
        experimentName = self.text
        options['experimentName'] = experimentName
        session = qi.Session()
        try:
            session.connect("tcp://" + ip + ":" + port)
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + ip + "\" on port " + port + ".\n"
                                                                                   "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)

        now = datetime.datetime.now()
        directory = "results/" + str(now).replace(" ", "") + experimentName
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        options['directory'] = directory
        scenarioControler = ScenarioControler(session, scenarioPath, options)
        scenarioControler.run()

        download = DownloadData(directory, experimentName)
        download.download()
        download.close()


class MyApp(App):

    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    MyApp().run()
