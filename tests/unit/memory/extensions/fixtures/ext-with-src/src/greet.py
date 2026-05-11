"""A trivial helper imported from extension.py to prove that `src.*`
imports work without any sys.path prelude in the entrypoint."""


def hello() -> str:
    return "hi from src/greet.py"
