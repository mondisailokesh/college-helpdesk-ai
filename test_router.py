from router import route_query


print("=" * 60)
print("COLLEGE HELPDESK AI - ROUTER TEST")
print("Type 'exit' to stop")
print("=" * 60)


while True:

    query = input("\nYou: ")

    if query.lower() == "exit":
        break

    response = route_query(query)

    print("\nBot:")
    print(response)