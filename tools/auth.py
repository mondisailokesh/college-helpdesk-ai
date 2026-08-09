import sqlite3

DB_PATH = "database/users.db"


def login(student_id, password):
    """
    Authenticate a student.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT student_id, name, department, year
        FROM students
        WHERE student_id = ?
        AND password = ?
        """,
        (student_id, password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        return {
            "status": "success",
            "student_id": user[0],
            "name": user[1],
            "department": user[2],
            "year": user[3]
        }

    return {
        "status": "failed",
        "message": "Invalid Student ID or Password."
    }


def get_student(student_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT student_id, name, department, year
        FROM students
        WHERE student_id = ?
        """,
        (student_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    return {
        "student_id": user[0],
        "name": user[1],
        "department": user[2],
        "year": user[3]
    }


def change_password(student_id, new_password):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE students
        SET password = ?
        WHERE student_id = ?
        """,
        (new_password, student_id)
    )

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    if success:

        return {
            "status": "success",
            "message": "Password updated successfully."
        }

    return {
        "status": "failed",
        "message": "Student not found."
    }