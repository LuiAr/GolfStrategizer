from roboflow import Roboflow
import cv2
import numpy as np

global KEY
KEY = "uTfTNz7djrhMOSOWLZjN"

def getPredictionJson(path, threshold=70):
    # instantiate the Roboflow API
    rf = Roboflow(api_key=KEY)

    # get the model
    project = rf.workspace("private-qp21p").project("golfsegmentation")
    model = project.version(1).model # First version of the model

    # infer on the image
    predictions = model.predict(path, confidence=threshold).json()

    return predictions


def getPredictionLabels(path, threshold=0.7):
    # instantiate the Roboflow API
    rf = Roboflow(api_key=KEY)

    # get the model
    project = rf.workspace("private-qp21p").project("golfsegmentation")
    model = project.version(1).model # First version of the model

    # infer on the image
    predictions = model.predict(path, confidence=threshold).json()

    # Define specific colors for each class label
    class_colors = {
        "bunker": (0, 255, 0),     # Green
        "green": (255, 0, 0),      # Red
        "fairway": (0, 0, 255),    # Blue
    }

    image = cv2.imread(path)

    if image is None:
        print("Image not found. Please check the path.")
    else:
        # Iterate through each prediction to draw polygons based on "points" and add labels
        for pred in predictions['predictions']:
            # Extract polygon points
            pts = np.array([[point['x'], point['y']] for point in pred['points']], np.int32)
            pts = pts.reshape((-1, 1, 2))  

            # Draw polygon using the color mapped to the class
            class_label = pred['class'] 
            color = class_colors.get(class_label, (255, 255, 255))  # Default to white if class not found
            cv2.polylines(image, [pts], isClosed=True, color=color, thickness=2)

            # Put the label of the prediction
            x, y = pts[0][0] 
            cv2.putText(image, class_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Convert BGR to RGB for displaying with matplotlib
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        return image_rgb