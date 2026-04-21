"""Inspect and validate external skill extensions."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from memory.config import default_extensions_dir_for_home, resolve_mirror_home

_ALLOWED_KINDS = {"prompt-skill", "command-skill"}
_RUNTIME_NAME_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
_SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ExtensionValidationError(ValueError):
    """Raised when a skill manifest is invalid."""


def resolve_extensions_root(
    extensions_root: str | Path | None = None,
    *,
    mirror_home: str | Path | None = None,
) -> Path:
    if extensions_root is not None:
        return Path(extensions_root).expanduser()
    if mirror_home is not None:
        return default_extensions_dir_for_home(Path(mirror_home).expanduser())
    return default_extensions_dir_for_home(resolve_mirror_home())


def _load_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ExtensionValidationError(f"missing manifest: {path}") from exc
    except yaml.YAMLError as exc:
        raise ExtensionValidationError(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ExtensionValidationError(f"manifest must be a mapping: {path}")
    return data


def _validate_runtime_name(name: str) -> None:
    if not _RUNTIME_NAME_RE.fullmatch(name):
        raise ExtensionValidationError(f"invalid runtime name: {name}")


def _validate_command_name(runtime: str, command_name: str) -> None:
    if runtime == "claude" and not command_name.startswith("ext:"):
        raise ExtensionValidationError(f"runtime '{runtime}' command_name must start with 'ext:'")
    if runtime == "pi" and not command_name.startswith("ext-"):
        raise ExtensionValidationError(f"runtime '{runtime}' command_name must start with 'ext-'")


def load_extension_manifest(extension_dir: Path) -> dict:
    manifest_path = extension_dir / "skill.yaml"
    data = _load_yaml(manifest_path)

    for field in ("id", "name", "category", "kind", "summary", "runtimes"):
        if not data.get(field):
            raise ExtensionValidationError(f"missing required field '{field}' in {manifest_path}")

    skill_id = data["id"]
    if not isinstance(skill_id, str) or not _SKILL_ID_RE.fullmatch(skill_id):
        raise ExtensionValidationError(f"invalid skill id '{skill_id}' in {manifest_path}")

    if data["category"] != "extension":
        raise ExtensionValidationError(
            f"unsupported category '{data['category']}' in {manifest_path}"
        )

    kind = data["kind"]
    if kind not in _ALLOWED_KINDS:
        raise ExtensionValidationError(f"unsupported kind '{kind}' in {manifest_path}")

    runtimes = data["runtimes"]
    if not isinstance(runtimes, dict) or not runtimes:
        raise ExtensionValidationError(f"runtimes must be a non-empty mapping in {manifest_path}")

    entrypoint = data.get("entrypoint")
    if kind == "command-skill":
        if not isinstance(entrypoint, dict) or not entrypoint.get("command"):
            raise ExtensionValidationError(
                f"command-skill requires entrypoint.command in {manifest_path}"
            )

    validated_runtimes: dict[str, dict] = {}
    for runtime_name, runtime_data in runtimes.items():
        if not isinstance(runtime_name, str):
            raise ExtensionValidationError(f"runtime names must be strings in {manifest_path}")
        _validate_runtime_name(runtime_name)
        if not isinstance(runtime_data, dict):
            raise ExtensionValidationError(
                f"runtime '{runtime_name}' must map to an object in {manifest_path}"
            )

        command_name = runtime_data.get("command_name")
        if not isinstance(command_name, str) or not command_name:
            raise ExtensionValidationError(
                f"runtime '{runtime_name}' missing command_name in {manifest_path}"
            )
        _validate_command_name(runtime_name, command_name)

        validated_runtime = dict(runtime_data)
        if kind == "prompt-skill":
            skill_file = runtime_data.get("skill_file")
            if not isinstance(skill_file, str) or not skill_file:
                raise ExtensionValidationError(
                    f"prompt-skill runtime '{runtime_name}' missing skill_file in {manifest_path}"
                )
            skill_path = extension_dir / skill_file
            if not skill_path.exists():
                raise ExtensionValidationError(
                    f"runtime '{runtime_name}' skill_file not found: {skill_path}"
                )
            validated_runtime["skill_path"] = str(skill_path)

        validated_runtimes[runtime_name] = validated_runtime

    validated = dict(data)
    validated["root"] = str(extension_dir)
    validated["manifest_path"] = str(manifest_path)
    validated["runtimes"] = validated_runtimes
    return validated


def discover_extensions(extensions_root: Path) -> tuple[list[dict], list[tuple[str, str]]]:
    if not extensions_root.exists():
        return [], []

    manifests: list[dict] = []
    errors: list[tuple[str, str]] = []
    for child in sorted(extensions_root.iterdir()):
        if not child.is_dir():
            continue
        manifest_path = child / "skill.yaml"
        if not manifest_path.exists():
            continue
        try:
            manifests.append(load_extension_manifest(child))
        except ExtensionValidationError as exc:
            errors.append((child.name, str(exc)))
    return manifests, errors


def _parse_args(args: list[str]) -> tuple[Path | None, str | None, list[str]]:
    extensions_root = None
    mirror_home = None
    positional: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--extensions-root" and i + 1 < len(args):
            extensions_root = Path(args[i + 1]).expanduser()
            i += 2
        elif args[i] == "--mirror-home" and i + 1 < len(args):
            mirror_home = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1
    return extensions_root, mirror_home, positional


def cmd_extensions(args: list[str]) -> None:
    """python -m memory extensions [list|validate] [--mirror-home PATH] [--extensions-root PATH]"""
    extensions_root, mirror_home, positional = _parse_args(args)
    command = positional[0] if positional else "list"
    if command not in {"list", "validate"}:
        print(
            "Usage: python -m memory extensions [list|validate] [--mirror-home PATH] [--extensions-root PATH]"
        )
        sys.exit(1)

    root = resolve_extensions_root(extensions_root, mirror_home=mirror_home)
    manifests, errors = discover_extensions(root)

    if command == "list":
        print(f"Extensions root: {root}")
        print("=== EXTENSIONS ===")
        if not manifests:
            print("  (none)")
        for manifest in manifests:
            print(f"  {manifest['id']} [{manifest['kind']}]")
            print(f"    name: {manifest['name']}")
            runtime_parts = []
            for runtime_name, runtime_data in sorted(manifest["runtimes"].items()):
                runtime_parts.append(f"{runtime_name}={runtime_data['command_name']}")
            print(f"    runtimes: {', '.join(runtime_parts)}")
        if errors:
            print("\n=== INVALID EXTENSIONS ===")
            for ext_id, message in errors:
                print(f"  {ext_id}: {message}")
        return

    print(f"Extensions root: {root}")
    if errors:
        print("=== INVALID EXTENSIONS ===")
        for ext_id, message in errors:
            print(f"  {ext_id}: {message}")
        sys.exit(1)
    print(f"Validated {len(manifests)} extension(s).")
