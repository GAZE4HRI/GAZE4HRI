import json

import networkx as nx

from nodes.Node import Node


class ScenarioReader():
    def loadScenario(self, path):
        config = json.load(open(path))
        graph = self.parse_graph(config['root'])
        return Scenario(graph)

    def parse_graph(self, graph_json):
        graph = nx.DiGraph()
        children = graph_json["children"]
        parsed_children = []
        if len(children) > 0:
            for child in children:
                parsed_children.append(self.parse_graph(child))
        else:
            node = Node.of(graph_json)
            graph.add_node(node)
            return (node, graph)

        node = Node.of(graph_json)
        graph.add_node(node)
        for child in parsed_children:
            graph = nx.compose(graph, child[1])
            graph.add_edge(node, child[0])
        return (node, graph)


class Scenario(object):
    def __init__(self, graph):
        self.current_node, self.graph = graph
        self.performed_nodes = 0

    def set_current_node(self, node):
        self.current_node = node

    def get_successors(self):
        return list(self.graph.successors(self.current_node))
        # return stage

    def has_next_node(self):
        return len(list(self.graph.neighbors(self.current_node))) > 0

    def get_node(self, i):
        return self.graph[i]


if __name__ == '__main__':

    sr = ScenarioReader()
    sc = sr.loadScenario("scenarios/scenarioFiles/question_det_test.json")
    print sc.has_next_node()
    print sc.graph.number_of_nodes()
    print sc.graph.number_of_edges()
    print list(sc.graph.nodes)
    print list(sc.graph.edges)
    print sc.current_node
    print list(sc.graph.successors(sc.current_node))
    print sc.set_current_node(list(sc.graph.successors(list(sc.graph.successors(list(sc.graph.successors(sc.current_node))[1]))[0]))[0])
    print sc.has_next_node()