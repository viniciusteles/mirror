"""Entrypoint for the with-src fixture extension.

Deliberately imports a sibling module via `from src.greet import hello`
with no sys.path manipulation. The loader is expected to make this work.
"""

from src.greet import hello


def cmd_say(api, args):
    print(hello())
    return 0


def register(api):
    api.register_cli("say", cmd_say, summary="Say hi from src/greet.py")
