from tools.ticket_list import get_tickets

student_id = input("Student ID: ")

tickets = get_tickets(student_id)

print("\nMy Tickets\n")

if len(tickets) == 0:
    print("No tickets found.")
else:
    for ticket in tickets:
        print("----------------------")
        print("Ticket ID :", ticket[0])
        print("Issue     :", ticket[1])
        print("Status    :", ticket[2])