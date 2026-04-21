"""Parse tasks from journey path Markdown checkboxes."""

import re


def _task_payload(title: str, stage: str | None, status: str, journey: str) -> dict:
    return {
        "title": title,
        "stage": stage,
        "status": status,
        "journey": journey,
    }


def parse_journey_path_tasks(journey_path: str, journey: str) -> list[dict]:
    """Extract pending tasks from unchecked journey path checkboxes.

    Returns dicts with English keys.
    """
    tasks = []
    current_stage = None

    for line in journey_path.split("\n"):
        # Detect current stage (### Stage N: ...). Legacy paths may still use "Etapa".
        stage_match = re.match(r"###\s+(?:Etapa\s+\d+:\s*)?(.+?)(?:\s*[✅🚧⏸])?$", line.strip())
        if stage_match:
            raw_stage = stage_match.group(1).strip()
            # Ignore completed stages.
            if "✅" in line:
                current_stage = None
                continue
            current_stage = raw_stage

        # Detect cycle/block lines.
        cycle_match = re.match(r"\*\*(.+?)(?:\s*[✅🚧⏸])?\s*:?\*\*", line.strip())
        if cycle_match and "✅" in line:
            # Completed cycle, skip tasks inside it.
            current_stage = None
            continue
        elif cycle_match and current_stage is None:
            # Active cycle inside the current stage.
            pass

        # Extract unchecked checkbox.
        checkbox_match = re.match(r"\s*-\s*\[\s*\]\s+(.+)", line)
        if checkbox_match and current_stage is not None:
            title = checkbox_match.group(1).strip()
            # Clean Markdown formatting from the title.
            title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)
            # Remove trailing punctuation while keeping useful markers.
            title = title.rstrip(".")

            tasks.append(_task_payload(title, current_stage, "todo", journey))

    return tasks


def parse_done_tasks(journey_path: str, journey: str) -> list[dict]:
    """Extract completed tasks from checked journey path checkboxes.

    Returns dicts with English keys.
    """
    tasks = []
    current_stage = None

    for line in journey_path.split("\n"):
        # Detect stage (### ...).
        stage_match = re.match(r"###\s+(?:Etapa\s+\d+:\s*)?(.+?)(?:\s*[✅🚧⏸])?$", line.strip())
        if stage_match:
            current_stage = stage_match.group(1).strip()

        # Extract checked checkbox.
        checkbox_match = re.match(r"\s*-\s*\[x\]\s+(.+)", line, re.IGNORECASE)
        if checkbox_match:
            title = checkbox_match.group(1).strip()
            title = re.sub(r"\*\*(.+?)\*\*", r"\1", title)
            title = title.rstrip(".")

            tasks.append(_task_payload(title, current_stage, "done", journey))

    return tasks
