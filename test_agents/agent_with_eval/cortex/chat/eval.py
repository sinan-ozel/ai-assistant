"""Basic greeting evaluation suite."""

eval(repeat=2, threshold=1)


def greets_user():
    """Agent should respond warmly to a greeting."""
    with question("Hello!"):
        expect(r"(?i)hi|hello|hey|greet|good\s+\w+|welcome|assist")


def answers_simple_math():
    """Agent should correctly compute 2 + 2."""
    with question("What is 2 + 2?"):
        expect(r"\b4\b|four")


def remembers_context():
    assume("My name is Alice.")
    with question("What is my name?"):
        expect(r"(?i)\bAlice\b")
