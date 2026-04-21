"""Unit tests for TaskService."""

import pytest

from memory.models import Task


class TestTaskServiceAddTask:
    def test_returns_task_object(self, task_service):
        task = task_service.add_task(title="Escrever artigo")
        assert isinstance(task, Task)
        assert task.title == "Escrever artigo"

    def test_persisted_in_store(self, task_service, store):
        task = task_service.add_task(title="Revisar rascunho")
        stored = store.get_task(task.id)
        assert stored is not None
        assert stored.id == task.id

    def test_default_source_is_manual(self, task_service):
        task = task_service.add_task(title="T")
        assert task.source == "manual"

    def test_custom_source(self, task_service):
        task = task_service.add_task(title="T", source="conversation")
        assert task.source == "conversation"

    def test_all_optional_fields_preserved(self, task_service, store):
        task = task_service.add_task(
            title="Reunião",
            journey="reflexo",
            due_date="2026-04-20",
            scheduled_at="2026-04-20T14:00",
            time_hint="tarde",
            stage="Etapa 1",
            context="Contexto da reunião",
        )
        stored = store.get_task(task.id)
        assert stored.journey == "reflexo"
        assert stored.due_date == "2026-04-20"
        assert stored.scheduled_at == "2026-04-20T14:00"
        assert stored.time_hint == "tarde"
        assert stored.stage == "Etapa 1"
        assert stored.context == "Contexto da reunião"


class TestTaskServiceListTasks:
    def test_no_filters_returns_all(self, task_service):
        task_service.add_task(title="A")
        task_service.add_task(title="B")
        result = task_service.list_tasks()
        assert len(result) >= 2

    def test_filter_by_journey(self, task_service):
        task_service.add_task(title="A", journey="reflexo")
        task_service.add_task(title="B", journey="outra")
        result = task_service.list_tasks(journey="reflexo")
        assert all(t.journey == "reflexo" for t in result)

    def test_filter_by_status(self, task_service):
        t = task_service.add_task(title="A")
        task_service.complete_task(t.id)
        task_service.add_task(title="B")  # ainda "todo"
        result = task_service.list_tasks(status="done")
        assert all(t.status == "done" for t in result)

    def test_filter_by_status_and_journey(self, task_service):
        t = task_service.add_task(title="A", journey="reflexo")
        task_service.complete_task(t.id)
        task_service.add_task(title="B", journey="outra")
        result = task_service.list_tasks(status="done", journey="reflexo")
        assert all(t.status == "done" and t.journey == "reflexo" for t in result)

    def test_open_only_excludes_done(self, task_service):
        t = task_service.add_task(title="A")
        task_service.complete_task(t.id)
        task_service.add_task(title="B")
        result = task_service.list_tasks(open_only=True)
        assert all(t.status != "done" for t in result)

    def test_open_only_with_journey(self, task_service):
        t = task_service.add_task(title="A", journey="reflexo")
        task_service.complete_task(t.id)
        task_service.add_task(title="B", journey="reflexo")
        result = task_service.list_tasks(journey="reflexo", open_only=True)
        assert all(t.status != "done" for t in result)
        assert all(t.journey == "reflexo" for t in result)


class TestTaskServiceFindTasks:
    def test_finds_by_partial_title(self, task_service):
        task_service.add_task(title="Escrever artigo sobre IA")
        result = task_service.find_tasks("artigo")
        assert len(result) >= 1
        assert any("artigo" in t.title for t in result)

    def test_scoped_to_journey(self, task_service):
        task_service.add_task(title="Artigo X", journey="reflexo")
        task_service.add_task(title="Artigo Y", journey="outra")
        result = task_service.find_tasks("Artigo", journey="reflexo")
        assert all(t.journey == "reflexo" for t in result)

    def test_empty_when_no_match(self, task_service):
        result = task_service.find_tasks("inexistente")
        assert result == []


class TestTaskServiceCompleteTask:
    def test_sets_status_done(self, task_service, store):
        task = task_service.add_task(title="A")
        task_service.complete_task(task.id)
        stored = store.get_task(task.id)
        assert stored.status == "done"

    def test_sets_completed_at(self, task_service, store):
        task = task_service.add_task(title="A")
        task_service.complete_task(task.id)
        stored = store.get_task(task.id)
        assert stored.completed_at is not None


class TestTaskServiceUpdateTask:
    def test_updates_single_field(self, task_service, store):
        task = task_service.add_task(title="Original")
        task_service.update_task(task.id, title="Atualizado")
        stored = store.get_task(task.id)
        assert stored.title == "Atualizado"

    def test_updates_multiple_fields(self, task_service, store):
        task = task_service.add_task(title="A")
        task_service.update_task(task.id, status="doing", due_date="2026-05-01")
        stored = store.get_task(task.id)
        assert stored.status == "doing"
        assert stored.due_date == "2026-05-01"


class TestTaskServiceIngestWeekPlan:
    def test_calls_extract_week_plan(self, task_service, mock_extract_week_plan, mocker):
        from unittest.mock import patch

        with patch(
            "memory.intelligence.extraction.extract_week_plan",
            return_value=[],
        ) as mock_fn:
            task_service.ingest_week_plan("Amanhã reunião às 14h.")
            mock_fn.assert_called_once()

    def test_week_plan_context_uses_journey_layer(self, task_service, identity_service, mocker):
        identity_service.set_identity("journey", "mirror-poc", "# Mirror POC\n**Status:** active")
        mock_fn = mocker.patch(
            "memory.intelligence.extraction.extract_week_plan",
            return_value=[],
        )

        task_service.ingest_week_plan("Plano.")

        assert mock_fn.call_args.args[1] == [
            {"slug": "mirror-poc", "description": "# Mirror POC\n**Status:** active"}
        ]

    def test_returns_items_with_proposed_tasks(self, task_service, mock_extract_week_plan):
        result = task_service.ingest_week_plan("Amanhã reunião às 14h.")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "item" in result[0]

    def test_flags_similar_existing_tasks(self, task_service, mock_extract_week_plan):
        # Criar task existente com mesmo título e due_date
        task_service.add_task(title="Task plana", due_date="2026-04-14")
        result = task_service.ingest_week_plan("Task planejada amanhã.")
        # O mock retorna título "Task planejada" — busca por primeiros 20 chars
        # A task criada tem "Task plana" que é similar nos 20 primeiros chars
        assert "similar_existing" in result[0]

    def test_no_similar_when_no_existing(self, task_service, mock_extract_week_plan):
        result = task_service.ingest_week_plan("Nova task única.")
        assert result[0]["similar_existing"] == []


class TestTaskServiceSaveWeekItems:
    def test_creates_task_for_each_item(self, task_service, mock_extract_week_plan):
        proposed = task_service.ingest_week_plan("Plano semanal.")
        tasks = task_service.save_week_items([p["item"] for p in proposed])
        assert len(tasks) == 1
        assert isinstance(tasks[0], Task)

    def test_source_is_week_plan(self, task_service, mock_extract_week_plan):
        proposed = task_service.ingest_week_plan("Plano.")
        tasks = task_service.save_week_items([p["item"] for p in proposed])
        assert tasks[0].source == "week_plan"

    def test_accepts_dict_format(self, task_service, mock_extract_week_plan):
        proposed = task_service.ingest_week_plan("Plano.")
        # Passa o dict completo com chave "item"
        tasks = task_service.save_week_items(proposed)
        assert len(tasks) == 1


class TestTaskServiceImportTasksFromJourneyPath:
    def test_returns_empty_when_no_journey_path(self, task_service):
        result = task_service.import_tasks_from_journey_path("journey-sem-journey_path")
        assert result == []

    def test_parses_checkboxes(self, task_service, identity_service):
        # O parser requer ### para detectar etapa (current_stage)
        journey_path = "# Journey Path\n### Etapa 1: Início\n- [ ] Task A\n- [ ] Task B\n"
        identity_service.set_identity("journey_path", "minha-journey", journey_path)
        result = task_service.import_tasks_from_journey_path("minha-journey")
        titles = [t.title for t in result]
        assert "Task A" in titles
        assert "Task B" in titles

    def test_deduplicates_existing_tasks(self, task_service, identity_service):
        journey_path = "# Journey Path\n### Etapa 1: Início\n- [ ] Task Única\n"
        identity_service.set_identity("journey_path", "trav", journey_path)
        # Importar duas vezes
        task_service.import_tasks_from_journey_path("trav")
        result2 = task_service.import_tasks_from_journey_path("trav")
        # Segunda importação não cria duplicatas
        assert result2 == []


class TestTaskServiceSyncTasksFromFile:
    def test_raises_when_no_sync_file_configured(self, task_service, identity_service):
        identity_service.set_identity("journey", "trav", "# Trav\n**Status:** active")
        with pytest.raises(ValueError, match="No sync file configured"):
            task_service.sync_tasks_from_file("trav")

    def test_raises_when_file_not_found(self, task_service, identity_service, journey_service):
        identity_service.set_identity("journey", "trav", "# Trav\n**Status:** active")
        journey_service.set_sync_file("trav", "/journey_path/inexistente/arquivo.md")
        with pytest.raises(FileNotFoundError):
            task_service.sync_tasks_from_file("trav")

    def test_creates_new_pending_tasks(
        self, task_service, identity_service, journey_service, store, tmp_path
    ):
        journey_path_file = tmp_path / "journey_path.md"
        journey_path_file.write_text(
            "# Journey Path\n### Etapa 1: Início\n- [ ] Nova task do arquivo\n", encoding="utf-8"
        )
        identity_service.set_identity("journey", "trav", "# Trav\n**Status:** active")
        journey_service.set_sync_file("trav", str(journey_path_file))

        result = task_service.sync_tasks_from_file("trav")
        assert result["created"] == 1
        tasks = store.get_tasks_by_journey("trav")
        assert any(t.title == "Nova task do arquivo" for t in tasks)

    def test_marks_done_in_db_when_done_in_file(
        self, task_service, identity_service, journey_service, store, tmp_path
    ):
        # Criar task no banco
        task_service.add_task(title="Task concluída", journey="trav")

        journey_path_file = tmp_path / "journey_path.md"
        journey_path_file.write_text(
            "# Journey Path\n### Etapa 1: Início\n- [x] Task concluída\n", encoding="utf-8"
        )
        identity_service.set_identity("journey", "trav", "# Trav\n**Status:** active")
        journey_service.set_sync_file("trav", str(journey_path_file))

        result = task_service.sync_tasks_from_file("trav")
        assert result["completed"] == 1
        tasks = store.get_tasks_by_journey("trav")
        assert all(t.status == "done" for t in tasks if t.title == "Task concluída")

    def test_unchanged_count_for_already_synced(
        self, task_service, identity_service, journey_service, store, tmp_path
    ):
        # Task já existe no banco e está pendente no arquivo
        task_service.add_task(title="Já existe", journey="trav")

        journey_path_file = tmp_path / "journey_path.md"
        journey_path_file.write_text(
            "# Journey Path\n### Etapa 1: Início\n- [ ] Já existe\n", encoding="utf-8"
        )
        identity_service.set_identity("journey", "trav", "# Trav\n**Status:** active")
        journey_service.set_sync_file("trav", str(journey_path_file))

        result = task_service.sync_tasks_from_file("trav")
        assert result["created"] == 0
        assert result["unchanged"] == 1
