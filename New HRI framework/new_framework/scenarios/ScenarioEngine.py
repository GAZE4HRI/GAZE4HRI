from threading import Thread
from time import sleep

from ScenarioReader import ScenarioReader
from nodes.Node import SyncNode, ParallelNode, LoopNode


class ScenarioEngine():
    def __init__(self, scenario_path, common_obj):
        scenario_reader = ScenarioReader()
        self.scenario = scenario_reader.loadScenario(scenario_path)
        self.common_obj = common_obj


    def run(self):
        node = self.scenario.current_node

        while self.scenario.has_next_node():
            self.scenario.set_current_node(node)
            self.common_obj["options"]["current_node"] = node
            node.run(self)
            while not node.end_rule_passed(self.common_obj):
                sleep(0.1)

            successors = self.scenario.get_successors()
            passing_parallel_successors = []
            passing_sync_successors = []

            if len(successors) < 0:
                break

            for successor in successors:
                if successor.start_rule_passed(self.common_obj):
                    if type(successor) == SyncNode or type(successor) == LoopNode:
                        passing_sync_successors.append(successor)
                    elif type(successor) == ParallelNode:
                        passing_parallel_successors.append(successor)

            for node in passing_parallel_successors:
                thread = Thread(target=node.run, args=(self, ))
                thread.start()
                self.common_obj[node.name] = thread

            if len(passing_sync_successors) > 0:
                node = passing_sync_successors[0]

