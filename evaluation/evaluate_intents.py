import json
import os
import sys


# ---------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from router import route_query


# ---------------------------------------------------
# Load test cases
# ---------------------------------------------------

TEST_FILE = os.path.join(
    os.path.dirname(__file__),
    "test_cases.json"
)


with open(TEST_FILE, "r", encoding="utf-8") as file:
    test_cases = json.load(file)


# ---------------------------------------------------
# Evaluation
# ---------------------------------------------------

correct = 0
total = len(test_cases)

failed_cases = []


print("=" * 75)
print("COLLEGE HELPDESK AI - INTENT & TOOL ROUTING EVALUATION")
print("=" * 75)


for index, test in enumerate(test_cases, start=1):

    query = test["query"]
    expected = test["expected_intent"]

    try:

        response = route_query(query)

        predicted = response.get(
            "intent",
            "unknown"
        )

    except Exception as e:

        predicted = "error"

        print(f"\nError: {e}")

    is_correct = predicted == expected

    if is_correct:

        correct += 1
        status = "PASS"

    else:

        status = "FAIL"

        failed_cases.append({
            "query": query,
            "expected": expected,
            "predicted": predicted
        })

    print(f"\nTest {index}")

    print(f"Query     : {query}")
    print(f"Expected  : {expected}")
    print(f"Predicted : {predicted}")
    print(f"Result    : {status}")


# ---------------------------------------------------
# Accuracy
# ---------------------------------------------------

accuracy = (correct / total) * 100


print("\n" + "=" * 75)

print("EVALUATION RESULTS")

print("=" * 75)

print(f"Total Test Cases : {total}")
print(f"Correct          : {correct}")
print(f"Incorrect        : {total - correct}")
print(f"Accuracy         : {accuracy:.2f}%")

print("=" * 75)


# ---------------------------------------------------
# Failed cases
# ---------------------------------------------------

if failed_cases:

    print("\nFAILED TEST CASES")

    print("-" * 75)

    for failure in failed_cases:

        print(f"\nQuery     : {failure['query']}")
        print(f"Expected  : {failure['expected']}")
        print(f"Predicted : {failure['predicted']}")

else:

    print("\nAll test cases passed successfully!")