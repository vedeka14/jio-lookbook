import ollama

print("Connecting to Ollama...")

response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": "Reply with only the word Hello."
        }
    ]
)

print(response["message"]["content"])