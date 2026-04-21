"""Extract Claude Code hook prompt text from stdin JSON."""

from __future__ import annotations

import json
import sys


def extract_prompt(raw_input: str) -> str:
    """Return the prompt string from a Claude Code hook JSON payload."""
    try:
        data = json.loads(raw_input)
    except (json.JSONDecodeError, TypeError):
        return ""

    prompt = data.get("prompt", "")
    return prompt if isinstance(prompt, str) else ""


def main() -> None:
    print(extract_prompt(sys.stdin.read()))


if __name__ == "__main__":
    main()
