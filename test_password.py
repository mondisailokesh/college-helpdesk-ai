from tools.password_reset import reset_password

student_id = input("Enter Student ID: ")

result = reset_password(student_id)

print("\nResponse")
print(result)