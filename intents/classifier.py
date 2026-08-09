import re


def detect_intent(query):
    """
    Rule-based intent classifier for College Helpdesk AI.

    Priority:
    1. View existing tickets
    2. Password reset
    3. Contact office
    4. Informational/RAG exceptions
    5. Create new ticket
    6. RAG fallback
    """

    query = query.lower().strip()

    # ==================================================
    # 1. VIEW EXISTING TICKETS / COMPLAINTS
    # ==================================================

    view_phrases = [
        "show my tickets",
        "show tickets",
        "my tickets",
        "view tickets",
        "view my tickets",
        "view my support tickets",
        "list tickets",
        "list my tickets",
        "ticket status",
        "check my ticket",
        "check ticket status",

        "show my complaints",
        "view my complaints",
        "my complaints",
        "list my complaints",
        "complaint status",
        "previous complaints",
        "existing complaints",

        "support requests",
        "previous support requests",
        "show previous support requests",

        "complaints have i raised",
        "complaints did i submit",
        "complaints i submitted",

        "open tickets",
        "any support tickets",
        "any tickets"
    ]

    if any(phrase in query for phrase in view_phrases):
        return "view_tickets"

    # More flexible view detection
    ticket_words = [
        "ticket",
        "tickets",
        "complaint",
        "complaints",
        "support request",
        "support requests"
    ]

    view_words = [
        "show",
        "view",
        "list",
        "check",
        "status",
        "previous",
        "existing",
        "submitted",
        "raised",
        "open",
        "have any",
        "did i",
        "my"
    ]

    if (
        any(word in query for word in ticket_words)
        and any(word in query for word in view_words)
    ):
        return "view_tickets"

    # ==================================================
    # 2. DELETE TICKET / COMPLAINT
    # ==================================================

    delete_phrases = [
        "delete ticket",
        "remove ticket",
        "cancel ticket",
        "delete complaint",
        "remove complaint",
        "cancel complaint",
        "delete my ticket",
        "remove my ticket",
        "delete my complaint",
        "remove my complaint"
    ]

    if any(phrase in query for phrase in delete_phrases):
        return "delete_ticket"

    # ==================================================
    # 3. PASSWORD RESET
    # ==================================================

    password_phrases = [
        "password",
        "reset password",
        "change password",
        "forgot password",
        "forgot my password",
        "password reset",
        "update password"
    ]

    if any(phrase in query for phrase in password_phrases):
        return "password_reset"

    # ==================================================
    # 4. CONTACT / OFFICE INFORMATION
    # ==================================================

    office_words = [
        "examination",
        "exam branch",
        "exam office",
        "examination branch",
        "examination office",
        "accounts",
        "accounts office",
        "placement",
        "placement cell",
        "library"
    ]

    contact_words = [
        "contact",
        "contact details",
        "phone",
        "phone number",
        "email",
        "email address",
        "where is",
        "where can i find",
        "find the",
        "location",
        "located",
        "address"
    ]

    if (
        any(office in query for office in office_words)
        and any(word in query for word in contact_words)
    ):
        return "contact_office"

    complaint_patterns = [
        r"\b(?:mess|canteen|hostel|hostel mess|hostel food|food)\b.*\b(?:not|poor|bad|terrible|awful|disgusting|unfit|unhealthy|spoiled|stale|cold|burnt|not good|not well|sick)\b",
        r"\b(?:not|poor|bad|terrible|awful|disgusting|unfit|unhealthy|spoiled|stale|cold|burnt|not good|not well|sick)\b.*\b(?:mess|canteen|hostel|hostel mess|hostel food|food)\b"
    ]

    if any(re.search(pattern, query) for pattern in complaint_patterns):
        return "create_ticket"

    # ==================================================
    # 4. INFORMATIONAL QUESTIONS → RAG
    # ==================================================
    # These rules prevent informational questions such as
    # "What WiFi problems are common?" from creating tickets.

    informational_starters = [
        "what is",
        "what are",
        "what problems",
        "tell me about",
        "explain",
        "describe",
        "give me information",
        "information about"
    ]

    if any(query.startswith(phrase) for phrase in informational_starters):
        return "rag_query"

    # ==================================================
    # 5. CREATE NEW SUPPORT TICKET
    # ==================================================

    create_phrases = [
        "raise a complaint",
        "raise complaint",
        "create complaint",
        "new complaint",
        "file a complaint",
        "file complaint",
        "raise a ticket",
        "raise ticket",
        "create ticket",
        "create a ticket",
        "report a problem",
        "report an issue",
        "report hostel",
        "i want to report",
        "please file a complaint",
        "food was not good",
        "bad food",
        "poor food",
        "mess food",
        "hostel mess",
        "canteen food",
        "food quality",
        "mess is bad",
        "mess is not good"
    ]

    if any(phrase in query for phrase in create_phrases):
        return "create_ticket"

    # Explicit malfunction/problem descriptions
    malfunction_phrases = [
        "not working",
        "doesn't work",
        "does not work",
        "stopped working",
        "is broken",
        "not functioning",
        "no water",
        "no electricity",
        "no internet",
        "no wifi"
    ]

    if any(phrase in query for phrase in malfunction_phrases):
        return "create_ticket"

    problem_phrases = [
        "i have a problem",
        "i have an issue",
        "i am having a problem",
        "i am having an issue",
        "there is a problem",
        "there is an issue",
        "has a problem",
        "has an issue"
    ]

    if any(phrase in query for phrase in problem_phrases):
        return "create_ticket"

    # ==================================================
    # 6. DEFAULT → RAG
    # ==================================================

    return "rag_query"