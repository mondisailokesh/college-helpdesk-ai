import re
import os

from intents.classifier import detect_intent

from tools.password_reset import reset_password
from tools.ticket_tool import create_ticket, delete_ticket
from tools.ticket_list import get_tickets
from tools.contact_tool import get_contact


def classify_intent(query, history=""):
    local_intent = detect_intent(query)
    llm_intent = None

    try:
        from rag.llm import classify_ticket_intent

        llm_intent = classify_ticket_intent(query, history)
    except Exception:
        llm_intent = None

    strong_local = local_intent != "rag_query"
    strong_llm = llm_intent in {
        "create_ticket",
        "delete_ticket",
        "view_tickets",
        "contact_office",
        "password_reset"
    }

    if strong_llm:
        return llm_intent
    if strong_local:
        return local_intent
    return llm_intent or local_intent


def retrieve_answer(query, history=""):
    try:
        from rag.retriever import retrieve
    except ImportError:
        return {
            "context": "",
            "source": None,
            "error": "Knowledge retriever unavailable"
        }

    try:
        retrieved = retrieve(query, history=history)
    except Exception as exc:
        return {
            "context": "",
            "source": None,
            "error": str(exc)
        }

    if isinstance(retrieved, dict):
        return retrieved

    if isinstance(retrieved, tuple) and len(retrieved) == 2:
        context, source = retrieved
        return {
            "context": context,
            "source": source
        }

    return {
        "context": "",
        "source": None
    }


def get_generate_answer_fn():
    try:
        from rag.llm import generate_answer
        return generate_answer
    except ImportError:
        def fallback_generate_answer(question, context, history=""):
            # If retriever provided context, return a helpful excerpt
            if context:
                # prefer returning the most relevant paragraph
                txt = context.strip()
                if len(txt) > 1500:
                    return txt[:1500] + "..."
                return txt

            # Try to find an answer directly from local knowledge files
            try:
                import glob
                base_dir = os.getcwd()
                knowledge_glob = os.path.join(base_dir, "knowledge", "*.md")
                qwords = [w.lower() for w in re.findall(r"\w+", question) if len(w) > 2]

                best_path = None
                best_score = 0

                for path in glob.glob(knowledge_glob):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            text = f.read()
                    except Exception:
                        continue

                    text_low = text.lower()
                    score = sum(1 for w in qwords if w in text_low)
                    if score > best_score:
                        best_score = score
                        best_path = path

                if best_path and best_score > 0:
                    with open(best_path, "r", encoding="utf-8") as f:
                        text = f.read()
                    # try to extract a subsection for the query (e.g., Bus Fee)
                    m = re.search(r"##+\s*(.*?)\n\n(.*?)(?:\n---|\n##|$)", text, flags=re.I | re.S)
                    if m:
                        snippet = m.group(2).strip()
                        if len(snippet) > 1500:
                            snippet = snippet[:1500] + "..."
                        return snippet
                    return text.strip()[:1500]
            except Exception:
                pass

            return (
                "I couldn't generate an answer because the LLM backend is unavailable. "
                "Please try again later."
            )

        return fallback_generate_answer


generate_answer = get_generate_answer_fn()

STOP_WORDS = {
    "what", "is", "the", "a", "an", "and", "or", "to", "of", "in", "on",
    "for", "my", "how", "do", "can", "i", "please", "you", "it", "that",
    "which", "are", "have", "has", "with", "by", "from", "at", "as"
}


def normalize_query_terms(query):
    return [
        w for w in re.findall(r"\w+", query.lower())
        if len(w) > 2 and w not in STOP_WORDS
    ]


def extract_best_section(query, text):
    sections = []
    query_terms = normalize_query_terms(query)

    for match in re.finditer(r"##+\s*(.+?)\s*\n\n(.*?)(?=\n##+|\Z)", text, flags=re.S):
        heading = match.group(1).strip().lower()
        content = match.group(2).strip()
        heading_terms = set(re.findall(r"\w+", heading))
        score = sum(1 for term in query_terms if term in heading_terms)
        if score > 0:
            sections.append((score, heading, content))

    if sections:
        return max(sections, key=lambda item: item[0])[2]

    # as fallback, return the first paragraph containing the most query terms
    paragraphs = re.split(r"\n\n+", text)
    best_para = ""
    best_score = 0
    for para in paragraphs:
        para_low = para.lower()
        score = sum(1 for term in query_terms if term in para_low)
        if score > best_score:
            best_score = score
            best_para = para.strip()
    return best_para or text.strip()


def choose_knowledge_file(query):
    query_low = query.lower()
    if "hostel fee" in query_low or "bus fee" in query_low or "tuition fee" in query_low or "transport fee" in query_low:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge", "fees.md")
    if "fee" in query_low and any(word in query_low for word in ["hostel", "bus", "tuition", "transport", "mess"]):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge", "fees.md")
    return None


# -----------------------------------------
# Conversation Memory
# -----------------------------------------

conversation_history = []


def add_history(role, message):

    conversation_history.append(f"{role}: {message}")

    # Keep only last 6 messages
    if len(conversation_history) > 6:
        conversation_history.pop(0)


def get_history():

    return "\n".join(conversation_history)


# -----------------------------------------
# Main Router
# -----------------------------------------

def route_query(query, student_id="23PA1A4271"):

    query = query.strip()

    lower = query.lower()

    # -----------------------------------------
    # Greetings
    # -----------------------------------------

    greetings = [

        r"\bhi\b",

        r"\bhello\b",

        r"\bhey\b",

        r"\bhii+\b",

        r"\bgood morning\b",

        r"\bgood afternoon\b",

        r"\bgood evening\b"

    ]

    if any(re.search(p, lower) for p in greetings):

        return {

            "intent": "greeting",

            "message":
            "Hello! 👋\n\n"
            "Welcome to College Helpdesk AI.\n"
            "How can I help you today?"

        }

    # -----------------------------------------
    # Intent Detection
    # -----------------------------------------

    intent = classify_intent(query)

    print(f"[Router] Detected Intent: {intent}")

    # -----------------------------------------
    # Password Reset
    # -----------------------------------------

    if intent == "password_reset":
        new_password = None
        pw_patterns = [
            r"change(?: my)? password(?: to| is|:)\s*(\S+)",
            r"set(?: my)? password(?: to| is|:)\s*(\S+)",
            r"new password(?: is|:)\s*(\S+)",
            r"password(?: is|=|:)\s*(\S+)"
        ]

        for p in pw_patterns:
            match = re.search(p, query, flags=re.I)
            if match:
                new_password = match.group(1).strip()
                break

        student = student_id
        sid_match = re.search(r"\b[0-9]{2}[A-Z]{2}[0-9A-Z]{6,8}\b", query, flags=re.I)
        if sid_match:
            student = sid_match.group(0).strip()

        if new_password:
            try:
                from tools.password_reset import set_new_password

                result = set_new_password(student, new_password)
                result["intent"] = "password_reset"
                if result.get("status") == "success":
                    result["message"] = "Your password has been updated successfully."
                return result
            except Exception as exc:
                return {
                    "intent": "password_reset",
                    "status": "failed",
                    "message": f"Failed to update password: {exc}"
                }

        return {
            "intent": "password_reset",
            "stage": "request_new_password",
            "message": (
                "Sure — please reply with your student ID and the new password in one message, "
                "for example: `23PA1A4271 new password: MyNewP@ssw0rd`."
            )
        }

    # -----------------------------------------
    # Create Ticket
    # -----------------------------------------

    elif intent == "create_ticket":

        response = create_ticket(
            student_id,
            query
        )

        response["intent"] = intent

        return response

    # -----------------------------------------
    # View Tickets
    # -----------------------------------------

    elif intent == "view_tickets":

        return {

            "intent": intent,

            "tickets": get_tickets(student_id)

        }

    # -----------------------------------------
    # Delete Ticket
    # -----------------------------------------

    elif intent == "delete_ticket":

        ticket_id = None
        match = re.search(r"\b(\d+)\b", query)

        if match:
            ticket_id = int(match.group(1))

        if ticket_id is None:
            tickets = get_tickets(student_id)

            return {
                "intent": "delete_ticket",
                "stage": "choose_ticket",
                "message": (
                    "Please choose which ticket number you want to delete from your existing tickets."
                ),
                "tickets": tickets
            }

        response = delete_ticket(student_id, ticket_id)
        response["intent"] = intent

        return response

    # -----------------------------------------
    # Contact Details
    # -----------------------------------------

    elif intent == "contact_office":

        response = get_contact(query)

        response["intent"] = intent

        return response

    # -----------------------------------------
    # RAG + Ollama
    # -----------------------------------------

    else:

        retrieved = retrieve_answer(query)

        context = retrieved.get("context", "")

        source = retrieved.get("source")

        # Local fallback: if retriever failed to return context, search knowledge files
        if (not context) or (source is None):
            fee_file = choose_knowledge_file(query)
            if fee_file and os.path.exists(fee_file):
                with open(fee_file, "r", encoding="utf-8") as f:
                    context = f.read()
                source = os.path.basename(fee_file)
                print(f"[Router] Chose knowledge file by query hint: {source}")
            else:
                import glob

                base_dir = os.path.dirname(os.path.abspath(__file__))
                knowledge_dir = os.path.join(base_dir, "knowledge")
                knowledge_glob = os.path.join(knowledge_dir, "*.md")

                qwords = normalize_query_terms(query)

                best_snippet = None
                best_source = None
                best_score = 0

                files = glob.glob(knowledge_glob)
                print(f"[Router] Looking in {knowledge_glob}, found {len(files)} files")
                for path in files:
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            text = f.read()
                    except Exception as exc:
                        print(f"[Router] Failed reading {path}: {exc}")
                        continue

                    text_low = text.lower()
                    score = sum(1 for w in qwords if w in text_low)

                    if score > best_score:
                        best_score = score
                        best_snippet = text
                        best_source = os.path.basename(path)

                if best_snippet and best_score > 0:
                    context = best_snippet
                    source = best_source
                    print(f"[Router] Matched knowledge file: {source} (score={best_score})")
                else:
                    print(f"[Router] No knowledge match (best_score={best_score}) qwords={qwords}")

        history = get_history()

        answer = generate_answer(
            question=query,
            context=context,
            history=history
        )

        # If the LLM returned an "unavailable" message, try to serve a local knowledge answer
        if isinstance(answer, str) and "LLM backend is unavailable" in answer:
            # If retriever provided context, prefer that
            if context:
                try:
                    specific = extract_best_section(query, context)
                    answer = specific or context.strip()[:1000]
                except Exception:
                    answer = context.strip()[:1000]
            else:
                # search local knowledge files for best match
                try:
                    fee_file = choose_knowledge_file(query)
                    if fee_file and os.path.exists(fee_file):
                        with open(fee_file, "r", encoding="utf-8") as f:
                            text = f.read()
                        answer = extract_best_section(query, text)
                        source = os.path.basename(fee_file)
                    else:
                        import glob

                        base_dir = os.getcwd()
                        knowledge_glob = os.path.join(base_dir, "knowledge", "*.md")
                        qwords = normalize_query_terms(query)

                        best_path = None
                        best_score = 0

                        for path in glob.glob(knowledge_glob):
                            try:
                                with open(path, "r", encoding="utf-8") as f:
                                    text = f.read()
                            except Exception:
                                continue

                            text_low = text.lower()
                            score = sum(1 for w in qwords if w in text_low)
                            if score > best_score:
                                best_score = score
                                best_path = path

                        if best_path and best_score > 0:
                            with open(best_path, "r", encoding="utf-8") as f:
                                text = f.read()
                            answer = extract_best_section(query, text)
                            source = os.path.basename(best_path)
                except Exception:
                    pass

        add_history("User", query)

        add_history("Assistant", answer)

        return {

            "intent": "rag_query",

            "answer": answer,

            "source": source

        }