# metadata/templates.py

"""
Defines required and optional slots for different occasions.
"""

OUTFIT_TEMPLATES = {
    "office": {
        "required": ["top", "bottom", "footwear"],
        "optional": ["accessory", "outerwear"]
    },
    "casual friday": {
        "required": ["top", "bottom", "footwear"],
        "optional": ["accessory", "outerwear"]
    },
    "cafe": {
        "required": ["top", "bottom", "footwear"],
        "optional": ["accessory", "outerwear"]
    },

    "party": {
         "required_options": [
                    ["top", "bottom", "footwear"],
                    ["full_body", "footwear"]
                ],
        "optional": ["accessory", "outerwear"]
    },
    "wedding": {
        # Can be top+bottom or full_body, we will handle this via logic OR
        "required_options": [
            ["top", "bottom", "footwear"],
            ["full_body", "footwear"]
        ],
        "optional": ["accessory", "outerwear"]
    },
    "travel": {
         "required_options": [
                    ["top", "bottom", "footwear"],
                    ["full_body", "footwear"]
                ],
        "optional": ["accessory", "outerwear"]
    },
    "beach": {
        "required_options": [
            ["top", "bottom", "footwear"],
            ["full_body", "footwear"]
        ],
        "optional": ["accessory", "outerwear"]
    },
    "cold destination (manali)": {
        "required": ["top", "bottom", "outerwear", "footwear"],
        "optional": ["accessory"]
    },
    "everyday / casual day": {
        "required": ["top", "bottom", "footwear"],
        "optional": ["accessory", "outerwear"]
    },
    # Default generic
    "default": {
        "required_options": [
            ["top", "bottom", "footwear"],
            ["full_body", "footwear"]
        ],
        "optional": ["accessory", "outerwear"]
    }
}
