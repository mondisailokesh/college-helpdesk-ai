from rag.llm import generate_answer

context = """
Hostel Fee:
₹40,000 per semester.
"""

question = "What is the hostel fee?"

answer = generate_answer(question, context)

print(answer)