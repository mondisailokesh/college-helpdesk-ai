import os
import re
import sys
import streamlit as st

# ---------------------------------------------------
# Project Path
# ---------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------
# Imports
# ---------------------------------------------------

from router import route_query
from tools.auth import login
from tools.password_reset import set_new_password
from tools.ticket_tool import delete_ticket

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="College Helpdesk AI",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------
# Session Variables
# ---------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "student" not in st.session_state:
    st.session_state.student = None

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content":
            "Hello! 👋\n\n"
            "I'm your College Helpdesk AI.\n\n"
            "How can I help you today?"
        }
    ]

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

if "pending_action_data" not in st.session_state:
    st.session_state.pending_action_data = None

# ---------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------

if not st.session_state.logged_in:

    st.title("🎓 College AI Portal")

    st.write("Please log in with your student credentials to continue.")

    with st.form(key="login_form"):

        student_id = st.text_input("Student ID")

        password = st.text_input("Password", type="password")

        login_button = st.form_submit_button("Login")

        if login_button:

            response = login(student_id, password)

            if response["status"] == "success":

                st.session_state.logged_in = True

                st.session_state.student = response

                st.success(f"Welcome {response['name']}")

                st.rerun()

            else:

                st.error(response["message"])

    st.stop()

# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

with st.sidebar:

    st.title("🎓 College Helpdesk AI")

    st.success("🟢 Offline AI Ready")

    st.markdown("---")

    student = st.session_state.student

    st.write(
        f"**Student:** {student['name']}"
    )

    st.write(
        f"**ID:** {student['student_id']}"
    )

    st.write(
        f"**Department:** {student['department']}"
    )

    st.write(
        f"**Year:** {student['year']}"
    )

    st.markdown("---")

    st.subheader("💡 Suggested Questions")

    st.markdown("""
- What is the hostel fee?
- What is the bus fee?
- Library timings
- Attendance requirement
- Bonafide certificate
- Reset my password
- Raise a complaint
- Show my tickets
- Contact examination office
""")

    st.markdown("---")

    if st.button(
        "🗑 Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content":
                "Hello! 👋\n\n"
                "How can I help you today?"
            }
        ]

        st.rerun()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.student = None

        st.session_state.messages = []

        st.rerun()

# ---------------------------------------------------
# Header
# ---------------------------------------------------

st.title("🎓 College Helpdesk AI")

st.info(
    f"Welcome **{student['name']}** | {student['department']} | Year {student['year']}"
)

# ---------------------------------------------------
# Display Messages
# ---------------------------------------------------

for message in st.session_state.messages:

    avatar = "🎓" if message["role"] == "assistant" else "👤"

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(message["content"])
        
# ---------------------------------------------------
# Response Formatter
# ---------------------------------------------------

def format_response(response):

    intent = response.get("intent")

    # ---------------------------------------------------
    # Greeting
    # ---------------------------------------------------

    if intent == "greeting":

        return f"""
### 👋 Welcome

{response['message']}
"""

    # ---------------------------------------------------
    # RAG Response
    # ---------------------------------------------------

    elif intent == "rag_query":

        answer = response.get(
            "answer",
            "I couldn't find that information."
        )

        source = response.get("source")

        if source:
            text = f"""
### 📚 College Information

{answer}
"""

            text += f"""

---

📄 **Knowledge Source**

`{source}`
"""

            return text

        return answer


    # ---------------------------------------------------
    # Complaint Created
    # ---------------------------------------------------

    elif intent == "create_ticket":

        return f"""
### 🎫 Complaint Registered

Your complaint has been successfully registered.

### Ticket Number

`#{response['ticket_id']}`

### Issue

{response['issue']}

### Current Status

🟡 {response['ticket_status']}
"""

    # ---------------------------------------------------
    # Ticket Deleted / Choose Ticket
    # ---------------------------------------------------

    elif intent == "delete_ticket":

        if response.get("stage") == "choose_ticket":
            tickets = response.get("tickets", [])

            if not tickets:
                return """
### 🎫 No Tickets Available

You do not have any existing tickets to delete.
"""

            reply = "## 🗑 Delete a Ticket\n\n"
            reply += "Please enter the ticket number of the complaint you want to delete.\n\n"

            for ticket in tickets:
                reply += f"- **Ticket #{ticket[0]}**: {ticket[1]} (Status: {ticket[2]})\n"

            return reply

        status = response.get("status")

        if status != "success":
            return f"""
### ⚠️ Ticket Deletion Failed

{response.get('message', 'Unable to delete the ticket.')}
"""

        return f"""
### 🗑 Ticket Deleted

Your ticket has been deleted successfully.

### Ticket Number

`#{response['ticket_id']}`

### Issue

{response['issue']}
"""

    # ---------------------------------------------------
    # View Tickets
    # ---------------------------------------------------

    elif intent == "view_tickets":

        tickets = response.get("tickets", [])

        if len(tickets) == 0:

            return """
### 🎫 My Complaints

No complaints have been registered.
"""

        reply = "## 🎫 My Complaints\n\n"

        for ticket in tickets:

            reply += f"""
### Ticket #{ticket[0]}

**Issue**

{ticket[1]}

**Status**

🟡 {ticket[2]}

---
"""

        return reply

    # ---------------------------------------------------
    # Contact Office
    # ---------------------------------------------------

    elif intent == "contact_office":

        return f"""
### 🏢 {response['office']}

📍 **Location**

{response['location']}

📞 **Phone**

{response['phone']}

📧 **Email**

{response['email']}
"""

    # ---------------------------------------------------
    # Password Reset
    # ---------------------------------------------------

    elif intent == "password_reset":
        if response.get("status") == "success":
            return """
### 🔑 Password Reset Successful

Your password has been updated successfully.
"""

        if response.get("status") == "failed":
            return f"""
### ⚠️ Password Reset Failed

{response.get('message', 'Unable to reset password.')}
"""

        return f"""
### 🔑 Password Reset

{response.get('message', 'Please enter your new password in the format: `new password: MyNewP@ssw0rd`.')}
"""

    # ---------------------------------------------------
    # Unknown
    # ---------------------------------------------------

    return f"""
Sorry.

I couldn't process your request.

Debug: intent={intent}, response={response}
"""

# ---------------------------------------------------
# Chat Input
# ---------------------------------------------------

prompt = st.chat_input(
    "Ask anything about your college..."
)

# ---------------------------------------------------
# Process User Query
# ---------------------------------------------------

if prompt:

    # Store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(prompt)

    # Assistant Response
    with st.chat_message(
        "assistant",
        avatar="🎓"
    ):

        with st.spinner("🤖 Thinking..."):

            try:

                student_id = st.session_state.student["student_id"]

                if st.session_state.pending_action == "password_reset":
                    new_password = prompt.strip()
                    response = set_new_password(student_id, new_password)
                    response["intent"] = "password_reset"
                    response["stage"] = "completed"
                    response["message"] = (
                        "Your password has been updated successfully."
                    )
                    st.session_state.pending_action = None
                    st.session_state.pending_action_data = None
                elif st.session_state.pending_action == "delete_ticket":
                    match = re.search(r"\b(\d+)\b", prompt)

                    if match:
                        ticket_id = int(match.group(1))
                        response = delete_ticket(student_id, ticket_id)
                        response["intent"] = "delete_ticket"
                        st.session_state.pending_action = None
                        st.session_state.pending_action_data = None
                    else:
                        response = {
                            "intent": "delete_ticket",
                            "status": "error",
                            "message": "Please enter the ticket number you want to delete."
                        }
                else:
                    response = route_query(
                        prompt,
                        student_id
                    )

                    if response.get("intent") == "password_reset" and response.get("stage") == "request_new_password":
                        st.session_state.pending_action = "password_reset"
                        st.session_state.pending_action_data = None
                    elif response.get("intent") == "delete_ticket" and response.get("stage") == "choose_ticket":
                        st.session_state.pending_action = "delete_ticket"
                        st.session_state.pending_action_data = None

                reply = format_response(response)

            except Exception as e:

                reply = f"""
### ⚠️ Error

{str(e)}
"""

        st.markdown(reply)

    # Save Assistant Message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

