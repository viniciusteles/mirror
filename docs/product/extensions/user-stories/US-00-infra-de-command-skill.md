# US-00 — Infra de `command-skill`

## Story

**Como** mantenedor do Mirror Mind,
**quero** uma infraestrutura que permita carregar extensions com estado
(schema próprio, CLI próprio, integração com Mirror Mode),
**para que** features específicas de um usuário (finanças, depoimentos,
integrações) possam viver fora do core sem perder acesso à infraestrutura
compartilhada (banco, embeddings, LLM, personas).

### Por que agora

O Mirror Mind tem hoje um único tipo de extension (`prompt-skill`), que só
serve para orquestrar comandos shell. Features que precisam de persistência,
schema próprio e integração com Mirror Mode não têm onde morar — ou viram
código no core (errado, mistura framework com identidade pessoal), ou ficam
fora do mirror inteiramente (errado, perdem acesso a embeddings, LLM router,
persona routing).

A primeira motivação concreta são duas features que existiam no mirror legado
(`~/Code/mirror-poc/`) e cujos dados ainda estão preservados no DB antigo: o
módulo de finanças (18 contas, 554 transações, 68 snapshots, 41 contas
recorrentes) e o de depoimentos (5 registros com embeddings). Sem esta
infraestrutura, nenhuma das duas pode voltar.

### Valor de aceitação

Ao fim desta story, um autor de extension consegue:

1. Criar um repositório com um `skill.yaml`, um `extension.py`, uma
   migration SQL e um `SKILL.md`.
2. Rodar `python -m memory extensions install <id>` — o mirror copia o
   tree, roda as migrations, importa o entrypoint, chama `register(api)`.
3. Rodar `python -m memory ext <id> <subcomando>` — o subcomando registrado
   executa.
4. Rodar `python -m memory ext <id> bind <capability> --persona <p>` — o
   binding é persistido.
5. Em uma sessão Mirror Mode com a persona `p` ativa, o texto retornado
   pelo provider aparece no prompt.

## Plan

### Arquivos novos

```
src/memory/extensions/
  __init__.py
  api.py
  loader.py
  migrations.py
  context.py
  testing.py
  errors.py

src/memory/cli/
  ext.py

tests/extensions/
  __init__.py
  conftest.py
  test_api.py
  test_loader.py
  test_migrations.py
  test_context.py
  test_cli_dispatch.py
  test_mirror_mode_hook.py
  fixtures/
    ext-hello/
      skill.yaml
      SKILL.md
      extension.py
      migrations/001_init.sql
```

### Arquivos alterados

- `src/memory/__main__.py` — adicionar dispatch de `ext` para
  `memory.cli.ext.cmd_ext`.
- `src/memory/cli/extensions.py` — após copiar o source tree, chamar
  `loader.install(...)` que dispara migrations e `register`.
- `src/memory/services/identity.py` — em `load_mirror_context`, após
  resolver persona, chamar `context.collect_for_persona(persona_id,
  journey_id, query)` e anexar o resultado ao prompt sob seções
  `=== extension/<id>/<capability> ===`.
- `src/memory/db/schema.py` — adicionar criação de `_ext_migrations` e
  `_ext_bindings` (idempotente, no bootstrap).
- `AGENTS.md` — nova seção curta "Extensions" apontando para
  `docs/product/extensions/`.

### Sequência sugerida de implementação (TDD)

1. **Errors + API skeleton.** Tipos de exceção + assinatura do
   `ExtensionAPI` sem implementação. Teste que importa, instancia (mock),
   verifica tipos.
2. **Schema bootstrap.** `_ext_migrations` e `_ext_bindings` criadas no
   bootstrap do DB. Teste lê `sqlite_master` e confirma.
3. **Migrations runner.** Aplica arquivos em ordem, checksum, prefix
   enforcement, idempotência. Testes cobrem: aplica do zero, re-aplica
   (skip), checksum mismatch (erro), prefix violation (erro), DML em
   tabela própria (ok), DML em tabela alheia (erro).
4. **API DB methods.** `execute`, `read`, `executemany`, `transaction`.
   Testes: write fora do prefixo é rejeitado, read em qualquer tabela
   permitido, transaction rollback funciona.
5. **API embeddings e LLM.** Wrappers finos sobre
   `intelligence.embeddings` e `intelligence.llm_router`. Testes com
   mocks.
6. **Loader.** Descobre, valida manifest, importa entrypoint, chama
   `register`. Testes: manifest válido, manifest inválido (cada campo),
   `register` ausente, `register` levanta.
7. **CLI registry e dispatcher.** `register_cli` + `cmd_ext` em
   `memory.cli.ext`. Testes: subcomando registrado executa, subcomando
   inexistente erro claro, `--help` lista subcomandos.
8. **Context registry e bindings.** Tabela `_ext_bindings`, métodos
   `bind`/`unbind`/`bindings`, dispatcher `collect_for_persona`.
   Testes: CRUD, dispatch chama provider, provider levanta é capturado,
   provider retorna None é skip.
9. **Mirror Mode hook.** Integração em `IdentityService.load_mirror_context`.
   Teste end-to-end: instala fixture, binda capability a persona, chama
   `load_mirror_context` com essa persona, confirma texto presente.
10. **Install path completo.** `python -m memory extensions install`
    chama loader que roda migrations e `register`. Teste de integração
    contra o fixture `ext-hello`.
11. **Documentação alinhada.** Reler todos os docs de
    `docs/product/extensions/` e ajustar onde a implementação divergiu.

### Decisões herdadas (não revisitar nesta story)

- Prefixo de tabela forçado `ext_<id>_*`.
- DB compartilhado (uma única `memory.db`).
- Binding modelos `persona` e `journey` em Phase 1; `global` só na schema.
- Bindings não auto-aplicam de `suggested_personas` no install.
- Falha de extension nunca quebra Mirror Mode.
- `prompt-skill` continua funcionando sem mudanças.

## Test Guide

### Casos por componente

#### `errors.py`

- Hierarquia: todos herdam de `ExtensionError`.
- Mensagens incluem `extension_id` quando aplicável.

#### `migrations.py`

- Aplica `001_init.sql` em DB virgem; `_ext_migrations` registra uma linha.
- Re-rodar é no-op.
- Editar `001_init.sql` após aplicado e re-rodar levanta
  `ExtensionMigrationError` com mensagem mencionando checksum.
- Migration com `CREATE TABLE foo` (sem prefixo) é rejeitada antes de
  qualquer SQL rodar.
- Migration com `INSERT INTO ext_hello_pings ...` aplica normalmente.
- Falha no meio do arquivo: nenhuma alteração persiste (transação),
  `_ext_migrations` não atualiza.

#### `api.py`

- `execute("INSERT INTO ext_hello_pings ...")` funciona.
- `execute("INSERT INTO memories ...")` levanta
  `ExtensionPermissionError`.
- `read("SELECT * FROM memories")` funciona.
- `read("UPDATE memories ...")` levanta (read enforcement).
- `transaction()` aninhado reusa.
- `embed("text")` retorna bytes não-vazios (com mock).
- `llm(prompt)` retorna string (com mock).

#### `loader.py`

- Carrega fixture `ext-hello` com sucesso.
- Manifest sem `id` → erro de validação claro.
- Manifest com `kind: command-skill` e sem `entrypoint` → erro.
- `extension.py` sem função `register` → erro.
- `register` que levanta → erro envolvido em `ExtensionLoadError`.

#### `context.py`

- `bind("finances", "financial_summary", "persona", "tesoureira")` cria
  linha em `_ext_bindings`.
- `bind` duplicado é no-op (PK).
- `unbind` remove a linha.
- `bindings("finances")` lista as bindings.
- `collect_for_persona("tesoureira", ...)` chama o provider registrado e
  retorna o texto.
- Provider que levanta: log emitido, texto vazio retornado.
- Provider que retorna `None`: texto vazio, sem warning.

#### `cli.ext`

- `python -m memory ext list` mostra extensions instaladas.
- `python -m memory ext hello ping foo` insere e imprime `ping: foo`.
- `python -m memory ext hello nope` retorna exit code não-zero e mensagem
  clara.
- `python -m memory ext hello --help` lista subcomandos.

#### Mirror Mode hook (end-to-end)

- Instala fixture `ext-hello`.
- Cria persona `tester` na identity (via API direta).
- Binda `hello.greeting` à persona `tester`.
- Insere uma ping.
- Chama `IdentityService.load_mirror_context(persona="tester", ...)`.
- O retorno contém `=== extension/hello/greeting ===` seguido do texto
  produzido pelo provider.

### Edge cases

- Mirror Mode sem persona ativa: nenhum provider é chamado.
- Binding aponta para extension que falhou ao carregar: log uma vez,
  Mirror Mode segue.
- Binding aponta para persona inexistente: nunca dispara (persona nunca
  é roteada).
- Múltiplas extensions com bindings para a mesma persona: todas disparam,
  ordem estável (ordenação por `extension_id, capability_id`).

### Critério de pronto

- [ ] Todos os testes acima passam.
- [ ] `uv run pytest tests/extensions/` verde.
- [ ] `uv run pytest` (suite completa) verde.
- [ ] Fixture `ext-hello` instalável com um único comando.
- [ ] CI verde após push.
- [ ] AGENTS.md atualizado.
- [ ] Nenhum doc em `docs/product/extensions/` em desacordo com o código.
