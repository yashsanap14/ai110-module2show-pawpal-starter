# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    1. a user should be able to add a pet
    2. a user will have his profile under which he will add his pets 
    3. Inside  a pets profile it will contain all the details of the pet
    4. After that  a user can be able schedule the tasks for pet like walk, feeding, grooming on basis of priority
    5. create a daily plan and why it craeted a plan

- What classes did you include, and what responsibilities did you assign to each?

User

Responsible for storing the pet owner’s information.

Attributes:

userId
name
email
password
phoneNumber

Responsibilities:

createProfile()
addPet()
editProfile()
viewPets()

Relationship:

One User can have many Pets.
Pet

Responsible for storing details about each pet.

Attributes:

petId
name
age
type
breed
weight
healthNotes
specialNeeds

Responsibilities:

updatePetDetails()
viewPetProfile()
getPetCareNeeds()

Relationship:

Each Pet belongs to one User.
Each Pet can have many Tasks.
Task

Responsible for storing pet care activities.

Attributes:

taskId
taskName
taskType
description
priority
dueTime
status
frequency

Examples of task types:

Feeding
Walking
Grooming
Medication
Vet Visit
Playtime

Responsibilities:

createTask()
updateTask()
markTaskCompleted()
setPriority()
Schedule

Responsible for organizing tasks by time and priority.

Attributes:

scheduleId
date
taskList

Responsibilities:

addTaskToSchedule()
removeTaskFromSchedule()
sortTasksByPriority()
viewSchedule()
Plan

Responsible for creating the daily care plan.

Attributes:

planId
date
petId
dailyTasks
planReason

Responsibilities:

generateDailyPlan()
explainPlan()
updatePlan()

Example reason:

The plan was created because the pet has a high-priority feeding task in the morning, a walking
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, in two ways. First, `User` became `Owner` and the separate `Schedule` and
`Plan` classes from the draft never got built as their own classes — their
responsibilities (holding a task list, sorting it, explaining the plan) turned
out to belong on a single stateless `Scheduler` that takes an `Owner` as an
argument to each method, instead of a class that owns and mutates its own
`taskList`/`dailyTasks` state. Building two more stateful classes that had to
stay in sync with `Owner.get_all_tasks()` would have meant more places for the
task list to drift out of sync; a stateless service class reading directly
from `Owner`/`Pet` at call time has one source of truth. Second, `Pet`
originally carried `weight` and `health_notes` fields from the draft UML, but
neither was ever read by any scheduling logic, so they were dropped from
`Pet.__init__`, `update_pet_details`, and `view_pet_profile` to keep the class
limited to what the scheduler and UI actually use.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three things: due time (`due_time` + `duration`,
converted to minutes-since-midnight for comparison), priority tier
(high/medium/low), and status (only `pending` tasks are scheduled or checked
for conflicts — `completed` tasks are history). Time won out as the primary
constraint because the core failure mode for a real pet owner isn't "did I
rank tasks correctly," it's "did I double-book myself" — a missed walk
because two tasks needed the owner in two places at once is worse than a
walk happening in a slightly suboptimal order. That's why `detect_conflicts`
exists as its own first-class check rather than just relying on sorted order
to reveal collisions.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`Scheduler.detect_conflicts` checks whether two tasks' full `[start, end)` time
windows overlap (using `due_time` + `duration`), instead of the cheaper check of
only flagging tasks with an identical `due_time` string. The overlap check is
more accurate — it also catches a 15-minute vet call at 07:15 colliding with a
30-minute walk that started at 07:00, which an exact-match check would miss —
but it costs an O(n²) pairwise comparison across every pending task, and it
trusts that each task's `duration` estimate is realistic. For a single owner's
daily task list (a handful of tasks per pet), that O(n²) cost is negligible, so
trading a bit of extra computation for catching real, physically-impossible
overlaps was the right call here. It would stop being reasonable if PawPal+
ever scheduled for a shelter with hundreds of pets and tasks per day.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used my AI coding assistant for implementation (turning the UML into the
`Task`/`Pet`/`Owner`/`Scheduler` classes), for writing the automated test
suite, and for wiring the tested backend into the Streamlit UI. The most
effective feature was tight write-run-verify loops: rather than asking for
code and reading it, I had the assistant run `pytest` and a headless browser
against the actual running Streamlit app after each change, so "it works" was
based on observed output (test pass/fail counts, screenshots of the rendered
UI) instead of a plausible-looking diff. Asking pointed questions like "what
are the most important edge cases to test for a pet scheduler with sorting
and recurring tasks?" produced a more useful test plan than a generic "write
tests for this file" would have, because it forced a concrete list (empty
task lists, same-time ties, back-to-back vs. overlapping durations) instead
of just happy-path coverage.

Using a separate chat session dedicated to testing (Phase 3) kept that phase
focused purely on behavior verification instead of re-litigating design
choices already made in the implementation phase, and this documentation
phase's own session stayed scoped to UI/UML/README/reflection work without
re-deriving scheduling logic that was already settled and tested. Keeping
each phase in its own session meant each conversation only had to hold the
context relevant to its task, which made it easier to review each phase's
output on its own terms.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

`detect_conflicts` started as a manual sweep: sort tasks by start time, keep a
running `active` list of tasks whose window hasn't ended yet, and compare each
new task against that list. I asked the assistant how that method could be
simplified for readability, and it suggested replacing the sweep with
`itertools.combinations(tasks, 2)` filtered by the overlap condition — no
sorting, no manual "active window" bookkeeping, just "check every pair."
Before accepting it, I checked the actual complexity: the sweep's active-list
filtering is also O(n) per task in the worst case, so it's O(n²) overall too —
the combinations version isn't slower for a daily task list, just shorter and
easier to read. I ran both versions against the same test data (the 07:00
walk vs. 07:15 vet call, and the two 12:00 nail-trim tasks) and got identical
results, so I kept the simplified version.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

`tests/test_pawpal.py` covers 23 cases across five areas: chronological and
priority sorting (including same-time ties), recurrence (daily/weekly tasks
rescheduling correctly, `once` tasks not recurring, completing an unknown
task ID being a no-op), conflict detection (exact-time and overlapping-
duration collisions flagged, back-to-back tasks and completed tasks correctly
*not* flagged), generic filtering, and edge cases like an owner with zero
pets/tasks and an invalid priority raising `ValueError`. These mattered
because they're exactly the places a plausible-looking implementation quietly
breaks: an off-by-one in the overlap comparison (`<` vs `<=`) would either
miss real conflicts or falsely flag back-to-back tasks, and both are wrong in
opposite, hard-to-notice ways.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

4/5 stars — the core scheduling logic (sorting, recurrence, conflicts,
filtering) is well tested and all 23 tests pass. Writing the UML/UI docs for
this phase surfaced one real gap I'd test next: `detect_conflicts` filters
pending tasks by status only, not by `due_date`, so two unrelated tasks
scheduled for different days at the same time-of-day would currently be
flagged as conflicting even though the owner would never actually be
double-booked. I'd add a test that pins this down (and a `due_date` filter to
`detect_conflicts` to fix it) before trusting the conflict warnings past a
single day's view. I'd also add tests around `Owner.remove_pet`/
`Pet.remove_task` and light UI-level checks for `app.py`, which today is only
verified by manual/browser walkthroughs, not automated tests.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The conflict-detection feature end to end: it's backed by tests that pin down
exactly which overlaps count, and the Streamlit UI turns a raw list of
`(Task, Task)` tuples into a specific, actionable warning ("Biscuit's
'Morning Walk' (07:00) overlaps Mochi's 'Vet Follow-up Call' (07:15)")
instead of a generic "you have a conflict" message — that's the difference
between a warning the owner can act on immediately and one they have to go
hunt down themselves.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd fix the date-blind-spot in `detect_conflicts` noted above, and I'd give
the app persistence — right now `Owner`/`Pet`/`Task` state lives only in
Streamlit's `session_state`, so a page refresh loses everything. A small
JSON or SQLite-backed save/load would make the "daily schedule" concept
actually useful across days instead of only within one browser session.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Being the "lead architect" meant treating AI suggestions as a first draft to
verify, not a final answer to accept — whether that's checking the actual
Big-O of a suggested simplification against what it replaced (Section 3b) or
actually running the app in a browser instead of trusting that code which
type-checks and reads well also *behaves* correctly. The AI was fastest at
producing plausible code and thorough test-case brainstorming; my job was
deciding which constraints actually mattered for this scenario (time over
priority) and catching the gap between "the tests I wrote pass" and "the
system is correct" — like the date-blind-spot in conflict detection, which
no test caught because no one had thought to write it yet.
