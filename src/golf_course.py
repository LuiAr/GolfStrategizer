import networkx as nx

class GolfCourse:
    def __init__(self):
        self.graph = nx.Graph()
        self.positions = {}  # Pour stocker les positions pour la visualisation

    def add_tee(self, tee_id, position):
        self.graph.add_node(tee_id, type='tee', position=position)
        self.positions[tee_id] = position

    def add_hole(self, hole_id, position):
        self.graph.add_node(hole_id, type='hole', position=position)
        self.positions[hole_id] = position

    def add_obstacle(self, obstacle_id, position, obstacle_type):
        self.graph.add_node(obstacle_id, type=obstacle_type, position=position)
        self.positions[obstacle_id] = position

    def add_shot(self, from_id, to_id, difficulty):
        self.graph.add_edge(from_id, to_id, weight=difficulty)
