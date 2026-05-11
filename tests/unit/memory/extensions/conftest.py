"""Shared fixtures for the extension-system test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def hello_fixture_dir() -> Path:
    """Absolute path to the ext-hello fixture extension."""
    return FIXTURES_DIR / "ext-hello"


@pytest.fixture
def with_src_fixture_dir() -> Path:
    """Absolute path to the ext-with-src fixture: an extension that
    imports helpers via ``from src.greet import hello`` with no
    sys.path prelude. Used to prove the loader adds the extension
    root to sys.path automatically."""
    return FIXTURES_DIR / "ext-with-src"


@pytest.fixture(autouse=True)
def _clear_loader_cache():
    """Each test starts with an empty loader cache.

    The loader memoizes loaded extensions by absolute directory path,
    which is great for production (one import per process) but harms
    test isolation: two tests pointing at the same fixture would share
    the same ExtensionAPI instance, including its CLI registry. Clearing
    the cache at the boundary of every test keeps the registries fresh.
    """
    from memory.extensions.loader import clear_load_cache

    clear_load_cache()
    yield
    clear_load_cache()
