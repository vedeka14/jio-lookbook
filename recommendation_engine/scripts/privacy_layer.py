import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def build_ajio_query(missing_items, preferred_colors):
    """
    Build a privacy-safe query.

    Only clothing requirements are included.
    No photos, OCR text, travel documents, or wardrobe images.
    """

    query = []

    for item in missing_items:

        query.append({

            "category": item["category"].title(),
            "reason": item["reason"],
            "priority": item["priority"],

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


def display_query(missing_items, preferred_colors):
    """
    Print the privacy-safe query in a clean, grouped format.
    """
    print("\nPrivacy-safe Query\n")

    if not missing_items:
        print("No query generated.")
        return

    for i, item in enumerate(missing_items):
        print(f"Category : {item['category'].title()} ({item['priority']})")
        print(f"Reason   : {item['reason']}")
        print("Colors")
        for color in sorted(preferred_colors):
            try:
                print(f"• {color}")
            except UnicodeEncodeError:
                print(f"- {color}")

        if i < len(missing_items) - 1:
            print("-" * 20)