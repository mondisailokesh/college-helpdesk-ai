import sqlite3


DB_PATH = "database/helpdesk.db"


def get_tickets(student_id):
    """
    Return all support tickets belonging to a student.
    """

    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, issue, status
            FROM tickets
            WHERE student_id = ?
            ORDER BY id DESC
            """,
            (student_id,)
        )

        tickets = cursor.fetchall()

        conn.close()

        return tickets

    except Exception as e:

        return {
            "status": "error",
            "message": f"Unable to retrieve tickets: {str(e)}"
        }