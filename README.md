# Mirror Mind

![A person reviews a blueprint with one lead contractor while a coordinated specialist team builds different parts of a house behind them, representing Mirror Mind as one unified AI interface with many expert lenses.](docs/assets/mirror-mind-contractor-team-1200px.jpg)

Imagine hiring a contractor to build a house. A good contractor doesn't show up
alone — they bring a team: the architect, the structural engineer, the
electrician, the plumber, the finish carpenter. Each one is exceptional in their
domain. They've worked together before. They hand off cleanly. You talk to one
person; the coordination is their problem, not yours.

Mirror Mind gives you that team for knowledge work. A strategist for business
decisions. An engineer for code. A therapist for the tensions underneath the
surface. A writer for the moments when voice matters. A researcher when you need
to go deep. Each activated by context, each exceptional in their domain, all
speaking with one unified voice — because they're all expressions of the same
intelligence: yours.

The AI tools most people use today are the equivalent of hiring contractors one
at a time, separately, with no shared context. Each one starts cold. They don't
know what the others decided. They don't know your constraints, your past
decisions, your current stage. You are the coordinator — doing the integration
work that should not be yours to do.

Mirror Mind changes this. Your team is briefed on your projects. They know where
you are in each one, what's been decided, what's unresolved. The second session
is faster than the first. The tenth is faster still. They don't start from zero
— because they were there.

And over time, something deeper happens. The team doesn't just know your
projects. They know you — your values, your patterns of thinking, your recurring
tensions, your voice. Every conversation is analyzed and the signal is
extracted: decisions, insights, commitments. The intelligence accumulates. The
reflection sharpens.

This is not a chatbot with memory. This is a mirror — conscious, accumulative,
and yours.

---

## How It Works

Local-first. SQLite. Four supported runtimes: Pi, Gemini CLI, Codex, Claude
Code. One Python core. Jungian architecture: Self, Ego, Personas, Shadow. The
identity lives in your machine, not a server.

→ Get started in ten minutes: [Getting Started](docs/getting-started.md)  
→ Full command reference: [REFERENCE.md](REFERENCE.md)

---

## Origins and Credits

Mirror Mind is a continuation of the original mirror work created by **Alisson
Vale** in
[alissonvale/mirror-poc](https://github.com/alissonvale/mirror-poc/).
This repository extends that foundation for English-speaking users, Pi-based
multi-model use, and stronger multi-user and multi-session runtime behavior.

The move toward **Pi** was inspired by **Henrique Bastos** and his early work
in [henriquebastos/mirror-mind](https://github.com/henriquebastos/mirror-mind),
which showed a strong path toward a more model-flexible runtime.

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package
  manager (handles Python 3.10+)
- [OpenRouter](https://openrouter.ai) account with at least $5 in credits —
  embeddings, memory extraction, and multi-LLM
- An AI runtime subscription:
  [Codex Plus](https://openai.com/codex/) (recommended),
  [Claude Code Pro](https://code.claude.com/docs), or
  [Gemini AI Pro](https://geminicli.com/)
- [Pi](https://github.com/earendil-works/pi/tree/main/packages/coding-agent)
  — recommended harness (multi-model, not locked to one provider)

---

## Documentation

- [Getting Started](docs/getting-started.md) — step-by-step onboarding for new users
- [REFERENCE.md](REFERENCE.md) — command reference and configuration
- [Architecture](docs/architecture.md) — system design, layers, and data model
- [Python API](docs/api.md) — programmatic interface for developers
- [Project Briefing](docs/project/briefing.md) — foundational architectural decisions
- [Decisions](docs/project/decisions.md) — incremental decision log
- [Roadmap](docs/project/roadmap/index.md) — current and planned capability values
- [Development Guide](docs/process/development-guide.md) — how to work on this codebase

---

## License

MIT
