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

    This is the ONLY information that would be sent to AJIO.
    No user photos, OCR text, or wardrobe images are included.
    """

    query = []

    for category in missing_items:
        for color in sorted(preferred_colors):
            query.append(f"Need:\n\n{color} {category.title()}")

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

    for i, category in enumerate(missing_items):
        print(f"Category : {category.title()}")
        print("Colors")
        for color in sorted(preferred_colors):
            try:
                print(f"• {color}")
            except UnicodeEncodeError:
                print(f"- {color}")

        if i < len(missing_items) - 1:
            print("-" * 20)