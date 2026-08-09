class ChatMemory:
    
    def __init__(self):
        self.history = []

    def add(self, role, message):

        self.history.append(
            {
                "role": role,
                "message": message
            }
        )

        # Keep only the last 6 messages
        if len(self.history) > 6:
            self.history = self.history[-6:]

    def get_context(self):

        context = ""

        for item in self.history:

            context += f"{item['role']}: {item['message']}\n"

        return context

    def clear(self):
        self.history = []