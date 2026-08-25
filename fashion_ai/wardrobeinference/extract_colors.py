import cv2
import math
import numpy as np

# ==================================================
# HSV Color Database (OpenCV Format: H:0-179, S:0-255, V:0-255)
# ==================================================
COLOR_DATABASE = {
    "Black": (0, 0, 40),
    "White": (0, 0, 255),
    "Grey": (0, 0, 140),

    "Red": (0, 255, 255),
    "Maroon": (175, 255, 120),

    "Orange": (15, 255, 255),
    "Coral": (10, 180, 255),

    "Yellow": (30, 255, 255),
    "Mustard": (25, 220, 180),
    "Gold": (22, 255, 200),

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
# Find Closest Color in Robust HSV Space
# ==================================================
def find_closest_color_hsv(h, s, v):
    best_color = None
    best_distance = float("inf")
    
    h, s, v = float(h), float(s), float(v)

    for color_name, (H, S, V) in COLOR_DATABASE.items():
        # Hue distance (circular, max 90)
        dh = min(abs(h - H), 180 - abs(h - H))
        dh_scaled = (dh / 90.0) * 255.0
        
        # If target is a neutral color (White, Black, Grey), Hue doesn't matter much
        if S < 50:
            # Heavily weight Saturation and Value
            distance = math.sqrt((s - S)**2 + ((v - V) * 1.5)**2)
            # Add a penalty if the fabric is highly saturated (it shouldn't match a neutral)
            if s > 80:
                distance += 500
        else:
            # Target is a colorful color. Heavily weight Hue!
            # Ignore Value (shadows/brightness) completely unless it's extremely dark
            distance = math.sqrt((dh_scaled * 2.0)**2 + ((s - S) * 0.5)**2)
            # Add a penalty if the fabric is totally desaturated (it shouldn't match a color)
            if s < 40:
                distance += 500

        if distance < best_distance:
            best_distance = distance
            best_color = color_name

    return best_color

# ==================================================
# Function Used by build_wardrobe_yolo.py
# ==================================================
def detect_color(crop):
    """
    Detect the dominant clothing color from a cropped BGR image using K-Means clustering.
    Takes a center crop to avoid background, then finds the most prominent color.
    """
    height, width = crop.shape[:2]
    
    # Take the center 50% of the image to focus on the clothing and ignore background/face
    cx, cy = width // 2, height // 2
    w_crop, h_crop = int(width * 0.5), int(height * 0.5)
    
    x1 = max(0, cx - w_crop // 2)
    y1 = max(0, cy - h_crop // 2)
    center_crop = crop[y1:y1+h_crop, x1:x1+w_crop]
    
    # Fallback if crop fails
    if center_crop.size == 0:
        center_crop = crop
        
    # Reshape for K-Means
    pixels = center_crop.reshape((-1, 3))
    pixels = np.float32(pixels)
    
    # Stop criteria for KMeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 2
    try:
        _, labels, centers = cv2.kmeans(pixels, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        counts = np.bincount(labels.flatten())
        dominant_bgr = centers[np.argmax(counts)]
        
        # Convert dominant BGR pixel back to HSV
        dominant_bgr_pixel = np.uint8([[dominant_bgr]])
        hsv_pixel = cv2.cvtColor(dominant_bgr_pixel, cv2.COLOR_BGR2HSV)[0][0]
        hue, saturation, value = hsv_pixel
        return find_closest_color_hsv(hue, saturation, value)
        
    except Exception:
        hsv = cv2.cvtColor(center_crop, cv2.COLOR_BGR2HSV)
        hue, saturation, value = hsv.mean(axis=(0, 1))
        return find_closest_color_hsv(hue, saturation, value)

if __name__ == "__main__":
    from extract_colors_owlvit import main
    main()
