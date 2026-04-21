"""Tests for the English-only public Python API."""

import pytest


def test_memory_client_is_primary_public_client():
    import memory
    import memory.client
    from memory import MemoryClient
    from memory.client import MemoryClient as ModuleMemoryClient

    assert MemoryClient is ModuleMemoryClient
    assert not hasattr(memory, "MemoriaClient")
    assert not hasattr(memory.client, "MemoriaClient")


def test_memory_services_export_only_english_primary_names():
    import memory.services as services
    from memory.services import (
        AttachmentService,
        ConversationService,
        IdentityService,
        JourneyService,
        MemoryService,
        TaskService,
    )

    assert services.AttachmentService is AttachmentService
    assert services.ConversationService is ConversationService
    assert services.IdentityService is IdentityService
    assert services.JourneyService is JourneyService
    assert services.MemoryService is MemoryService
    assert services.TaskService is TaskService

    assert not hasattr(services, "AnexoService")
    assert not hasattr(services, "IdentidadeService")
    assert not hasattr(services, "TarefaService")
    assert not hasattr(services, "TravessiaService")


def test_service_modules_do_not_export_portuguese_aliases():
    import memory.services.attachment as attachment
    import memory.services.identity as identity
    import memory.services.journey as journey
    import memory.services.tasks as tasks

    assert not hasattr(attachment, "AnexoService")
    assert not hasattr(identity, "IdentidadeService")
    assert not hasattr(journey, "TravessiaService")
    assert not hasattr(tasks, "TarefaService")


def test_memory_travessia_module_removed():
    with pytest.raises(ModuleNotFoundError):
        __import__("memory.services.travessia")


def test_memoria_package_removed():
    with pytest.raises(ModuleNotFoundError):
        __import__("memoria")


def test_memory_search_is_primary_public_search():
    import memory.intelligence.search

    assert hasattr(memory.intelligence.search, "MemorySearch")
    assert not hasattr(memory.intelligence.search, "MemoriaSearch")
