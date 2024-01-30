import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import LineString, Polygon
import time
import sys

# Some settings for the PIL package
font = ImageFont.truetype("../fonts/RobotoMono-Bold.ttf", 30)

# Function for reccommanded path
def generate_nodes(lat_min, lat_max, lon_min, lon_max, spacing):
    """Generate a grid of nodes covering the golf course area."""
    latitudes = np.arange(lat_min, lat_max, spacing)
    longitudes = np.arange(lon_min, lon_max, spacing)
    return [(lat, lon) for lat in latitudes for lon in longitudes]

def path_intersects_obstacle(node1, node2, obstacles, terrain):
    """Check for intersection with obstacles and if the path is within the terrain."""
    path = LineString([node1, node2])
    for obstacle in obstacles:
        if path.intersects(Polygon(obstacle)):
            return True
    if not terrain.contains(path):
        return True
    return False

def calculate_recommended_path(start_coords, end_coords, nodes, obstacles, terrain):
    # Create a graph
    graph = nx.Graph()

    # Add nodes to the graph
    for node in nodes:
        graph.add_node(node)

    # Connect nodes in the graph, avoiding obstacles and considering the range limit
    max_range = max(golf_irons.values())  # Get the maximum range of the golf irons
    for i, node1 in enumerate(nodes):
        for node2 in nodes[i + 1:]:
            distance = calculate_distance(node1, node2)
            if not path_intersects_obstacle(node1, node2, obstacles, terrain) and distance <= max_range:
                # Add an edge with distance as weight
                graph.add_edge(node1, node2, weight=distance)

    # Compute the shortest path
    try:
        path = nx.shortest_path(graph, source=start_coords, target=end_coords, weight='weight')
    except nx.NetworkXNoPath:
        print("No path found")
        return [], []

    # Calculate iron recommendations for each segment
    iron_recommendations = []
    for i in range(len(path) - 1):
        segment_distance = calculate_distance(path[i], path[i + 1])
        recommended_iron = select_iron(segment_distance)
        iron_recommendations.append((path[i], path[i + 1], recommended_iron))

    return path, iron_recommendations

    

def haversine(coord1, coord2):
    """Calculate the great-circle distance between two points in meters."""
    # Radius of the Earth in meters
    R = 6371000  
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance

def calculate_distance(coord1, coord2):
    """Calculate the Haversine distance between two points."""
    return haversine(coord1, coord2)

class Node:
    def __init__(self, position):
        self.position = position

def lat_lon_to_image_coords(lat, lon, img_width, img_height, lat_min, lat_max, lon_min, lon_max):
    lat = (lat - lat_min) / (lat_max - lat_min)
    lon = (lon - lon_min) / (lon_max - lon_min)
    x = lon * img_width
    y = (1 - lat) * img_height
    return int(x), int(y)

def draw_start_end_points(draw, start_coords, end_coords, img_width, img_height):
    """Draw the start (tee) and end (hole) points."""
    start_x, start_y = lat_lon_to_image_coords(*start_coords, img_width, img_height, lat_min, lat_max, lon_min, lon_max)
    end_x, end_y = lat_lon_to_image_coords(*end_coords, img_width, img_height, lat_min, lat_max, lon_min, lon_max)
    
    # Draw start and end points
    draw.ellipse([(start_x - 10, start_y - 10), (start_x + 10, start_y + 10)], fill='green')  # Tee
    draw.ellipse([(end_x - 5, end_y - 5), (end_x + 5, end_y + 5)], fill='red')  # Hole

def draw_path(draw, path, img_width, img_height):
    """Draw the path and a circle at each node."""
    for i in range(len(path) - 1):
        start = lat_lon_to_image_coords(*path[i], img_width, img_height, lat_min, lat_max, lon_min, lon_max)
        end = lat_lon_to_image_coords(*path[i + 1], img_width, img_height, lat_min, lat_max, lon_min, lon_max)
        draw.line([start, end], fill='blue', width=2)
        draw.ellipse((start[0] - 5, start[1] - 5, start[0] + 5, start[1] + 5), fill='yellow')


def draw_obstacle(draw, obstacle_coords, color):
    image_coords = [lat_lon_to_image_coords(lat, lon, img_width, img_height, lat_min, lat_max, lon_min, lon_max)
                    for lat, lon in obstacle_coords]
    draw.polygon(image_coords, outline=color, fill=color)

def parse_obstacle_data(line):
    parts = line.split(',')
    color = parts[1]
    coords = [(float(parts[i]), float(parts[i + 1])) for i in range(2, len(parts), 2)]
    return coords, color

def annotate_path(draw, path, iron_recommendations, img_width, img_height):
    """Annotate the path with the recommended iron."""
    for (start, end, iron) in iron_recommendations:
        mid_point = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        mid_x, mid_y = lat_lon_to_image_coords(*mid_point, img_width, img_height, lat_min, lat_max, lon_min, lon_max)
        draw.text((mid_x, mid_y), f'{iron}', fill="white" , font=font)

# SETTINGS
golf_irons = {
    # 'Sand Wedge': 70,
    'Iron 9': 105,  
    'Iron 7': 128,
    'Driver 3': 190,
    'Putter': 10
}

def select_iron(distance):
    """Select the appropriate golf iron for a given distance."""
    for iron, max_range in golf_irons.items():
        if distance <= max_range:
            return iron
    return 'Iron 9'


# Main execution part
if __name__ == "__main__":
    print("#########################################################")
    print(r"""    
    ______               __       ____                              
   / ____/____ _ ____ _ / /___   / __ \ _____ ___   ____ _ ____ ___ 
  / __/  / __ `// __ `// // _ \ / / / // ___// _ \ / __ `// __ `__ \
 / /___ / /_/ // /_/ // //  __// /_/ // /   /  __// /_/ // / / / / /
/_____/ \__,_/ \__, //_/ \___//_____//_/    \___/ \__,_//_/ /_/ /_/ 
              /____/                                                                                    
    """)
    print("#########################################################")
    print("### 🏌️‍♂️  An Innovative Algorithm for Golf Strategies 🏌️‍♀️  ###")
    print("#########################################################\n")

    # Load your image
    img = Image.open("../images/hole4.png")
    draw = ImageDraw.Draw(img)

    # Define the geographical extent and image size
    lat_min, lat_max, lon_min, lon_max = 48.906378, 48.909397, 1.991191, 1.994474
    img_width, img_height = img.size

    print("-- Geographical extent --")
    print(f"lat_min = {lat_min}, lat_max = {lat_max}, lon_min = {lon_min}, lon_max = {lon_max}")
    print(f"img_width = {img_width}, img_height = {img_height}")
    print()

    # Define start (tee) and end (hole) points
    start_coords = (48.90891343931512, 1.9938896367494228)
    end_coords = (48.90665014147519, 1.991794617313395)

    # Print the distance in meters from Tee to Hole
    print("-- Distance from Tee to Hole --")
    print(calculate_distance(start_coords, end_coords) , " meters.")
    print()

    # Generate nodes
    # The value of spacing defines the distance between nodes,
    # more nodes we have, more accurate the path will be
    spacing = 0.0005
    nodes = generate_nodes(lat_min, lat_max, lon_min, lon_max, spacing)


    # Ensure start and end points are in nodes
    if start_coords not in nodes:
        nodes.append(start_coords)
    if end_coords not in nodes:
        nodes.append(end_coords)

    # Read and parse obstacles
    obstacles = []
    with open("../data/obstacles.txt", "r") as file:
        for line in file:
            coords, _ = parse_obstacle_data(line)
            obstacles.append(coords)
    
    print("-- Calculate recommended path --")
    # Read and parse terrain
    terrain = None
    with open("../data/terrain.txt", "r") as file:
        coords, _ = parse_obstacle_data(file.readline())
        terrain = Polygon(coords)

    # Calculate recommended path
    recommended_path, iron_recommendations = calculate_recommended_path(start_coords, end_coords, nodes, obstacles, terrain)

    for i, segment in enumerate(iron_recommendations, start=1):
        distance = calculate_distance(segment[0], segment[1])
        print(f"Shot {i}: Distance = {distance} meters, Use {segment[2]}")


    # Optionally, draw obstacles based on a flag
    draw_obstacles = True
    # draw_obstacles = False
    if draw_obstacles:
        with open("../data/obstacles.txt", "r") as file:
            for line in file:
                coords, color = parse_obstacle_data(line)
                draw_obstacle(draw, coords, color)

    # Draw start and end points, the recommended path, and a circle at each node
    draw_start_end_points(draw, start_coords, end_coords, img_width, img_height)
    draw_path(draw, recommended_path, img_width, img_height)

    #  Annotate the path with the recommended iron
    annotate_path(draw, recommended_path, iron_recommendations, img_width, img_height)

    # Save or display the modified image
    img.save("output.png")
    # img.show()

    print()
    print("#########################################################")
