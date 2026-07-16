User stories for the two features
Feature 1: Search bar and filter experience

1- Search tasks quickly
User story: As a user, I want to search tasks by keywords so I can quickly find the task I need.

Acceptance criteria:

A search box is visible above the board.
Typing a keyword filters tasks instantly.
Matching tasks are shown while non-matching tasks are hidden.
The board remains visible and organized while filtering.

2- Combine search with other filters
User story: As a user, I want to combine search text with status, priority, and assignee filters so I can narrow results precisely.

Acceptance criteria:

Users can apply search text together with status, priority, and assignee filters.
The results reflect all selected filters at the same time.
Filters can be cleared individually or together.
The board updates without reloading the page.
Corrected AI assumption: I initially assumed one filter at a time would be enough, but I corrected it to support combined filtering.

3- Show a clear empty state
User story: As a user, I want to see a clear empty state when no tasks match my search so I know the filter worked.

Acceptance criteria:

If no tasks match, the board shows a clear message such as “No tasks”.
The empty state appears without breaking the column layout.
The message remains visible until the filters are changed or cleared.

Feature 2: Due date and reminders

1- Add and edit due dates on tasks
User story: As a user, I want to set a due date when creating or editing a task so I can track deadlines.

Acceptance criteria:

A due date field is available in the task modal.
The selected date is saved with the task.
The due date is displayed on the task card after saving.
The task can be updated later and the due date can be changed.
Corrected AI assumption: I initially assumed due dates were only useful for display, but I corrected it to be a real saved field in both create and edit flows.

2- Show visual reminders for urgent tasks
User story: As a user, I want to see overdue or soon-due reminders on cards so I can prioritize work.

Acceptance criteria:

Tasks with due dates show a reminder badge when they are due today or within 3 days.
Overdue tasks show an overdue badge.
The reminder text is clear and easy to understand.
The reminder appears on the task card without changing the card structure.

3- Prevent invalid past due dates
User story: As a user, I want the app to prevent me from entering a past due date so I do not create incorrect deadlines.

Acceptance criteria:

If a user selects a date earlier than today, the app shows a validation message.
The task is not saved until the date is corrected.
The validation message is visible in the modal.
The user can still enter a valid future date.
Corrected AI assumption: I initially assumed client-side validation alone would be sufficient, but I corrected it to ensure the user gets a clear error message and the task is blocked from saving.
