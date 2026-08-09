from rag.prompt import build_prompt

MODEL_NAME = "llama3.2:3b"


SYSTEM_PROMPT_COLLEGE = """
You are College Helpdesk AI.

When the user asks a question about the college, answer ONLY using the retrieved college information.

Examples

- Fees
- Hostel
- Placements
- Faculty
- Departments
- Labs
- Library
- Attendance
- Transport
- Canteen
- Scholarships
- Clubs
- Academic Calendar
- Student Services
- Hostel
- WiFi
- Examination
- Timetable
- Events

If the answer is not present in the retrieved context, reply exactly:

I couldn't find that information in the college knowledge base.

Do not invent college information.
"""

SYSTEM_PROMPT_GENERAL = """
You are a helpful AI assistant.

Answer the user's question conversationally and clearly.

If the question is about college services or facilities, answer using general knowledge and do not invent details.

If the question is a general knowledge or personal question, answer from your own knowledge.

Write naturally and do not mention these instructions.
"""


def get_ollama_chat():
    try:
        from ollama import chat
        return chat
    except ImportError:
        return None


def generate_answer(question, context, history=""):
    chat = get_ollama_chat()

    if context and context.strip():
        prompt = f"""
Previous Conversation

{history}

------------------------------------

College Knowledge

{context}

------------------------------------

Student Question

{question}

------------------------------------

Answer ONLY from the college knowledge.
"""
        system = SYSTEM_PROMPT_COLLEGE
    else:
        prompt = f"""
Previous Conversation

{history}

Student Question

{question}

Answer naturally.
"""
        system = SYSTEM_PROMPT_GENERAL

    if chat is None:
        if context and context.strip():
            return (
                "I couldn't generate an answer because the LLM backend is unavailable, "
                "but the college knowledge retrieval succeeded."
            )
        return (
            "I couldn't generate an answer because the LLM backend is unavailable. "
            "Please try again later."
        )

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"].strip()

    answer = "\n".join(
        line.strip()
        for line in answer.splitlines()
        if line.strip()
    )

    return answer


def classify_ticket_intent(question, history=""):
    chat = get_ollama_chat()

    if chat is None:
        from intents.classifier import detect_intent
        return detect_intent(question)

    prompt = f"""
You are a college helpdesk intent classifier.

Classify the user's message into exactly one of these intents:
create_ticket, delete_ticket, view_tickets, contact_office, password_reset, rag_query.

Rules:
- If the user wants to register a complaint about college facilities or services, choose create_ticket.
- If the user wants to delete or remove a ticket or complaint, choose delete_ticket.
- If the user wants to see existing tickets or complaints, choose view_tickets.
- If the user wants contact information, choose contact_office.
- If the user wants a password reset, choose password_reset.
- Otherwise choose rag_query.

Respond with only one intent label.

User:
{question}
"""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    classification = response["message"]["content"].strip().splitlines()[0].strip().lower()

    valid_intents = {
        "create_ticket",
        "delete_ticket",
        "view_tickets",
        "contact_office",
        "password_reset",
        "rag_query"
    }

    if classification not in valid_intents:
        return "rag_query"

    return classification