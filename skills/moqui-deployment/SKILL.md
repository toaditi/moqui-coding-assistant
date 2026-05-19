---
name: moqui-deployment-operations
description: Guide Moqui build, load, packaging, runtime-embedding, and Tomcat deployment operations using the repository’s actual Gradle tasks. Use when the user asks how to run, load, package, or deploy a Moqui backend, or when operational verification must be tied to backend build tasks.
---

# Moqui Deployment Operations

## Quick start

- `python3 ../../scripts/moqui_repo_inventory.py ops --root "<backend-root>"`

## Procedure

1. Confirm the backend root and whether the task is local build, data load, package creation, or Tomcat deployment.
2. Inspect available Gradle tasks before proposing a command.
3. Choose the narrowest command that matches the intent.
4. State environment assumptions explicitly:
   - runtime directory present or not
   - Tomcat target or not
   - load type required or not
5. After execution or recommendation, report what remains unverified.

## Guardrails

- Do not flatten local-load, package-build, and Tomcat deploy into a single generic “deploy” story.
- Do not invent production infrastructure steps beyond what the repo provides.
- Do not recommend broad load tasks when a narrower seed or packaging task is sufficient.

## References

- Deployment guide: `../../assets/moqui-deployment-operations.md`
- Codebase guide: `../../assets/moqui-codebase-management.md`
