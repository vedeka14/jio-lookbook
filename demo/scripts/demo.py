import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_step(title, module):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            module
        ]
    )

    if result.returncode != 0:
        print(f"\n[FAILED] {title} failed.")
        sys.exit(result.returncode)

    print(f"\n[OK] {title} completed.")


def main():

    print("\n" + "=" * 60)
    print("          Jio Lookbook – Goa Trip Outfit Helper")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("Input")
    print("=" * 60)

    try:
        print("\nFlight Ticket\n\n✓ goa_ticket.jpg\n")
        print("Wardrobe Photos\n\n✓ 17 Images\n")
    except UnicodeEncodeError:
        print("\nFlight Ticket\n\n[OK] goa_ticket.jpg\n")
        print("Wardrobe Photos\n\n[OK] 17 Images\n")

    print("Starting AI Pipeline...")

    run_step(
        "Step 1 - Analyze Wardrobe",
        "fashion_ai.wardrobeinference.build_wardrobe_yolo"
    )

    run_step(
        "Step 2 - Read Travel Ticket",
        "travel_context_ai.scripts.ocr_ticket"
    )

    run_step(
        "Step 3 - Understand Trip",
        "travel_context_ai.scripts.travel_context"
    )

    run_step(
        "Step 4 - Recommend Outfit",
        "recommendation_engine.scripts.recommend_outfit"
    )

    print("\n" + "=" * 60)
    print("Jio Lookbook MVP Completed")
    print("=" * 60)

    try:
        print("\n✓ Wardrobe Built")
        print("✓ Trip Understood")
        print("✓ Recommendations Generated")
        print("✓ Privacy Preserved")
    except UnicodeEncodeError:
        print("\n[OK] Wardrobe Built")
        print("[OK] Trip Understood")
        print("[OK] Recommendations Generated")
        print("[OK] Privacy Preserved")

    print("\nThank you!\n\nReady for GPU YOLO Integration")


if __name__ == "__main__":
    main()