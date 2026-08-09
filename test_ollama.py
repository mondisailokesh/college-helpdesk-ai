from ollama import chat

response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Explain Artificial Intelligence in one simple sentence."
        }
    ]
)

print(response["message"]["content"])