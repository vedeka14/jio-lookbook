# metadata/compatibility.py

"""
Defines valid garment combinations.
If a category is in pair_with, they can be matched.
If a category is in avoid_pair_with, they must NEVER be matched.
"""

COMPATIBILITY_RULES = {
    "shirt": {
        "pair_with": ["jeans", "trousers", "shorts", "cargo", "pants", "skirt"],
        "avoid_pair_with": ["saree", "maxi", "dress", "lehenga", "anarkali", "swimsuit", "churidaar", "salwar", "palazzo"]
    },
    "t-shirt": {
        "pair_with": ["jeans", "trousers", "shorts", "cargo", "pants", "skirt"],
        "avoid_pair_with": ["saree", "maxi", "dress", "lehenga", "anarkali", "swimsuit", "churidaar", "salwar"]
    },
    "blouse": {
        "pair_with": ["saree", "lehenga", "skirt", "trousers", "palazzo"],
        "avoid_pair_with": ["shorts", "cargo", "swimsuit", "churidaar", "salwar"]
    },
    "kurti": {
        "pair_with": ["jeans", "leggings", "churidaar", "salwar", "palazzo", "pants"],
        "avoid_pair_with": ["saree", "shorts", "cargo", "swimsuit", "maxi", "dress"]
    },
    "kurta": {
        "pair_with": ["pajama", "churidaar", "jeans"],
        "avoid_pair_with": ["shorts", "swimsuit", "saree"]
    },
    # Full body items inherently avoid bottoms and tops
    "saree": {
        "pair_with": ["blouse"],
        "avoid_pair_with": ["shirt", "t-shirt", "kurti", "kurta", "jeans", "trousers", "shorts", "cargo", "pants", "leggings", "churidaar", "pajama", "salwar", "palazzo"]
    },
    "maxi": {
        "pair_with": ["scarf"],
        "avoid_pair_with": ["shirt", "t-shirt", "kurti", "kurta", "jeans", "trousers", "shorts", "cargo", "pants", "leggings", "churidaar", "pajama", "salwar", "palazzo"]
    },
    "dress": {
        "pair_with": [],
        "avoid_pair_with": ["shirt", "t-shirt", "kurti", "kurta", "jeans", "trousers", "shorts", "cargo", "pants", "leggings", "churidaar", "pajama", "salwar", "palazzo"]
    },
    "swimsuit": {
        "pair_with": ["cover up", "shrug"],
        "avoid_pair_with": ["shirt", "t-shirt", "kurti", "kurta", "jeans", "trousers", "cargo", "pants", "leggings", "churidaar", "pajama", "salwar", "palazzo"]
    }
}
