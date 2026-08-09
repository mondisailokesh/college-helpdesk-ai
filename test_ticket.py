from tools.ticket_tool import create_ticket

student_id = input("Student ID: ")

issue = input("Issue: ")

response = create_ticket(student_id, issue)

print("\nResponse")

print(response)