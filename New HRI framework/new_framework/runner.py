import datetime
import errno
import os

from config.ConfigReader import ConfigReader
from scenarios.ScenarioEngine import ScenarioEngine



scenario_path = "./scenarios/scenarioFiles/question_det_test.json"
config_path = "./config/platform/avatar.json"


ip = '192.168.0.103'
port = '9559'
experimentName = 'idMJ'


class Runner(object):
    def main(self, common_obj):
        now = datetime.datetime.now()
        directory = "results/" + str(now).replace(" ", "") + experimentName
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        common_obj["options"]['directory'] = directory

        scenarioControler = ScenarioEngine( scenario_path, common_obj)
        scenarioControler.run()



if __name__ == "__main__":
    config_reader = ConfigReader()
    common_obj = config_reader.loadConfig(config_path)
    if ip:
        common_obj["options"]["ip"] = ip
    if port:
        common_obj["options"]["port"] = port
    if experimentName:
        common_obj["options"]["experimentName"] = experimentName

    config_reader.create_robot_client(common_obj)
    runner = Runner()
    runner.main(common_obj)