from rag.query_rewriter import rewrite_query

while True:

    q = input("Question : ")

    if q == "exit":
        break

    print(rewrite_query(q))