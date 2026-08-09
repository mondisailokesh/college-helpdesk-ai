from tools.auth import login

student_id = input("Student ID: ")
password = input("Password: ")

response = login(student_id, password)

print("\nResponse")
print(response)