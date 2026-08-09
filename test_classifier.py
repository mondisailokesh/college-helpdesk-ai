from intents.classifier import detect_intent

while True:

    query = input("Enter Query: ")

    if query.lower() == "exit":
        break

    intent = detect_intent(query)

    print("\nDetected Intent:", intent)