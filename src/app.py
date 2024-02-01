import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import LineString, Polygon
import cv2
import time
import sys

# Import the function GoogleMapDownloader to download high res maps
from GoogleMapDownloader import GoogleMapDownloader, GoogleMapsLayers

# Import function to get the predictions on the image
from visionModel import getPredictionJson, getPredictionLabels

# Some settings for the PIL package
font = ImageFont.truetype("../fonts/RobotoMono-Bold.ttf", 30)

# Don't mind this 🤡
global golf_irons 

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
                graph.add_edge(node1, node2, weight=distance)

    # Compute the shortest path
    try:
        path = nx.shortest_path(graph, source=start_coords, target=end_coords, weight='weight')
    except nx.NetworkXNoPath:
        print("No path found")
        return [], []

    # Calculate iron recommendations for each segment, considering the rule for 'Driver 3'
    iron_recommendations = []
    for i, (start, end) in enumerate(zip(path[:-1], path[1:])):
        segment_distance = calculate_distance(start, end)
        is_first_shot = (i == 0)  # Check if it's the first shot
        recommended_iron = select_iron(segment_distance, is_first_shot)
        iron_recommendations.append((start, end, recommended_iron))

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
    if line.strip(): 
        parts = line.split(',')
        color = parts[1]
        coords = [(float(parts[i]), float(parts[i + 1])) for i in range(2, len(parts), 2)]
        return coords, color
    return [], None 

def annotate_path(draw, path, iron_recommendations, img_width, img_height):
    """Annotate the path with the recommended iron."""
    for (start, end, iron) in iron_recommendations:
        mid_point = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        mid_x, mid_y = lat_lon_to_image_coords(*mid_point, img_width, img_height, lat_min, lat_max, lon_min, lon_max)
        draw.text((mid_x, mid_y), f'{iron}', fill="white" , font=font)


def select_iron(distance, is_first_shot):
    """Select the appropriate golf iron for a given distance, considering usage rules."""
    # Exclude 'Driver 3' if it's not the first shot
    available_irons = {k: v for k, v in golf_irons.items() if not (k == 'Driver 3' and not is_first_shot)}
    
    for iron, max_range in sorted(available_irons.items(), key=lambda item: item[1], reverse=True):
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

    """
    SETTINGS
    """

    print("Select version: \n- 1. Golf de Béthemont \n- 2. Golf d'Ilbarritz")
    input_version = input("Version: ")
    # Defined to setp multiple version to test with differents golfs
    if input_version == "1": 
        print("\n---- Golf de Béthemont ----")
        # Define start (tee) and end (hole) points
        start_coords = (48.90891343931512, 1.9938896367494228)
        end_coords = (48.90665014147519, 1.991794617313395)
        # Define the threshold for the prediction
        value_threshold = 60
        # Define the golf irons
        golf_irons = {
            'Iron 9': 105,  
            'Iron 7': 128,
            'Driver 3': 190,
        }
        # Define the files to store all the obstacles (until the model is 100% accurate)
        obstacles_file = "../data/obstacles.txt"
        terrain_file = "../data/terrain.txt"
    elif input_version == "2":
        print("\n---- Golf d'Ilbarritz ----")
        start_coords = (43.46049913636801, -1.5757732009295526)
        end_coords = (43.46042123600998, -1.5719332568242161)
        value_threshold = 30
        golf_irons = {
            'Iron 9': 90,  
            'Iron 7': 130,
            'Driver 3': 190,
        }
        obstacles_file = "../data-ilbarritz/obstacles.txt"
        terrain_file = "../data-ilbarritz/terrain.txt"
    else:
        print("Invalid input")
        sys.exit()

    """
    SETTINGS
    """

    # Calculate the center point
    LAT_center_point = (start_coords[0] + end_coords[0]) / 2
    LNG_center_point = (start_coords[1] + end_coords[1]) / 2

    # Use the GoogleMapDownloader
    gmd = GoogleMapDownloader(LAT_center_point, LNG_center_point, 19, GoogleMapsLayers.SATELLITE)

    # Load your image
    img = gmd.generateImage()
    draw = ImageDraw.Draw(img)

    # Save image
    img_path = "output/image.png"
    img.save(img_path)

    # Show the prediction on the image (the returned image is a cv2 image)
    img_with_labels = getPredictionLabels(img_path, threshold=value_threshold)
    # Save the image
    cv2.imwrite("output/image_with_labels.png", img_with_labels)

    # Define the geographical extent and image size
    corners = gmd.get_corner_lat_lons()

    lat_min = corners["bottom_left"][0]
    lon_min = corners["bottom_left"][1]

    lat_max = corners["top_right"][0]
    lon_max = corners["top_right"][1]
    
    img_width, img_height = img.size

    print("-- Geographical extent --")
    print(f"lat_min = {lat_min}, lat_max = {lat_max}, lon_min = {lon_min}, lon_max = {lon_max}")
    print(f"img_width = {img_width}, img_height = {img_height}")
    print()

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
    with open(obstacles_file, "r") as file:
        for line in file:
            coords, _ = parse_obstacle_data(line)
            if coords:  # Check if coords is not empty
                obstacles.append(coords)

    # Initialize terrain with a default value if no data is provided
    default_terrain_coords = [(lat_min, lon_min), (lat_min, lon_max), (lat_max, lon_max), (lat_max, lon_min)]
    terrain = Polygon(default_terrain_coords)  # Default terrain that covers the entire area

    with open(terrain_file, "r") as file:
        line = file.readline()
        coords, _ = parse_obstacle_data(line)
        if coords:  # Check if coords is not empty
            terrain = Polygon(coords)
    
    print("-- Calculate recommended path --")
    # Calculate recommended path
    recommended_path, iron_recommendations = calculate_recommended_path(start_coords, end_coords, nodes, obstacles, terrain)

    for i, segment in enumerate(iron_recommendations, start=1):
        distance = calculate_distance(segment[0], segment[1])
        print(f"Shot {i}: Distance = {distance} meters, Use {segment[2]}")


    # Optionally, draw obstacles based on a flag
    draw_obstacles = False
    if draw_obstacles:
        with open(obstacles_file, "r") as file:
            for line in file:
                coords, color = parse_obstacle_data(line)
                draw_obstacle(draw, coords, color)

    # Draw start and end points, the recommended path, and a circle at each node
    draw_start_end_points(draw, start_coords, end_coords, img_width, img_height)
    draw_path(draw, recommended_path, img_width, img_height)

    #  Annotate the path with the recommended iron
    annotate_path(draw, recommended_path, iron_recommendations, img_width, img_height)

    # Save or display the modified image
    img.save("output/image_with_path.png")

    print("\n#")
    print("All files saved to the output folder !")
    print()
    print("#########################################################")
