import cv2
import math

# ==================================================
# HSV Color Database
# ==================================================
COLOR_DATABASE = {
    "Black": (0, 0, 20),
    "White": (0, 0, 255),
    "Grey": (0, 0, 140),

    "Red": (0, 255, 255),
    "Maroon": (175, 255, 120),

    "Orange": (15, 255, 255),
    "Coral": (10, 180, 255),

    "Yellow": (30, 255, 255),
    "Mustard": (25, 220, 180),

    "Green": (60, 255, 255),
    "Olive": (45, 180, 120),
    "Mint": (55, 120, 255),

    "Cyan": (90, 255, 255),
    "Teal": (90, 180, 180),

    "Blue": (120, 255, 255),
    "Sky Blue": (105, 120, 255),
    "Navy": (120, 255, 100),

    "Purple": (145, 255, 180),
    "Lavender": (145, 80, 255),

    "Pink": (170, 120, 255),

    "Brown": (15, 180, 120),
    "Beige": (20, 50, 220),
    "Cream": (25, 30, 255)
}


# ==================================================
# Find Closest Color
# ==================================================
def find_closest_color(h, s, v):
    best_color = None
    best_distance = float("inf")

    for color_name, (H, S, V) in COLOR_DATABASE.items():
        distance = math.sqrt(
            (h - H) ** 2 +
            (s - S) ** 2 +
            (v - V) ** 2
        )

        if distance < best_distance:
            best_distance = distance
            best_color = color_name

    return best_color


# ==================================================
# Function Used by build_wardrobe_yolo.py and color_detection_lab.py
# ==================================================
def detect_color(crop):
    """
    Detect the dominant clothing color from a cropped BGR image.
    """

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    hue, saturation, value = hsv.mean(axis=(0, 1))

    return find_closest_color(hue, saturation, value)
