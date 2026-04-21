"""Tests for parsing tasks from journey-path markdown."""

from memory.cli.tasks import parse_done_tasks, parse_journey_path_tasks

JOURNEY = "reflexo"


class TestParseJourneyPathTasks:
    def test_basic_checkbox_extracted(self):
        journey_path = """
### Etapa 1: Início
- [ ] Task simples
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task simples"
        assert tasks[0]["status"] == "todo"
        assert tasks[0]["journey"] == JOURNEY

    def test_stage_assigned_correctly(self):
        # The regex strips the "Etapa N:" prefix — only the label is captured
        journey_path = """
### Etapa 2: Desenvolvimento
- [ ] Implementar feature
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert tasks[0]["stage"] == "Desenvolvimento"

    def test_multiple_tasks_under_same_stage(self):
        journey_path = """
### Etapa 1: Planejamento
- [ ] Task A
- [ ] Task B
- [ ] Task C
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 3
        assert all(t["stage"] == "Planejamento" for t in tasks)

    def test_tasks_under_different_stages(self):
        journey_path = """
### Etapa 1: Início
- [ ] Alpha

### Etapa 2: Meio
- [ ] Beta
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 2
        assert tasks[0]["title"] == "Alpha"
        assert tasks[1]["title"] == "Beta"
        assert tasks[0]["stage"] != tasks[1]["stage"]

    def test_done_checkbox_ignored(self):
        journey_path = """
### Etapa 1: Início
- [x] Já feito
- [ ] Pendente
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Pendente"

    def test_completed_stage_skipped(self):
        journey_path = """
### Etapa 1: Completa ✅
- [ ] Não deve ser extraída

### Etapa 2: Ativa
- [ ] Deve ser extraída
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Deve ser extraída"

    def test_markdown_bold_stripped_from_title(self):
        journey_path = """
### Etapa 1: Início
- [ ] **Título em negrito**
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert tasks[0]["title"] == "Título em negrito"

    def test_trailing_period_stripped(self):
        journey_path = """
### Etapa 1: Início
- [ ] Task com ponto final.
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert tasks[0]["title"] == "Task com ponto final"

    def test_task_without_stage_not_extracted(self):
        """Tasks before any ### heading should not be extracted."""
        journey_path = "- [ ] Task sem etapa\n"
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 0

    def test_empty_journey_path(self):
        tasks = parse_journey_path_tasks("", JOURNEY)
        assert tasks == []

    def test_no_tasks_in_journey_path(self):
        journey_path = """
### Etapa 1: Planejamento
Apenas texto descritivo, sem checkboxes.
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert tasks == []

    def test_indented_checkbox_extracted(self):
        journey_path = """
### Etapa 1: Início
    - [ ] Task indentada
"""
        tasks = parse_journey_path_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1

    def test_journey_set_on_all_tasks(self):
        journey_path = """
### Etapa 1
- [ ] Task A
- [ ] Task B
"""
        tasks = parse_journey_path_tasks(journey_path, "minha-journey")
        assert all(t["journey"] == "minha-journey" for t in tasks)
        assert all(t["journey"] == "minha-journey" for t in tasks)


class TestParseDoneTasks:
    def test_basic_done_checkbox_extracted(self):
        journey_path = """
### Etapa 1: Concluída
- [x] Task feita
"""
        tasks = parse_done_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task feita"
        assert tasks[0]["status"] == "done"
        assert tasks[0]["journey"] == JOURNEY

    def test_uppercase_X_matches(self):
        journey_path = """
### Etapa 1
- [X] Feita com X maiúsculo
"""
        tasks = parse_done_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1

    def test_open_checkbox_ignored(self):
        journey_path = """
### Etapa 1
- [ ] Pendente
- [x] Concluída
"""
        tasks = parse_done_tasks(journey_path, JOURNEY)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Concluída"

    def test_stage_assigned(self):
        # "Etapa N:" prefix is stripped by the regex
        journey_path = """
### Etapa 3: Entrega
- [x] Deploy feito
"""
        tasks = parse_done_tasks(journey_path, JOURNEY)
        assert tasks[0]["stage"] == "Entrega"

    def test_bold_stripped(self):
        journey_path = """
### Etapa 1
- [x] **Concluída em negrito**
"""
        tasks = parse_done_tasks(journey_path, JOURNEY)
        assert tasks[0]["title"] == "Concluída em negrito"

    def test_trailing_period_stripped(self):
        journey_path = """
### Etapa 1
- [x] Feita com ponto.
"""
        tasks = parse_done_tasks(journey_path, JOURNEY)
        assert tasks[0]["title"] == "Feita com ponto"

    def test_empty_returns_empty(self):
        assert parse_done_tasks("", JOURNEY) == []

    def test_both_parsers_together(self):
        """parse_journey_path_tasks and parse_done_tasks should split correctly."""
        journey_path = """
### Etapa 1: Sprint
- [x] Task concluída
- [ ] Task pendente
"""
        pending = parse_journey_path_tasks(journey_path, JOURNEY)
        done = parse_done_tasks(journey_path, JOURNEY)
        assert len(pending) == 1
        assert len(done) == 1
        assert pending[0]["status"] == "todo"
        assert done[0]["status"] == "done"
