from PIL import Image


def getPredictionJson(image_path, threshold=0):
    """Return an empty dict as a placeholder for future model predictions."""
    return {}


def getPredictionLabels(image_path, threshold=0):
    """Return the image opened with PIL as a placeholder for labeled output."""
    return Image.open(image_path)
