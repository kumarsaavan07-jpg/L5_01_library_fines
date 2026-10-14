import ast
import json
import operator
from datetime import datetime

# Global state
loans = {}
FINE_PER_DAY = 2


def add_book_loan(student_id, book_id, dates=None):
    """Record a book loan for a student."""
    if dates is None:
        dates = []

    if not student_id:
        return

    dates.append(str(datetime.now()))
    loans[student_id] = loans.get(student_id, []) + [str(book_id)]

    print(
        "%s borrowed %s (loan dates on record: %d)"
        % (student_id, book_id, len(dates))
    )


def return_book(student_id, book_id):
    """Return a borrowed book if the student has it."""
    if student_id not in loans or book_id not in loans[student_id]:
        return

    loans[student_id].remove(book_id)

    if not loans[student_id]:
        del loans[student_id]


def calculate_fine(days_overdue):
    """Calculate the fine based on overdue days."""
    return max(0, days_overdue) * FINE_PER_DAY


def renew_book(student_id, book_id, extra_days):
    """Renew a borrowed book and update the fine rate if needed."""
    global FINE_PER_DAY

    if extra_days > 14:
        FINE_PER_DAY += 1

    print(
        f"Renewed {book_id} for {student_id} "
        f"by {extra_days} days"
    )


def load_records(file="loans.json"):
    """Load saved loan records from a JSON file."""
    global loans

    try:
        with open(file, "r", encoding="utf-8") as records_file:
            loans = json.load(records_file)
    except FileNotFoundError:
        loans = {}


def save_records(file="loans.json"):
    """Save current loan records to a JSON file."""
    with open(file, "w", encoding="utf-8") as records_file:
        json.dump(loans, records_file, indent=4)


def fine_from_rule(rule, days):
    """Calculate a fine using a restricted arithmetic expression."""
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    expression = rule.replace("days", str(days))
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
        ):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            return operators[type(node.op)](
                evaluate(node.left),
                evaluate(node.right),
            )

        raise ValueError("Unsupported expression")

    return evaluate(tree)


def print_report():
    """Print all current loan records."""
    print("Loan Report")

    for student_id, book_list in loans.items():
        print(student_id, "->", book_list)


def main():
    """Run the library system demonstration."""
    add_book_loan("S101", "B-ALGO")
    add_book_loan("S102", "B-NETW")
    add_book_loan("", "B-DBMS")
    add_book_loan("S103", "4521")

    return_book("S999", "B-NONE")
    renew_book("S101", "B-ALGO", 21)

    print("Fine for 5 days:", calculate_fine(5))
    print("Fine for -3 days:", calculate_fine(-3))
    print("Fine via rule:", fine_from_rule("days * 2 + 10", 4))

    days = input("Days overdue for S102 (press Enter for 0): ") or "0"

    try:
        overdue_days = int(days)
        print("S102 owes:", calculate_fine(overdue_days))
    except ValueError:
        print("Please enter a valid whole number.")
        return

    save_records()
    load_records()
    print_report()


if __name__ == "__main__":
    main()
