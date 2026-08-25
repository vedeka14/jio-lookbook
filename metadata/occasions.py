# metadata/occasions.py

"""
Defines occasions and their styling constraints.
"""

OCCASIONS = {
    "office": {
        "preferred_styles": ["minimal", "old_money", "traditional"],
        "preferred_weather": ["all"],
        "avoid_items": ["shorts", "swimsuit", "flip flops", "sandals", "cargo"]
    },
    "casual friday": {
        "preferred_styles": ["casual", "minimal", "streetwear"],
        "preferred_weather": ["all"],
        "avoid_items": ["swimsuit", "flip flops", "saree", "lehenga", "anarkali", "sherwani"]
    },
    "cafe": {
        "preferred_styles": ["casual", "minimal", "boho", "streetwear"],
        "preferred_weather": ["all"],
        "avoid_items": ["swimsuit", "formal", "saree", "lehenga", "anarkali", "sherwani", "kurta"]
    },
    "party": {
        "preferred_styles": ["streetwear", "minimal", "casual", "boho", "traditional"],
        "preferred_weather": ["all"],
        "avoid_items": ["swimsuit", "flip flops", "kurta", "kurti", "saree", "churidaar", "salwar", "lehenga"]
    },
    "wedding": {
        "preferred_styles": ["traditional"],
        "preferred_weather": ["all"],
        "avoid_items": ["shorts", "swimsuit", "flip flops", "t-shirt", "jeans", "cargo"]
    },
    "travel": {
        "preferred_styles": ["casual", "streetwear", "minimal","traditional","old_money"],
        "preferred_weather": ["all"],
        "avoid_items": ["saree", "lehenga", "heels", "swimsuit"]
    },
    "beach": {
        "preferred_styles": ["casual", "boho"],
        "preferred_weather": ["hot", "warm"],
        "avoid_items": ["boots", "jacket", "sweater", "blazer", "saree", "lehenga", "jeans", "trousers"]
    },
    "everyday / casual day": {
        "preferred_styles": ["casual", "minimal", "streetwear", "boho"],
        "preferred_weather": ["all"],
        "avoid_items": ["swimsuit", "heels", "lehenga", "saree", "anarkali", "sherwani"]
    }
}
