"""Inspect and validate external skill extensions."""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from memory.config import (
    default_extensions_dir_for_home,
    default_runtime_skills_dir_for_home,
    resolve_mirror_home,
)

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


def _parse_args(
    args: list[str],
) -> tuple[Path | None, str | None, str | None, Path | None, list[str]]:
    extensions_root = None
    mirror_home = None
    runtime = None
    target_root = None
    positional: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--extensions-root" and i + 1 < len(args):
            extensions_root = Path(args[i + 1]).expanduser()
            i += 2
        elif args[i] == "--mirror-home" and i + 1 < len(args):
            mirror_home = args[i + 1]
            i += 2
        elif args[i] == "--runtime" and i + 1 < len(args):
            runtime = args[i + 1]
            i += 2
        elif args[i] == "--target-root" and i + 1 < len(args):
            target_root = Path(args[i + 1]).expanduser()
            i += 2
        else:
            positional.append(args[i])
            i += 1
    return extensions_root, mirror_home, runtime, target_root, positional


def filter_manifests_for_runtime(manifests: list[dict], runtime: str | None) -> list[dict]:
    if runtime is None:
        return manifests
    return [manifest for manifest in manifests if runtime in manifest.get("runtimes", {})]


def print_extension_list(manifests: list[dict], errors: list[tuple[str, str]], root: Path) -> None:
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


def _catalog_entry_for_manifest(manifest: dict, runtime: str, target_skill_path: Path) -> dict:
    runtime_data = manifest["runtimes"][runtime]
    return {
        "id": manifest["id"],
        "name": manifest["name"],
        "category": manifest["category"],
        "kind": manifest["kind"],
        "summary": manifest["summary"],
        "runtime": runtime,
        "command_name": runtime_data["command_name"],
        "source_extension_dir": manifest["root"],
        "manifest_path": manifest["manifest_path"],
        "source_skill_path": runtime_data.get("skill_path", ""),
        "installed_skill_path": str(target_skill_path),
    }


def _catalog_document(runtime: str, target_root: Path, items: list[dict]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "runtime": runtime,
        "target_root": str(target_root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "extensions": items,
    }


def sync_extensions_for_runtime(
    manifests: list[dict], runtime: str, target_root: Path
) -> list[dict[str, str]]:
    target_root.mkdir(parents=True, exist_ok=True)
    synced: list[dict[str, str]] = []

    for manifest in manifests:
        runtime_data = manifest.get("runtimes", {}).get(runtime)
        if not runtime_data:
            continue
        skill_path = runtime_data.get("skill_path")
        if not skill_path:
            continue

        command_name = runtime_data["command_name"]
        target_dir = target_root / command_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_skill_path = target_dir / "SKILL.md"
        shutil.copyfile(skill_path, target_skill_path)
        synced.append(_catalog_entry_for_manifest(manifest, runtime, target_skill_path))

    catalog_path = target_root / "extensions.json"
    _write_catalog(catalog_path, runtime, target_root, synced)
    return synced


def _load_catalog(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1", "extensions": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": "1", "extensions": []}
    if isinstance(data, list):
        return {"schema_version": "0", "extensions": data}
    return data if isinstance(data, dict) else {"schema_version": "1", "extensions": []}


def load_runtime_catalog(runtime: str, mirror_home: Path) -> dict[str, Any]:
    runtime_root = default_runtime_skills_dir_for_home(mirror_home, runtime)
    catalog_path = runtime_root / "extensions.json"
    if not catalog_path.exists():
        raise ExtensionValidationError(f"runtime catalog not found: {catalog_path}")

    catalog = _load_catalog(catalog_path)
    if catalog.get("schema_version") != "1":
        raise ExtensionValidationError(
            f"unsupported runtime catalog schema '{catalog.get('schema_version')}' in {catalog_path}"
        )
    if catalog.get("runtime") != runtime:
        raise ExtensionValidationError(
            f"runtime catalog {catalog_path} does not match runtime '{runtime}'"
        )
    extensions = catalog.get("extensions")
    if not isinstance(extensions, list):
        raise ExtensionValidationError(
            f"invalid runtime catalog extensions payload in {catalog_path}"
        )
    return catalog


def _write_catalog(path: Path, runtime: str, target_root: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_catalog_document(runtime, target_root, items), indent=2) + "\n",
        encoding="utf-8",
    )


def _prune_catalog_for_extension(
    catalog_path: Path, extension_id: str, runtime: str, target_root: Path
) -> None:
    catalog = _load_catalog(catalog_path)
    items = [
        item
        for item in catalog.get("extensions", [])
        if isinstance(item, dict) and item.get("id") != extension_id
    ]
    _write_catalog(catalog_path, runtime, target_root, items)


def install_extension(
    extension_id: str,
    *,
    source_root: Path,
    mirror_home: Path,
    runtime: str | None = None,
) -> dict[str, Any]:
    source_dir = source_root / extension_id
    load_extension_manifest(source_dir)

    target_extensions_root = default_extensions_dir_for_home(mirror_home)
    target_extension_dir = target_extensions_root / extension_id
    target_extensions_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, target_extension_dir, dirs_exist_ok=True)

    installed_manifest = load_extension_manifest(target_extension_dir)
    runtimes = [runtime] if runtime is not None else sorted(installed_manifest["runtimes"].keys())

    synced: dict[str, list[dict[str, str]]] = {}
    for runtime_name in runtimes:
        runtime_target_root = default_runtime_skills_dir_for_home(mirror_home, runtime_name)
        synced[runtime_name] = sync_extensions_for_runtime(
            [installed_manifest], runtime_name, runtime_target_root
        )

    return {
        "extension_id": extension_id,
        "source_dir": str(source_dir),
        "installed_dir": str(target_extension_dir),
        "synced": synced,
    }


def _load_claude_overlay_catalog(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def cleanup_claude_runtime_skills(project_root: Path) -> dict[str, Any]:
    claude_skills_root = project_root / ".claude" / "skills"
    overlay_catalog_path = claude_skills_root / "extensions.external.json"
    removed: list[str] = []

    for item in _load_claude_overlay_catalog(overlay_catalog_path):
        if not isinstance(item, dict):
            continue
        target_skill_path = item.get("target_skill_path")
        if not isinstance(target_skill_path, str):
            continue
        target_path = Path(target_skill_path)
        if target_path.exists():
            target_path.unlink()
            removed.append(str(target_path))
        parent = target_path.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()

    if overlay_catalog_path.exists():
        overlay_catalog_path.unlink()

    return {
        "project_root": str(project_root),
        "claude_skills_root": str(claude_skills_root),
        "overlay_catalog_path": str(overlay_catalog_path),
        "removed": removed,
    }


def expose_claude_runtime_skills(mirror_home: Path, project_root: Path) -> dict[str, Any]:
    catalog = load_runtime_catalog("claude", mirror_home)
    items = catalog.get("extensions", [])
    claude_skills_root = project_root / ".claude" / "skills"
    claude_skills_root.mkdir(parents=True, exist_ok=True)

    cleanup = cleanup_claude_runtime_skills(project_root)

    exposed: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        command_name = item.get("command_name")
        installed_skill_path = item.get("installed_skill_path")
        if not isinstance(command_name, str) or not isinstance(installed_skill_path, str):
            continue
        source_path = Path(installed_skill_path)
        if not source_path.exists():
            continue
        target_dir = claude_skills_root / command_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_skill_path = target_dir / "SKILL.md"
        shutil.copyfile(source_path, target_skill_path)
        exposed.append(
            {
                "command_name": command_name,
                "source_skill_path": str(source_path),
                "target_skill_path": str(target_skill_path),
            }
        )

    overlay_catalog_path = claude_skills_root / "extensions.external.json"
    overlay_catalog_path.write_text(json.dumps(exposed, indent=2) + "\n", encoding="utf-8")
    return {
        "project_root": str(project_root),
        "claude_skills_root": str(claude_skills_root),
        "overlay_catalog_path": str(overlay_catalog_path),
        "removed": cleanup["removed"],
        "exposed": exposed,
    }


def uninstall_extension(
    extension_id: str,
    *,
    mirror_home: Path,
    runtime: str | None = None,
) -> dict[str, Any]:
    installed_dir = default_extensions_dir_for_home(mirror_home) / extension_id
    if not installed_dir.exists():
        raise ExtensionValidationError(f"installed extension not found: {installed_dir}")

    manifest = load_extension_manifest(installed_dir)
    runtimes = [runtime] if runtime is not None else sorted(manifest["runtimes"].keys())

    removed: dict[str, list[str]] = {}
    for runtime_name in runtimes:
        runtime_data = manifest["runtimes"].get(runtime_name)
        if not runtime_data:
            removed[runtime_name] = []
            continue
        runtime_root = default_runtime_skills_dir_for_home(mirror_home, runtime_name)
        command_name = runtime_data["command_name"]
        target_dir = runtime_root / command_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        _prune_catalog_for_extension(
            runtime_root / "extensions.json", extension_id, runtime_name, runtime_root
        )
        removed[runtime_name] = [str(target_dir)]

    if runtime is None and installed_dir.exists():
        shutil.rmtree(installed_dir)

    return {
        "extension_id": extension_id,
        "installed_dir": str(installed_dir),
        "removed": removed,
        "source_removed": runtime is None,
    }


def cmd_extensions(args: list[str]) -> None:
    """python -m memory extensions [list|validate|sync|install|uninstall|expose-claude|clean-claude] [--mirror-home PATH] [--extensions-root PATH] [--runtime NAME] [--target-root PATH]"""
    extensions_root, mirror_home, runtime, target_root, positional = _parse_args(args)
    command = positional[0] if positional else "list"
    if command not in {
        "list",
        "validate",
        "sync",
        "install",
        "uninstall",
        "expose-claude",
        "clean-claude",
    }:
        print(
            "Usage: python -m memory extensions [list|validate|sync|install|uninstall|expose-claude|clean-claude] [--mirror-home PATH] [--extensions-root PATH] [--runtime NAME] [--target-root PATH]"
        )
        sys.exit(1)

    if command == "install":
        if len(positional) != 2:
            print(
                "Usage: python -m memory extensions install <id> [--extensions-root PATH] [--mirror-home PATH] [--runtime NAME]"
            )
            sys.exit(1)
        if mirror_home is None:
            print("install requires --mirror-home PATH")
            sys.exit(1)
        if extensions_root is None:
            print("install requires --extensions-root PATH")
            sys.exit(1)

        result = install_extension(
            positional[1],
            source_root=extensions_root,
            mirror_home=Path(mirror_home).expanduser(),
            runtime=runtime,
        )
        print(f"Installed extension/{result['extension_id']}")
        print(f"  source: {result['source_dir']}")
        print(f"  installed: {result['installed_dir']}")
        for runtime_name, items in result["synced"].items():
            print(f"  runtime {runtime_name}:")
            for item in items:
                print(f"    {item['command_name']} -> {item['installed_skill_path']}")
        return

    if command == "uninstall":
        if len(positional) != 2:
            print(
                "Usage: python -m memory extensions uninstall <id> [--mirror-home PATH] [--runtime NAME]"
            )
            sys.exit(1)
        if mirror_home is None:
            print("uninstall requires --mirror-home PATH")
            sys.exit(1)
        try:
            result = uninstall_extension(
                positional[1],
                mirror_home=Path(mirror_home).expanduser(),
                runtime=runtime,
            )
        except ExtensionValidationError as exc:
            print(str(exc))
            sys.exit(1)
        print(f"Uninstalled extension/{result['extension_id']}")
        print(f"  installed: {result['installed_dir']}")
        if result["source_removed"]:
            print("  source tree: removed")
        for runtime_name, items in result["removed"].items():
            print(f"  runtime {runtime_name}:")
            for item in items:
                print(f"    removed {item}")
        return

    if command == "expose-claude":
        if mirror_home is None:
            print("expose-claude requires --mirror-home PATH")
            sys.exit(1)
        project_root = target_root or Path.cwd()
        try:
            result = expose_claude_runtime_skills(
                Path(mirror_home).expanduser(),
                project_root.expanduser(),
            )
        except ExtensionValidationError as exc:
            print(str(exc))
            sys.exit(1)
        print(f"Exposed Claude external skills into {result['claude_skills_root']}")
        print(f"  overlay catalog: {result['overlay_catalog_path']}")
        for removed in result["removed"]:
            print(f"  pruned {removed}")
        for item in result["exposed"]:
            print(f"  {item['command_name']} -> {item['target_skill_path']}")
        return

    if command == "clean-claude":
        project_root = target_root or Path.cwd()
        result = cleanup_claude_runtime_skills(project_root.expanduser())
        print(f"Removed Claude external skills from {result['claude_skills_root']}")
        print(f"  overlay catalog: {result['overlay_catalog_path']}")
        for removed in result["removed"]:
            print(f"  removed {removed}")
        return

    root = resolve_extensions_root(extensions_root, mirror_home=mirror_home)
    manifests, errors = discover_extensions(root)
    manifests = filter_manifests_for_runtime(manifests, runtime)

    if command == "list":
        if runtime is not None:
            print(f"Runtime filter: {runtime}")
        print_extension_list(manifests, errors, root)
        return

    print(f"Extensions root: {root}")
    if runtime is not None:
        print(f"Runtime filter: {runtime}")
    if errors:
        print("=== INVALID EXTENSIONS ===")
        for ext_id, message in errors:
            print(f"  {ext_id}: {message}")
        sys.exit(1)
    if command == "validate":
        print(f"Validated {len(manifests)} extension(s).")
        return

    if runtime is None:
        print("sync requires --runtime")
        sys.exit(1)
    if target_root is None:
        print("sync requires --target-root PATH")
        sys.exit(1)

    synced = sync_extensions_for_runtime(manifests, runtime, target_root)
    print(f"Synced {len(synced)} extension(s) to {target_root}")
    for item in synced:
        print(f"  {item['command_name']} -> {item['installed_skill_path']}")
