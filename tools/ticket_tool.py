import sqlite3


DB_PATH = "database/helpdesk.db"


def create_ticket(student_id, issue):
    """
    Create a support ticket for a student.
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tickets (student_id, issue, status)
            VALUES (?, ?, ?)
            """,
            (student_id, issue, "Open")
        )

        conn.commit()

        ticket_id = cursor.lastrowid
        conn.close()

        return {
            "status": "success",
            "ticket_id": ticket_id,
            "issue": issue,
            "ticket_status": "Open",
            "message": "Support ticket created successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unable to create ticket: {str(e)}"
        }


def delete_ticket(student_id, ticket_id=None):
    """
    Delete a support ticket by ticket ID or the last ticket for the student.
    """

    if isinstance(ticket_id, str) and ticket_id.isdigit():
        ticket_id = int(ticket_id)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if ticket_id is not None:
            cursor.execute(
                "SELECT id, issue FROM tickets WHERE id = ? AND student_id = ?",
                (ticket_id, student_id)
            )
            row = cursor.fetchone()

            if row is None:
                conn.close()
                return {
                    "status": "error",
                    "message": "Ticket not found for this student."
                }

            ticket_id, issue = row
        else:
            cursor.execute(
                "SELECT id, issue FROM tickets WHERE student_id = ? ORDER BY id DESC LIMIT 1",
                (student_id,)
            )
            row = cursor.fetchone()

            if row is None:
                conn.close()
                return {
                    "status": "error",
                    "message": "No tickets were found to delete."
                }

            ticket_id, issue = row

        cursor.execute(
            "DELETE FROM tickets WHERE id = ?",
            (ticket_id,)
        )

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "ticket_id": ticket_id,
            "issue": issue,
            "message": "Ticket deleted successfully."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unable to delete ticket: {str(e)}"
        }
