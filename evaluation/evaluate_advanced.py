import json
import os
import sys
from collections import defaultdict


# ---------------------------------------------------
# Add project root
# ---------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from router import route_query


# ---------------------------------------------------
# Load advanced test cases
# ---------------------------------------------------

TEST_FILE = os.path.join(
    os.path.dirname(__file__),
    "advanced_test_cases.json"
)


with open(TEST_FILE, "r", encoding="utf-8") as file:
    test_cases = json.load(file)


# ---------------------------------------------------
# Evaluation variables
# ---------------------------------------------------

total = len(test_cases)
correct = 0

failed_cases = []

category_results = defaultdict(
    lambda: {
        "correct": 0,
        "total": 0
    }
)


print("=" * 80)
print("COLLEGE HELPDESK AI - ADVANCED EVALUATION")
print("=" * 80)


# ---------------------------------------------------
# Run tests
# ---------------------------------------------------

for index, test in enumerate(test_cases, start=1):

    query = test["query"]

    expected = test["expected_intent"]

    category = test["category"]


    category_results[category]["total"] += 1


    try:

        response = route_query(query)

        predicted = response.get(
            "intent",
            "unknown"
        )

    except Exception as e:

        predicted = "error"

        print(f"\nERROR: {e}")


    passed = predicted == expected


    if passed:

        correct += 1

        category_results[category]["correct"] += 1

        status = "PASS"

    else:

        status = "FAIL"

        failed_cases.append({
            "query": query,
            "expected": expected,
            "predicted": predicted,
            "category": category
        })


    print(
        f"{index:02d}. "
        f"{status:<4} | "
        f"{category:<15} | "
        f"{query}"
    )

    if not passed:

        print(
            f"    Expected: {expected} | "
            f"Predicted: {predicted}"
        )


# ---------------------------------------------------
# Overall accuracy
# ---------------------------------------------------

accuracy = (
    correct / total * 100
    if total > 0
    else 0
)


print("\n" + "=" * 80)

print("OVERALL RESULTS")

print("=" * 80)

print(f"Total test cases : {total}")
print(f"Correct          : {correct}")
print(f"Incorrect        : {total - correct}")
print(f"Accuracy         : {accuracy:.2f}%")


# ---------------------------------------------------
# Category accuracy
# ---------------------------------------------------

print("\n" + "=" * 80)

print("CATEGORY RESULTS")

print("=" * 80)


for category, result in category_results.items():

    category_accuracy = (
        result["correct"]
        / result["total"]
        * 100
    )

    print(
        f"{category:<18} "
        f"{result['correct']:>2}/"
        f"{result['total']:<2} "
        f"({category_accuracy:6.2f}%)"
    )


# ---------------------------------------------------
# Failed cases
# ---------------------------------------------------

print("\n" + "=" * 80)

print("FAILED TEST CASES")

print("=" * 80)


if not failed_cases:

    print("No failed test cases.")

else:

    for number, failure in enumerate(
        failed_cases,
        start=1
    ):

        print(f"\nFailure {number}")

        print(
            f"Query     : "
            f"{failure['query']}"
        )

        print(
            f"Category  : "
            f"{failure['category']}"
        )

        print(
            f"Expected  : "
            f"{failure['expected']}"
        )

        print(
            f"Predicted : "
            f"{failure['predicted']}"
        )


print("\n" + "=" * 80)