import random

from tools.auth import change_password


def reset_password(student_id):
    """
    Simulate a password reset OTP.

    NOTE:
    This is a prototype. No real SMS is sent.
    """

    otp = random.randint(100000, 999999)

    return {
        "status": "success",
        "student_id": student_id,
        "otp": otp,
        "message": "Password reset OTP generated successfully."
    }


def set_new_password(student_id, new_password):
    """
    Update a student's password.
    """

    result = change_password(student_id, new_password)

    if result["status"] == "success":
        return {
            "status": "success",
            "student_id": student_id,
            "new_password": new_password,
            "message": "Password updated successfully."
        }

    return result