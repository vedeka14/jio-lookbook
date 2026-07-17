import json


def build_ajio_query(missing_items, preferred_colors):
    """
    Build a privacy-safe query.

    This is the ONLY information that would be sent to AJIO.
    No user photos, OCR text, or wardrobe images are included.
    """

    query = []

    for category in missing_items:
        query.append({
            "category": category.title(),
            "preferred_colors": sorted(preferred_colors)
        })

    return query


def save_query(query, output_file):
    """
    Save the privacy-safe query.
    """

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(query, f, indent=4)

    print(f"\nPrivacy-safe query saved to:\n{output_file}")