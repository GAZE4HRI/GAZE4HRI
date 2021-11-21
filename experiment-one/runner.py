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
# scenarioPath = "./scenario/experiment_one_new_scenario_pl_android_tts.json"
# scenarioPath = "./scenario/experiment_one_scenario_pl_android_tts_short.json"
scenarioPath = "./scenario/conference_demo.json"
# scenarioPath = "./scenario/interwiew_demo.json"
experimentName = 'idMJ'

options = {'gesturesEnabled': True,'SpeechToTextEnabled': False,
           'gazeCase': "contact_mode", 'SpeechToTextAndroid': False,

           'experimentName': experimentName, 'pepperIP': ip, 'humanTracking': 'half',
           'debugMode': True}

def main(session):
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

    # download = DownloadData(directory, experimentName)
    # download.download()
    # download.close()


if __name__ == "__main__":
    session = qi.Session()
    try:
        session.connect("tcp://" + ip + ":" + port)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + ip + "\" on port " + port +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)