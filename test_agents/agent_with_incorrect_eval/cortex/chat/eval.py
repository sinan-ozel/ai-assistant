"""Incorrect eval suite with a deliberate NameError."""

eval(repeat=2, threshold=1)


def greets_user():
    """Agent should respond warmly to a greeting."""
    with question("Hello!"):
        expekt(r"(?i)hi|hello|hey")  # noqa: F821 — intentional typo: NameError


def answers_simple_math():
    """Agent should correctly compute 2 + 2."""
    with question("What is 2 + 2?"):
        expect(r"\b4\b|four")
