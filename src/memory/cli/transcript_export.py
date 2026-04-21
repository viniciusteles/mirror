"""Export Claude Code JSONL transcripts to readable Markdown."""

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from memory.config import TRANSCRIPT_EXPORT_DIR, default_transcript_export_dir_for_home


def slugify(text: str, max_len: int = 50) -> str:
    """Generate a slug from text."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rsplit("-", 1)[0]
    return text or "conversation"


def _extract_date(entries: list[dict]) -> str:
    """Extract the first available timestamp date."""
    for entry in entries:
        ts = entry.get("timestamp")
        if ts and entry.get("type") in ("user", "assistant"):
            return ts[:10]
    return datetime.now().strftime("%Y-%m-%d")


def _user_messages(entries: list[dict], limit: int = 10) -> list[str]:
    """Return the first N user text messages, excluding tool results."""
    msgs = []
    for entry in entries:
        if entry.get("type") == "user":
            content = entry.get("message", {}).get("content", "")
            if isinstance(content, str) and content.strip():
                msgs.append(content.strip())
                if len(msgs) >= limit:
                    break
    return msgs


# Common Portuguese words that do not add useful slug signal.
_STOPWORDS = {
    # articles, prepositions, pronouns
    "a",
    "o",
    "e",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "um",
    "uma",
    "uns",
    "umas",
    "que",
    "para",
    "por",
    "com",
    "como",
    "se",
    "me",
    "te",
    "eu",
    "ele",
    "ela",
    "nao",
    "sim",
    "mas",
    "ou",
    "ao",
    "os",
    "as",
    "isso",
    "esse",
    "essa",
    "este",
    "esta",
    "aqui",
    "ali",
    "la",
    "pra",
    "pro",
    "pelo",
    "pela",
    "entre",
    "sobre",
    "ate",
    "sem",
    # pronouns and demonstratives
    "voce",
    "meu",
    "minha",
    "meus",
    "minhas",
    "seu",
    "sua",
    "seus",
    "suas",
    "qual",
    "quais",
    "quem",
    "onde",
    "quando",
    "quanto",
    # common verbs
    "tem",
    "ter",
    "ser",
    "estar",
    "estou",
    "vamos",
    "vai",
    "vou",
    "pode",
    "posso",
    "preciso",
    "quero",
    "queria",
    "acho",
    "faz",
    "fazer",
    "foi",
    "era",
    "tinha",
    "deixa",
    "olhe",
    "veja",
    "mostra",
    "ajude",
    "seria",
    "sera",
    "temos",
    "havia",
    "dizer",
    # adverbs and filler
    "muito",
    "mais",
    "tambem",
    "agora",
    "hoje",
    "ontem",
    "ainda",
    "depois",
    "antes",
    "entao",
    "bem",
    "bom",
    "certeza",
    "algum",
    "alguma",
    # tech filler
    "arquivo",
    "code",
    "docs",
    "nesse",
    "nessa",
    "dessa",
    "desse",
    # additional generic verbs
    "trabalhar",
    "implementar",
    "rodar",
    "gerar",
    "criar",
    "usar",
    "funcionar",
    "resolver",
    "colocar",
    "manter",
    "tornar",
    "retomar",
    "separar",
    "disparar",
    "registrar",
    "comecar",
    "seguir",
    # generic adverbs and adjectives
    "aparentemente",
    "mesmo",
    "outro",
    "outra",
    "novo",
    "nova",
    "ultimo",
    "ultima",
    "proximo",
    "proxima",
    "certo",
    "certa",
}


def _extract_keywords(messages: list[str], max_words: int = 5) -> list[str]:
    """Extract keywords from user messages.

    Uses weighted frequency: longer words that appear in multiple distinct
    messages receive more weight.
    """
    # Count how many distinct messages each word appears in.
    word_msgs: dict[str, set[int]] = {}
    for i, msg in enumerate(messages):
        first_line = msg.split("\n")[0][:200]
        # Ignore paths containing / or ~.
        first_line = re.sub(r"[~/]\S+", "", first_line)
        words = re.findall(r"[a-záàâãéêíóôõúç]+", first_line.lower())
        for w in words:
            normalized = unicodedata.normalize("NFKD", w)
            normalized = normalized.encode("ascii", "ignore").decode("ascii")
            if len(normalized) > 3 and normalized not in _STOPWORDS:
                if normalized not in word_msgs:
                    word_msgs[normalized] = set()
                word_msgs[normalized].add(i)

    # Score: number of distinct messages * length bonus.
    scored = []
    for word, msg_set in word_msgs.items():
        score = len(msg_set) * (1 + len(word) / 10)
        scored.append((word, score))

    scored.sort(key=lambda x: (-x[1], x[0]))
    return [w for w, _ in scored[:max_words]]


def _auto_slug(entries: list[dict]) -> str:
    """Generate a representative slug from user messages."""
    msgs = _user_messages(entries)
    if not msgs:
        return "conversation"
    keywords = _extract_keywords(msgs, max_words=4)
    if keywords:
        return "-".join(keywords)
    # Fallback: first message.
    return slugify(msgs[0])


def _assistant_text(content_blocks: list) -> str:
    """Extract only text blocks from an assistant message."""
    parts = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text", "").strip()
            if text:
                parts.append(text)
    return "\n\n".join(parts)


def _is_command(text: str) -> bool:
    """Check whether text is a command or skill invocation."""
    stripped = text.strip()
    return (
        stripped.startswith("/")
        or stripped.startswith("<command-message>")
        or stripped.startswith("<command-name>")
    )


def parse_jsonl(jsonl_path: str) -> list[dict]:
    """Read JSONL and return entries."""
    entries = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def entries_to_markdown(entries: list[dict]) -> str:
    """Convert transcript entries to Markdown."""
    parts = []
    last_role = None

    for entry in entries:
        etype = entry.get("type")

        if etype == "user":
            raw = entry.get("message", {}).get("content", "")
            if not isinstance(raw, str):
                continue  # tool_results are lists.
            content = raw.strip()
            if not content or _is_command(content):
                continue
            if last_role != "user" or not parts:
                parts.append(f"## Vinícius\n\n{content}")
            else:
                parts.append(content)
            last_role = "user"

        elif etype == "assistant":
            content_blocks = entry.get("message", {}).get("content", [])
            text = _assistant_text(content_blocks)
            if not text:
                continue
            if last_role != "assistant":
                parts.append(f"---\n\n## Claude\n\n{text}")
            else:
                parts.append(text)
            last_role = "assistant"

    return "\n\n".join(parts) + "\n"


def _last_turn(entries: list[dict]) -> list[dict]:
    """Extract the latest user plus assistant turn from the transcript."""
    last_user_idx = None

    for i, entry in enumerate(entries):
        etype = entry.get("type")
        if etype == "user":
            raw = entry.get("message", {}).get("content", "")
            if isinstance(raw, str) and raw.strip() and not _is_command(raw):
                last_user_idx = i

    if last_user_idx is None:
        return []

    # Pegar o user message e todos os assistant messages que vieram depois dele
    turn = []
    for i in range(last_user_idx, len(entries)):
        entry = entries[i]
        etype = entry.get("type")
        if etype == "user" and i > last_user_idx:
            break  # Next user turn starts.
        if etype in ("user", "assistant"):
            turn.append(entry)

    return turn


def _resolve_output_dir(
    output_dir: str | None = None,
    *,
    mirror_home: str | Path | None = None,
) -> Path:
    if output_dir:
        return Path(output_dir).expanduser()
    if mirror_home is not None:
        return default_transcript_export_dir_for_home(Path(mirror_home).expanduser())
    return TRANSCRIPT_EXPORT_DIR


def export_last_turn(
    jsonl_path: str,
    output_dir: str | None = None,
    slug: str | None = None,
    *,
    mirror_home: str | Path | None = None,
) -> str:
    """Export only the latest user plus assistant turn to Markdown.

    Returns: generated file path.
    """
    out_dir = _resolve_output_dir(output_dir, mirror_home=mirror_home)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = parse_jsonl(jsonl_path)
    if not entries:
        return ""

    turn = _last_turn(entries)
    if not turn:
        return ""

    date_str = _extract_date(entries)

    if not slug:
        msgs = _user_messages(turn)
        if msgs:
            slug = slugify(msgs[0])
        else:
            slug = "turn"

    filename = f"{date_str}-{slug}.md"
    out_path = out_dir / filename

    counter = 2
    while out_path.exists():
        out_path = out_dir / f"{date_str}-{slug}-{counter}.md"
        counter += 1

    markdown = entries_to_markdown(turn)
    out_path.write_text(markdown, encoding="utf-8")

    return str(out_path)


def export_transcript(
    jsonl_path: str,
    output_dir: str | None = None,
    slug: str | None = None,
    *,
    mirror_home: str | Path | None = None,
) -> str:
    """Export a JSONL transcript to a Markdown file.

    Returns: generated file path.
    """
    out_dir = _resolve_output_dir(output_dir, mirror_home=mirror_home)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = parse_jsonl(jsonl_path)
    if not entries:
        return ""

    date_str = _extract_date(entries)

    if not slug:
        slug = _auto_slug(entries)

    filename = f"{date_str}-{slug}.md"
    out_path = out_dir / filename

    counter = 2
    while out_path.exists():
        out_path = out_dir / f"{date_str}-{slug}-{counter}.md"
        counter += 1

    markdown = entries_to_markdown(entries)
    out_path.write_text(markdown, encoding="utf-8")

    return str(out_path)
