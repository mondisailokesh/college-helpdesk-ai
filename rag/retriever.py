from rag.query_rewriter import rewrite_query

# ----------------------------
# Configuration
# ----------------------------

TOP_RESULTS_PER_QUERY = 3
MAX_DISTANCE = 1.10
MAX_CONTEXT_CHUNKS = 8

_embedding_model = None
_collection = None


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(f"SentenceTransformers not available: {exc}")

        _embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _embedding_model


def get_collection():
    global _collection

    if _collection is None:
        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(f"Chromadb not available: {exc}")

        client = chromadb.PersistentClient(path="college_db")
        _collection = client.get_collection("college_helpdesk")

    return _collection


def retrieve(question, history=""):

    # ----------------------------
    # Rewrite Query using Ollama
    # ----------------------------

    rewritten = rewrite_query(question, history)

    queries = [
        q.strip()
        for q in rewritten.split("\n")
        if q.strip()
    ]

    if len(queries) == 0:
        queries = [question]

    print("\nSearching using:\n")

    for q in queries:
        print("-", q)

    print()

    retrieved = []

    seen = set()

    # ----------------------------
    # Search each rewritten query
    # ----------------------------

    for query in queries:

        # obtain embedding model and collection (lazy)
        embedding_model = get_embedding_model()
        collection = get_collection()

        embedding = embedding_model.encode(query).tolist()

        results = collection.query(
            query_embeddings=[embedding],
            n_results=TOP_RESULTS_PER_QUERY
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, distance in zip(
            docs,
            metas,
            distances
        ):

            print(
                f"[{query}] "
                f"{meta['source']} "
                f"{distance:.4f}"
            )

            if distance > MAX_DISTANCE:
                continue

            if doc in seen:
                continue

            seen.add(doc)

            retrieved.append(
                (
                    distance,
                    doc,
                    meta["source"]
                )
            )

    if len(retrieved) == 0:

        return "", None

    # ----------------------------
    # Rank Results
    # ----------------------------

    retrieved.sort(
        key=lambda x: x[0]
    )

    retrieved = retrieved[:MAX_CONTEXT_CHUNKS]

    context = "\n\n".join(
        x[1] for x in retrieved
    )

    sources = list(
        dict.fromkeys(
            x[2] for x in retrieved
        )
    )

    return context, ", ".join(sources)