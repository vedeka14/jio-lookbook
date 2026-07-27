import subprocess
import sys


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
    print("          Jio Lookbook MVP")
    print("=" * 60)

    run_step(
        "Step 1 - YOLO Wardrobe Inference",
        "fashion_ai.wardrobeinference.build_wardrobe_yolo"
    )

    run_step(
        "Step 2 - OCR Ticket",
        "travel_context_ai.scripts.ocr_ticket"
    )

    run_step(
        "Step 3 - Trip Context",
        "travel_context_ai.scripts.travel_context"
    )

    run_step(
        "Step 4 - Recommendation Engine",
        "recommendation_engine.scripts.recommend_outfit"
    )

    print("\n" + "=" * 60)
    print("[SUCCESS] Jio Lookbook MVP Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()