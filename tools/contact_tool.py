OFFICES = {

    "exam": {
        "office": "Examination Branch",
        "location": "Block A - First Floor",
        "phone": "9876543210",
        "email": "exam@college.edu"
    },

    "accounts": {
        "office": "Accounts Office",
        "location": "Administration Block",
        "phone": "9876543211",
        "email": "accounts@college.edu"
    },

    "placement": {
        "office": "Placement Cell",
        "location": "Training & Placement Block",
        "phone": "9876543212",
        "email": "placement@college.edu"
    },

    "library": {
        "office": "Central Library",
        "location": "Library Building",
        "phone": "9876543213",
        "email": "library@college.edu"
    }
}


def get_contact(query):

    query = query.lower()

    if "exam" in query:
        return OFFICES["exam"]

    elif "account" in query or "fee office" in query:
        return OFFICES["accounts"]

    elif "placement" in query:
        return OFFICES["placement"]

    elif "library" in query:
        return OFFICES["library"]

    else:
        return {
            "status": "not_found",
            "message": "I couldn't identify the office. Try Examination Branch, Accounts Office, Placement Cell, or Library."
        }