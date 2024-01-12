import networkx as nx
import matplotlib.pyplot as plt

def find_best_path(graph, source, target):
    try:
        path = nx.dijkstra_path(graph, source, target, weight='weight')
        return path
    except nx.NetworkXNoPath:
        return "Aucun chemin possible"

    # Note: 'weight' dans dijkstra_path représente l'attribut à considérer pour le calcul du coût.
    # Dans notre cas, il pourrait s'agir de la difficulté du coup.


def visualize_course(golf_course):
    # Dessiner les nœuds
    for node, data in golf_course.graph.nodes(data=True):
        if data['type'] == 'tee':
            nx.draw_networkx_nodes(golf_course.graph, golf_course.positions, nodelist=[node], node_color='green')
        elif data['type'] == 'hole':
            nx.draw_networkx_nodes(golf_course.graph, golf_course.positions, nodelist=[node], node_color='red')
        elif data['type'] == 'tree':
            nx.draw_networkx_nodes(golf_course.graph, golf_course.positions, nodelist=[node], node_color='brown')
        elif data['type'] == 'bunker':
            nx.draw_networkx_nodes(golf_course.graph, golf_course.positions, nodelist=[node], node_shape='s')
        elif data['type'] == 'water':
            nx.draw_networkx_nodes(golf_course.graph, golf_course.positions, nodelist=[node], node_color='blue', node_shape='s')
    
    # Dessiner les arêtes
    nx.draw_networkx_edges(golf_course.graph, golf_course.positions)

    # Dessiner les étiquettes
    nx.draw_networkx_labels(golf_course.graph, golf_course.positions)

    plt.show()
