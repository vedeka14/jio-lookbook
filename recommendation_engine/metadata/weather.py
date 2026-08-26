# metadata/weather.py

"""
Defines weather profiles and their constraints.
"""

WEATHER_PROFILES = {
    "hot": {
        "avoid": ["wool", "heavy_jacket", "sweater", "jacket", "hoodie", "blazer", "coat", "boots"],
        "prefer": ["linen", "cotton", "shorts", "sandals", "flip flops", "t-shirt", "skirt"]
    },
    "cold": {
        "avoid": ["shorts", "sandals", "flip flops", "swimsuit"],
        "prefer": ["wool", "jacket", "sweater", "hoodie", "blazer", "boots"]
    },
    "warm": {
        "avoid": ["wool", "heavy_jacket", "boots"],
        "prefer": ["cotton", "linen"]
    },
    "rainy": {
        "avoid": ["suede", "white", "sandals"],
        "prefer": ["waterproof", "boots", "dark"]
    }
}
