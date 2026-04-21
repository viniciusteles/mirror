[< Plan](plan.md)

# CV5.E2.S2 — Test Guide — Safe DB Startup Under Concurrency

## Automated

- targeted concurrency regression test for `get_connection()` / `MemoryClient()`

## Targeted Assertions

- concurrent opens against a fresh DB complete without migration integrity errors
- repeated opens against an existing DB remain clean
