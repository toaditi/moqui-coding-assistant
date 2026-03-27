# Moqui Codebase Management

Use this guide to orient before changing a Moqui repository.

## Start from the runtime layout

- `runtime/component/<component>/component.xml` defines the component boundary.
- `entity/`, `service/`, `screen/`, `data/`, `script/`, and `src/` together describe most application behavior.
- `build.gradle` defines repo-wide operational commands such as runtime setup, component retrieval, load tasks, and deploy tasks.

## Repo-management sequence

1. Identify the backend root and target component.
2. Read `component.xml` plus the nearest neighboring artifact before editing.
3. Check whether the change belongs in an existing component or a new one.
4. Inspect related build or runtime tasks before proposing operational steps.
5. Prefer component-scoped verification and change summaries over repo-wide assumptions.

## Use the inventory script

- `python3 ../../scripts/moqui_repo_inventory.py summary --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py components --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py integrations --root "<backend-root>"`
- `python3 ../../scripts/moqui_repo_inventory.py ops --root "<backend-root>"`
