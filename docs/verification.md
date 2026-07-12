Verification report

1. Baseline check
   Baseline scope: task creation, task listing, filtering, validation, patching, and deletion.
   Current backend status: the task API is running and responding correctly.
   Evidence:
   Backend test suite passed: 22 passed, 4 warnings, 0 failures.
   The live API accepted task creation and search/filter requests successfully.
2. Backend test results
   Verified with:

pytest test_tasks.py -q
Result:

22 passed
0 failed
4 warnings (FastAPI/Starlette deprecation warnings only) 3. Manual browser checks
Manual UI checks that should be validated in the browser:

The search bar and filter controls appear above the board.
Typing a keyword updates the visible task list.
Combining search text with status/priority/assignee filters narrows the results.
When no results match, an empty-state message is shown.
Due dates appear on cards and overdue/soon-due reminders display visually. 4. Behavior contract before/after refactor
Before refactor:

The board only showed tasks without search/filter support.
No due-date field existed in the task form.
No visual reminder state existed for overdue or soon-due tasks.
After refactor:

GET /tasks supports search and filter query parameters:
q
status
priority
assignee
overdue
The UI shows a clear empty state when a filter returns no matches.
Task creation/editing supports due_date.
Task cards display due date and reminder/overdue badges. 5. Break test evidence
Here are two concrete break-test examples that demonstrate the behavior contract:

Search + filter combination
Test: list tasks with q, status, priority, and assignee
Expected: only one matching task is returned
Evidence: backend test in test_tasks.py covers this behavior and passed.
Live API evidence:
A task was created successfully.
A GET request with q=manual&status=ToDo&priority=High&assignee=Rashed returned one matching task.
Invalid filter value
Test: invalid status filter should return 422
Expected: API rejects unknown status values with validation detail
Evidence: backend test in test_tasks.py covers this and passed.
Live API evidence:
GET /tasks?status=Unknown returned HTTP 422
Response included validation detail for the invalid enum value
