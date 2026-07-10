from ollama import chat

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": "Reply ONLY with the word Hello."
        }
    ]
)

print(response.message.content)