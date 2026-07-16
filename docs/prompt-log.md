i need to add
Search bar to search for the task above the columns.

Extend GET /tasks to support text search and combinations such as status, priority, assignee, or tag/due-date if implemented.

Add a compact filter/search bar above the board. Keep columns visible and preserve empty states.

Add due date to the modal. Show due date or overdue pill on cards. Add an overdue filter or visual indicator.

backend:
Add optional due_date validation. Support create/update. Decide whether overdue is computed in the backend or UI. Optional query filter for overdue.

this was weak since i did not mentioned the validation and the alert message.
so i rewrite them:

i need to do validation not to enter a due date with a date from yesterday and before( old dates)+
when the due date is 3,2,1 days -> an alert message should appear on the task card reminding the user
