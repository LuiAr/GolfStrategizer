"""Very lightweight vision utilities used by app.py."""

from PIL import Image
import cv2
import numpy as np


def getPredictionJson(image_path, threshold=0):
    """Return an empty dict as a placeholder for future model predictions."""
    return {}


def getPredictionLabels(image_path, threshold=500):
    """Perform a naive blue color segmentation and draw contours.

    Parameters
    ----------
    image_path: str
        Path to the image on which to run the segmentation.
    threshold: int, optional
        Minimum contour area (in pixels) to be drawn.  This keeps the
        output relatively clean.

    Returns
    -------
    numpy.ndarray
        The annotated image in OpenCV's BGR format.
    """

    image = cv2.imread(image_path)
    if image is None:
        # Fallback: return the raw image opened with PIL
        return np.array(Image.open(image_path))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) >= threshold:
            cv2.drawContours(image, [cnt], -1, (0, 0, 255), 2)

    return image
