import threading
from threading import currentThread

import time

from actions.Action import Action
from utils.Constants import EventType


class Node(object):
    def run(self, scenario_engine):
        raise NotImplementedError("Should have implemented this")

    def start_rule_passed(self, common_obj):
        raise NotImplementedError("Should have implemented this")

    def end_rule_passed(self, common_obj):
        raise NotImplementedError("Should have implemented this")

    def on_event(self, type):
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def of(node_json):
        if node_json is None:
            return EmptyNode()
        if node_json["type"] == "sync":
            return SyncNode(node_json["start_rule"], node_json["end_rule"],  node_json["actions"], node_json["events"])
        if node_json["type"] == "loop":
            return LoopNode(node_json["start_rule"], node_json["end_rule"],  node_json["actions"], node_json["events"] )
        if node_json["type"] == "parallel":
            return ParallelNode(node_json["start_rule"], node_json["end_rule"],  node_json["actions"], node_json["name"], node_json["events"] )


class EmptyNode(Node):
    def run(self, nao_client):
        pass


def parse_actions(actions):
    stages = []
    for stage in actions:
        action = Action.of(stage['Action'])
        stages.append(action)
    return stages

def parse_events(events):
    stages = []
    for stage in events:
        event = Event.of(stage['Event'])
        stages.append(event)
    return stages

class SyncNode(Node):
    def __init__(self, start_rule, end_rule, actions, events):
        self.start_rule = start_rule
        self.end_rule = end_rule
        self.actions = parse_actions(actions)
        self.events = parse_events(events)
        self.common_obj = None
        self.lock = threading.Lock()



    def end_rule_passed(self, common_obj):
        return eval(self.end_rule,  {"common_obj": common_obj, "options": common_obj["options"].get, "always": always, "child_ready": child_ready})

    def start_rule_passed(self, common_obj):
        return eval(self.start_rule, {"common_obj": common_obj, "options": common_obj["options"].get, "always": always, "child_ready": child_ready})

    def on_event(self, data):
        print "event"
        print type
        print self.events
        for e in self.events:
            if e.data == data:
                self.lock.acquire()
                e.run(self.common_obj)
                self.lock.release()
                print "event"
                time.sleep(0.1)

    def run(self, scenario_engine):
        print self.events

        self.common_obj = scenario_engine.common_obj
        self.common_obj["options"]["interrupt_lock"] = self.lock
        if self.common_obj.get("Analyser", None):
            for e in self.events:
                self.common_obj["Analyser"].add_event_to_lissen(e.data)
        for action in self.actions:
            self.lock.acquire()
            action.run(scenario_engine.common_obj)
            self.lock.release()
            time.sleep(0.01)
        if self.common_obj.get("Analyser", None):
            for e in self.events:
                self.common_obj["Analyser"].remove_event_to_lissen(e.data)

class LoopNode(Node):
    def __init__(self, start_rule, end_rule, actions, events):
        self.start_rule = start_rule
        self.end_rule = end_rule
        self.actions = parse_actions(actions)
        self.events = parse_events(events)
        self.common_obj = None
        self.lock = threading.Lock()

    def end_rule_passed(self, common_obj):
        return eval(self.end_rule,  {"common_obj": common_obj,
                                     "options": common_obj["options"].get,
                                     "always": always,
                                     "child_ready": child_ready,
                                     "now": time.time(),
                                     "start": self.start,
                                     "clicked": common_obj["click"].is_clicked()})

    def start_rule_passed(self, common_obj):
        return eval(self.start_rule, {"common_obj": common_obj,
                                      "options": common_obj["options"].get,
                                      "always": always,
                                      "child_ready": child_ready})

    def on_event(self, type):

        for e in self.events:
            if e.type == type:
                self.lock.acquire()
                e.run()
                self.lock.release()

    def run(self, scenario_engine):
        print self.actions
        self.common_obj = scenario_engine.common_obj
        self.start = time.time()
        while not self.end_rule_passed(scenario_engine.common_obj):
            for action in self.actions:
                self.lock.acquire()
                action.run(scenario_engine.common_obj)
                self.lock.release()
                time.sleep(0.01)


class ParallelNode(Node):
    def __init__(self, start_rule, end_rule, actions, name, events):
        self.start_rule = start_rule
        self.end_rule = end_rule
        self.actions = parse_actions(actions)
        self.name = name
        self.events = parse_events(events)
        self.common_obj = None
        self.lock = threading.Lock()

    def end_rule_passed(self, common_obj):
        return eval(self.end_rule,  {"common_obj": common_obj, "options": common_obj["options"].get, "always": always, "child_ready": child_ready})

    def start_rule_passed(self, common_obj):
        return eval(self.start_rule,  {"common_obj": common_obj, "options": common_obj["options"].get, "always": always, "child_ready": child_ready})

    def on_event(self, type):
        for e in self.events:
            if e.type == type:
                self.lock.acquire()
                e.run()
                self.lock.release()

    def run(self, scenario_engine):
        print self.actions
        self.common_obj = scenario_engine.common_obj
        t = currentThread()
        while getattr(t, "do_run", True):
            for action in self.actions:
                self.lock.acquire()
                action.run(scenario_engine.common_obj)
                self.lock.release()
                time.sleep(0.01)

def always():
    return True


def child_ready():
    return True


def options(val):
    global common_obj
    return common_obj["options"].get(val, False)





class Event(object):
    def run(self, common_obj):
        raise NotImplementedError("Should have implemented this")
    @staticmethod
    def of(event_json):
        if event_json is None:
            return EmptyEvent()
        if event_json["type"] == EventType.GAZE_AVERTING.value:
            return SimpleEvent(EventType.GAZE_AVERTING, event_json["separation"], event_json["value"], event_json["actions"])
        if event_json["type"] == EventType.Emotion_OCCURRED.value:
            return SimpleEvent(EventType.Emotion_OCCURRED, event_json["separation"], event_json["value"], event_json["actions"])
        if event_json["type"] == EventType.QUESTION_DETECTED.value:
            return SimpleEvent(EventType.QUESTION_DETECTED, event_json["separation"], event_json["value"], event_json["actions"])
        if event_json["type"] == EventType.SILENCE_DETECTED.value:
            return SimpleEvent(EventType.SILENCE_DETECTED, event_json["separation"], event_json["value"], event_json["actions"])


class EmptyEvent(Event):
    def run(self, common_obj):
        pass


class SimpleEvent(Event):
    def __init__(self, type, separation, value,  actions):
        self.type = type
        self.data = {"type": type, "separation": separation, "value": value}
        self.actions = parse_actions(actions)

    def run(self, common_obj):
        print self.actions
        for action in self.actions:
            action.run(common_obj)
