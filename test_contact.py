from tools.contact_tool import get_contact

while True:

    query = input("Department: ")

    if query.lower() == "exit":
        break

    print()

    print(get_contact(query))