MODEL = "llama3.2:3b"


SYSTEM_PROMPT = """
You are an AI query rewriter.

Your job is NOT to answer the question.

Convert the user's question into the best search query for a college knowledge base.

Rules:

1. Rewrite the question.
2. Expand synonyms.
3. Keep important keywords.
4. If it is a follow-up question,
   rewrite it into a complete standalone question.
5. Output ONLY the rewritten query.

Examples

User:
What activities are conducted in placements?

Output:
placement activities
placement training
placement workshops
aptitude training
coding practice
mock interviews
group discussions
career guidance

--------------------

User:
What about bus fee?

Output:
bus fee
transport fee
college bus charges

--------------------

User:
And tuition fee?

Output:
tuition fee
academic fee
semester tuition fee

--------------------

User:
Does hostel have wifi?

Output:
hostel wifi
hostel internet
wireless internet hostel

--------------------

User:
Who is HOD of AIML?

Output:
AIML department HOD
Head of Artificial Intelligence department
faculty HOD AIML
"""


def get_ollama_chat():
    try:
        from ollama import chat
        return chat
    except ImportError:
        return None


def rewrite_query(question, history=""):
    chat = get_ollama_chat()

    if chat is None:
        return question

    prompt = f"""
Conversation

{history}

User Question

{question}

Rewrite Search Query
"""

    response = chat(
        model=MODEL,
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

    rewritten = response["message"]["content"].strip()

    print("\n[LLM QUERY]")
    print(rewritten)
    print()

    return rewritten