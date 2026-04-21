"""Bootstrap a user home from repository identity templates."""

import argparse
import shutil
from pathlib import Path


def find_templates_identity_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__).resolve()).resolve()
    for parent in [current, *current.parents]:
        candidate = parent / "templates" / "identity"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find templates/identity in the repository.")


def default_user_home(user: str, home: Path | None = None) -> Path:
    selected_home = Path(home).expanduser() if home is not None else Path.home()
    return selected_home / ".mirror" / user


def init_user_home(
    user: str,
    *,
    templates_identity_root: Path | None = None,
    user_home: Path | None = None,
) -> Path:
    templates_root = templates_identity_root or find_templates_identity_root()
    if not templates_root.exists():
        raise FileNotFoundError(f"Identity templates not found: {templates_root}")

    destination_home = user_home or default_user_home(user)
    identity_root = destination_home / "identity"

    if identity_root.exists() and any(identity_root.iterdir()):
        raise FileExistsError(f"Identity root already exists and is not empty: {identity_root}")

    destination_home.mkdir(parents=True, exist_ok=True)
    shutil.copytree(templates_root, identity_root, dirs_exist_ok=True)
    return identity_root


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Initialize a user home from identity templates")
    parser.add_argument("user", help="User name for ~/.mirror/<user>")
    args = parser.parse_args(argv)

    identity_root = init_user_home(args.user)
    print(f"Created user home: {identity_root.parent}")
    print(f"Copied templates to: {identity_root}")
    print("Next steps:")
    print(f"  1. Set MIRROR_HOME={identity_root.parent}")
    print(f"  2. Edit files under {identity_root}")
    print("  3. Run: python -m memory seed")


if __name__ == "__main__":
    main()
