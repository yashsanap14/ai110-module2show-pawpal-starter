# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run `python3 main.py` to see the schedule in the terminal:

```
====================================================
        TODAY'S SCHEDULE — PawPal+
====================================================
  Owner : Alex
  Pets  : Biscuit, Mochi
----------------------------------------------------
  TIME     TASK               PET          DUR  PRIORITY
----------------------------------------------------
  07:00    Morning Walk       Biscuit      30m  [high]
  08:00    Breakfast          Biscuit      10m  [high]
  08:30    Breakfast          Mochi        10m  [high]
  18:00    Evening Walk       Biscuit      30m  [medium]
  17:00    Playtime           Mochi        15m  [medium]
  14:00    Grooming           Mochi        20m  [low]
====================================================
  6 tasks scheduled  |  all pending
====================================================
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The suite in `tests/test_pawpal.py` covers 23 tests across 5 areas:

- **Sorting** — `sort_tasks_by_time` returns chronological order and breaks same-time ties by priority; `sort_tasks_by_priority` groups by tier then time; sorting an empty list doesn't crash.
- **Recurrence** — completing a `daily`/`weekly` task returns a new `Task` due one day/week later and wires it back into the pet's task list; a `once` task returns `None` and isn't re-added; completing an unknown task ID is a no-op.
- **Conflict detection** — exact-same-time tasks and partially-overlapping-duration tasks are flagged; back-to-back tasks (end time == next start time) are not; completed tasks are excluded from conflict checks.
- **Edge cases** — a pet/owner with zero tasks doesn't error; an invalid priority raises `ValueError` on task creation and on filtering; `generate_daily_schedule` excludes tasks due on other dates.
- **Filtering** — `filter_tasks` correctly combines `pet_name`, `status`, and `priority` filters, and returns everything when called with no filters.

**Confidence level: ⭐⭐⭐⭐☆ (4/5)** — core scheduling logic (sorting, recurrence, conflicts) is well covered and all tests pass. Not yet covered: `Owner`/`Pet` CRUD edge cases (e.g. removing a pet/task mid-iteration) and the Streamlit UI layer in `app.py`.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
rootdir: /path/to/ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 23 items

tests/test_pawpal.py .......................                             [100%]

============================== 23 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks_by_time()`, `Scheduler.sort_tasks_by_priority()` | `sort_tasks_by_time` orders tasks chronologically by `due_time` (converted to minutes since midnight), breaking ties by priority. `sort_tasks_by_priority` orders by priority tier first, breaking ties chronologically. `generate_daily_schedule()` uses `sort_tasks_by_time` to build each day's agenda. |
| Filtering | `Scheduler.filter_tasks()` (+ shortcuts `get_pending_tasks()`, `get_tasks_by_priority()`, `get_tasks_for_pet()`) | One generic method filters by any combination of `pet_id`, `pet_name`, `status`, `task_type`, and `priority` in a single pass, instead of one hardcoded method per filter. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.get_conflict_warnings()` | Compares every pair of a day's pending tasks (`itertools.combinations`) and flags any whose `[start, end)` time windows overlap — catching both exact-same-time collisions and overlapping-duration collisions (e.g. a 30-minute walk that swallows a 15-minute call). `get_conflict_warnings()` returns printable warning strings instead of raising, so a conflicting schedule never crashes the app. |
| Recurring tasks | `Task.mark_task_completed()`, `Pet.complete_task()` | Completing a task with `frequency` of `"daily"` or `"weekly"` automatically creates and returns a new `Task` for the next occurrence (`due_date` advanced with `datetime.timedelta`), while the original stays `"completed"` as history. `Pet.complete_task()` wires the new occurrence back into the pet's task list. `generate_daily_schedule()` only shows tasks due on the target date, so a next-day occurrence doesn't appear early. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
