# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  
The revised UML design uses four classes: Owner, Pet, Task, and Scheduler. Owner stores the owner's daily time budget and preferences, and manages a collection of pets. Pet stores identity details and maintains a task list while staying linked to one owner. Task stores care details (title, duration, priority, category, due date, frequency, and optional time-of-day), and can be assigned to one pet or remain unassigned. Scheduler is initialized around a focal pet and builds daily plans using either provided tasks/time_budget or owner/pet defaults. It supports filtering, priority sorting, time sorting, conflict detection, and plan explanation. This keeps planning logic centralized and reflects a one-to-many Owner-to-Pet model and a one-to-many Pet-to-Task model.

Owner Class:
Attributes: name, available_minutes (daily time budget), preferences, pets
Methods: set_available_time(), update_preferences(), add_pet(pet), remove_pet(pet), get_all_tasks()

Pet Class:
Attributes: name, species, age, owner, tasks
Methods: get_tasks(), add_task(task), remove_task(task)

Task Class:
Attributes: title, duration_minutes, priority ("low" / "medium" / "high"), category, frequency, due_date, time_of_day, pet, completed
Methods: mark_complete(), to_dict() (for display/storage)

Scheduler Class:
Attributes: pet, tasks (optional), time_budget (optional)
Methods:
detect_time_conflicts() — report same-time task collisions as warnings
filter_tasks() — filter by completion status and/or pet name
filter_by_time() — drop tasks that won't fit
sort_by_priority() — rank remaining tasks
sort_by_time() — order tasks by scheduled time
build_plan() — return scheduled_tasks, skipped_tasks, and total_time_used
explain_plan() — return human-readable reasoning for each inclusion/exclusion


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, I changed my design during implementation:
1. Added stricter priority typing on Task.priority to Literal["low", "medium", "high"] in pawpal_system.py:24.
2. Added explicit Task.pet relationship (Pet | None) in pawpal_system.py:26 to match your UML “Task involves one Pet” model.
3. Made Scheduler.tasks and Scheduler.time_budget optional in pawpal_system.py:57 and pawpal_system.py:58, so later logic can safely default to pet.tasks and owner.available_minutes and avoid dual-source drift.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
	My scheduler considers time budget, task priority, completion status, and time-of-day collisions. It only schedules tasks that fit within the owner's available minutes, sorts by priority (high to low), uses incomplete tasks for planning, and warns when two tasks share the same scheduled time.
- How did you decide which constraints mattered most?
	I prioritized time budget and task priority first because they most directly affect whether the schedule is realistic and whether important care tasks happen. Completion filtering and conflict warnings were added to improve day-to-day reliability without making the core logic too complex.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
	A key tradeoff is using a greedy priority-first approach instead of a full optimization approach. The scheduler may not always maximize total task coverage, because it chooses higher-priority tasks first when time is limited.
- Why is that tradeoff reasonable for this scenario?
	This tradeoff is reasonable because PawPal+ is a practical daily assistant, not an advanced optimization system. The greedy method is faster, easier to explain, and easier to test, while still ensuring critical pet-care tasks are more likely to be included.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI as a design and implementation partner in three main ways: (1) brainstorming the class boundaries so Owner, Pet, Task, and Scheduler had clear responsibilities, (2) debugging edge cases in scheduling behavior (especially task filtering and conflict handling), and (3) refactoring for clearer typing and safer defaults. For example, AI support helped me tighten `Task.priority` with `Literal["low", "medium", "high"]` and make `Scheduler.tasks` / `Scheduler.time_budget` optional so scheduling can default to owner/pet state without duplicated sources of truth.
- What kinds of prompts or questions were most helpful?
The most helpful prompts were specific, constraint-based prompts like: "Given this class model, what should happen when no explicit task list is passed to Scheduler?" and "Write tests for recurring daily/weekly completion and time conflicts." Questions that included expected behavior and edge conditions produced much better results than generic "improve this" prompts.


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One moment was around conflict handling. A suggestion leaned toward treating same-time tasks as hard errors. I did not accept that as-is because for a planning assistant, warnings are more practical than blocking execution.
- How did you evaluate or verify what the AI suggested?
I evaluated suggestions against project goals (usable daily planner, explainable behavior, non-fragile UX) and verified by running/expanding tests. I specifically validated that `detect_time_conflicts()` returns warning strings instead of exceptions, and that existing schedule generation still works under those warnings.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested core scheduling and task lifecycle behaviors: completion state updates, daily/weekly recurrence generation on `mark_complete()`, non-recurring task completion, task add behavior, completion and pet-name filtering, chronological HH:MM sorting (with unset times placed last), and conflict detection for duplicate `time_of_day` values.
- Why were these tests important?
These tests cover the most failure-prone logic that directly affects user trust: whether important tasks are selected correctly, whether recurring care is generated reliably, and whether schedule output is predictable and explainable. They also protect against regressions when refactoring scheduler internals.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am highly confident for the implemented feature set because the test suite passes and covers the key decision rules (README notes a full passing run). Confidence is strongest for priority/time filtering, recurrence behavior, and conflict-warning output.
- What edge cases would you test next if you had more time?
I would add tests for: zero-minute owner budget, tasks longer than total budget, malformed or non-standard `time_of_day` strings, very large task lists (performance), ties across identical priority/duration/title patterns, and mixed multi-pet plans where some tasks are already completed.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the separation of concerns and explainability: Task/Pet/Owner handle data and relationships, while Scheduler owns planning decisions and returns both machine-readable output and human-readable reasoning.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
In another iteration, I would redesign scheduling to support preference-weighted scoring (not just greedy priority), stricter validation for task time formats, and richer conflict resolution suggestions (for example, recommended alternate times). I would also expand tests into parameterized scenarios and add UI-level checks for Streamlit interactions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
A key takeaway is that AI is most effective when treated as a fast draft partner, not an authority. Clear requirements, explicit constraints, and test-driven verification are what turn AI suggestions into reliable system design decisions.
