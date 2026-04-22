Proceed end-to-end within the approved scope.

You may:

- inspect only necessary files
- edit only in-scope files
- run tests
- update clearly necessary docs/control files
- commit and push if the step is complete

You must:

- keep scope narrow
- avoid unrelated refactors
- avoid architecture changes unless explicitly part of the task
- stop only if something outside the approved scope becomes necessary

At the end:

1. run `pytest -v`
2. run `pre-commit run --all-files`
3. if pre-commit changes files, stage those files
4. run `git add .`
5. commit with a clear message
6. push
7. return one final concise report:
   - files changed
   - exact work completed
   - tests and results
   - docs/control files updated
   - commit message
   - commit hash
   - final git status
