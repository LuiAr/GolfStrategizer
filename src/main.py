import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse

# Define the classes for various course elements
class Tee:
    def __init__(self, position):
        self.position = position

class Hole:
    def __init__(self, position):
        self.position = position

class Green:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class Bunker:
    def __init__(self, vertices):
        self.vertices = vertices

class Lake:
    def __init__(self, center, width, height):
        self.center = center
        self.width = width
        self.height = height

class Node:
    def __init__(self, position):
        self.position = position

# GolfCourse class with all functionalities
class GolfCourse:
    def __init__(self, name, length, par, iron_7_range=80, iron_9_range=50):
        self.name = name
        self.length = length
        self.par = par
        self.tee = None
        self.hole = None
        self.green = None
        self.obstacles = []
        self.nodes = []
        self.graph = nx.Graph()
        self.iron_7_range = iron_7_range
        self.iron_9_range = iron_9_range

    def set_tee(self, tee):
        self.tee = tee

    def set_hole(self, hole):
        self.hole = hole

    def add_green(self, green):
        self.green = green

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def generate_nodes(self, node_spacing=1, safety_margin=5):
        x_range = np.arange(0, self.length, node_spacing)
        y_range = np.arange(0, self.length, node_spacing)
        for x in x_range:
            for y in y_range:
                point = (x, y)
                if self.is_point_safe(point, safety_margin):
                    self.nodes.append(Node(point))

    def is_point_safe(self, point, safety_margin):
        if self.green and np.hypot(point[0] - self.green.center[0], point[1] - self.green.center[1]) < self.green.radius:
            return False
        for obstacle in self.obstacles:
            if isinstance(obstacle, Lake):
                if np.hypot(point[0] - obstacle.center[0], point[1] - obstacle.center[1]) < (obstacle.width / 2 + safety_margin):
                    return False
            elif isinstance(obstacle, Bunker):
                bunker_center = np.mean(obstacle.vertices, axis=0)
                bunker_radius = np.hypot(obstacle.vertices[0][0] - obstacle.vertices[1][0], obstacle.vertices[0][1] - obstacle.vertices[1][1]) / 2
                if np.hypot(point[0] - bunker_center[0], point[1] - bunker_center[1]) < (bunker_radius + safety_margin):
                    return False
        return True

    def create_graph(self):
        for node in self.nodes:
            self.graph.add_node(node)
            for other_node in self.nodes:
                distance = np.hypot(node.position[0] - other_node.position[0], node.position[1] - other_node.position[1])
                if distance <= self.iron_7_range:
                    self.graph.add_edge(node, other_node, weight=1, club='Iron 7')
                elif distance <= self.iron_9_range:
                    self.graph.add_edge(node, other_node, weight=1, club='Iron 9')

    def find_best_path(self):
        start_node = min(self.nodes, key=lambda node: np.hypot(node.position[0] - self.tee.position[0], node.position[1] - self.tee.position[1]))
        end_node = min(self.nodes, key=lambda node: np.hypot(node.position[0] - self.hole.position[0], node.position[1] - self.hole.position[1]))
        path = nx.shortest_path(self.graph, source=start_node, target=end_node, weight='weight')
        return path

    def display_graphically(self, path=None):
        fig, ax = plt.subplots()
        if self.tee:
            ax.plot(*self.tee.position, 'go')
        if self.hole:
            ax.plot(*self.hole.position, 'ro')
        if self.green:
            green_circle = plt.Circle(self.green.center, self.green.radius, color='lightgreen', label='Green')
            ax.add_artist(green_circle)
        for obstacle in self.obstacles:
            if isinstance(obstacle, Lake):
                lake_patch = Ellipse(obstacle.center, obstacle.width, obstacle.height, color='blue', label='Lake')
                ax.add_patch(lake_patch)
            elif isinstance(obstacle, Bunker):
                bunker_patch = Polygon(obstacle.vertices, color='sandybrown', label='Bunker')
                ax.add_patch(bunker_patch)
        if path:
            for node in path:
                ax.plot(*node.position, 'b.', markersize=1)
            path_positions = [node.position for node in path]
            ax.plot(*zip(*path_positions), color='black')
        ax.set_title(f"{self.name} (Par {self.par})")
        plt.xlabel('Distance in meters')
        plt.ylabel('Distance in meters')
        plt.grid(True)
        plt.legend()
        plt.show()

# Example usage
course = GolfCourse("Ilbarritz Trou 1", 100, 3)
course.set_tee(Tee((5, 5)))
course.set_hole(Hole((90, 90)))

print("> Adding obstacles ...")
# Adding bunkers and a lake
course.add_obstacle(Bunker([(56, 66), (45,51), (64, 47) , (63, 57)]))
course.add_obstacle(Lake(center=(40, 20), width=25, height=10))
print("Done.")

# Setting the green around the hole
course.add_green(Green(center=(90, 90), radius=2))
# Display the course
course.display_graphically()

print("> Generating nodes and creating the graph ...")
# Generating nodes and creating the graph
course.generate_nodes(node_spacing=1, safety_margin=5)
course.create_graph()
print("Done.")

print("> Finding best path ...")
# Finding the best path
best_path = course.find_best_path()
print("Done.")

print("- DISPLAY -")
# Displaying the course with the best path
course.display_graphically(best_path)
