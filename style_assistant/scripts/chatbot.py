import sys
import argparse
import ollama

from style_assistant.scripts.build_prompt import build_prompt


def main():
    parser = argparse.ArgumentParser(description="AI Fashion Stylist")
    parser.add_argument(
        "--model", 
        type=str, 
        default="phi3:latest", 
        help="Ollama model to use (default: phi3:latest)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"AI Fashion Stylist (Model: {args.model})")
    print("=" * 60)

    # Build prompt from your project data
    prompt = build_prompt()

    print(f"\nPrompt length: {len(prompt)} characters")
    print("\nGenerating fashion advice...\n")

    print("=" * 60)
    print("Fashion Advice")
    print("=" * 60)

    try:
        response = ollama.chat(
            model=args.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI fashion stylist. "
                        "Give practical, personalized outfit recommendations "
                        "based on the user's trip, wardrobe, and preferences."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True
        )
        
        # Stream the response back to the console
        for chunk in response:
            print(chunk['message']['content'], end='', flush=True)
            
        print("\n")

    except Exception as e:
        print("\n[Error] Could not connect to the LLM or an error occurred.")
        print("Please ensure the Ollama application is running and the model is downloaded.")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


