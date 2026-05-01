# Cursor Command — Map Truthfulness Cleanup All Priorities

Read these files first:

1. AI_CONTROL/00_PROJECT_CANONICAL.md
2. AI_CONTROL/02_CURRENT_TASK.md
3. MAP_TRUTHFULNESS_CLEANUP_SPEC.md

Use MAP_TRUTHFULNESS_CLEANUP_SPEC.md as the living implementation brief.

Implement the map truthfulness cleanup priorities in order:

1. Span label clutter
2. Underground cable layer truthfulness
3. Layer/filter counts
4. Span popup wording
5. Span anomaly intelligence
6. Context/crossing review
7. Pole popup cleanup
8. Replacement pair review

Do not broaden scope.

Keep the correct field ownership model:

- pole/support popups = physical support, mechanical evidence, mounted equipment, location and evidence
- span/cable popups = voltage, conductor, phase, route, crossing and clearance data

After each implementation batch, run:

pytest -v
pre-commit run --all-files

Commit clearly and push to master.
