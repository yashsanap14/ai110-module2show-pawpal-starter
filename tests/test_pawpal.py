from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def owner():
    return Owner("u1", "Alex", "alex@email.com", "secret", "555-1234")


@pytest.fixture
def dog(owner):
    pet = Pet("p1", "Biscuit", 3, "Dog", "Golden Retriever")
    owner.add_pet(pet)
    return pet


@pytest.fixture
def cat(owner):
    pet = Pet("p2", "Mochi", 5, "Cat", "Siamese", special_needs="Needs hairball supplement")
    owner.add_pet(pet)
    return pet


def make_task(task_id, due_time, priority="medium", duration=30, frequency="once", **kwargs):
    return Task(
        task_id=task_id,
        task_name=f"Task {task_id}",
        task_type="other",
        description="",
        priority=priority,
        due_time=due_time,
        duration=duration,
        frequency=frequency,
        **kwargs,
    )


# --- Sorting correctness ---

class TestSorting:
    def test_sort_by_time_chronological(self):
        t1 = make_task("t1", "18:00")
        t2 = make_task("t2", "07:00")
        t3 = make_task("t3", "12:00")
        result = Scheduler().sort_tasks_by_time([t1, t2, t3])
        assert [t.task_id for t in result] == ["t2", "t3", "t1"]

    def test_sort_by_time_ties_break_by_priority(self):
        low = make_task("low", "09:00", priority="low")
        high = make_task("high", "09:00", priority="high")
        medium = make_task("medium", "09:00", priority="medium")
        result = Scheduler().sort_tasks_by_time([low, high, medium])
        assert [t.task_id for t in result] == ["high", "medium", "low"]

    def test_sort_by_priority_groups_tiers_then_time(self):
        low = make_task("low", "07:00", priority="low")
        high_late = make_task("high_late", "20:00", priority="high")
        high_early = make_task("high_early", "06:00", priority="high")
        result = Scheduler().sort_tasks_by_priority([low, high_late, high_early])
        assert [t.task_id for t in result] == ["high_early", "high_late", "low"]

    def test_sort_empty_list_returns_empty(self):
        assert Scheduler().sort_tasks_by_time([]) == []


# --- Recurrence logic ---

class TestRecurrence:
    def test_daily_task_reschedules_next_day(self):
        today = date.today()
        task = make_task("daily1", "08:00", frequency="daily", due_date=today)
        next_task = task.mark_task_completed()
        assert task.status == "completed"
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)
        assert next_task.due_time == "08:00"
        assert next_task.status == "pending"

    def test_weekly_task_reschedules_next_week(self):
        today = date.today()
        task = make_task("weekly1", "08:00", frequency="weekly", due_date=today)
        next_task = task.mark_task_completed()
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_once_task_does_not_recur(self):
        task = make_task("once1", "08:00", frequency="once")
        next_task = task.mark_task_completed()
        assert task.status == "completed"
        assert next_task is None

    def test_pet_complete_task_adds_next_occurrence(self, dog):
        today = date.today()
        task = make_task("daily1", "08:00", frequency="daily", due_date=today)
        dog.add_task(task)
        next_task = dog.complete_task("daily1")
        assert next_task is not None
        assert next_task in dog.tasks
        assert next_task.pet_id == dog.pet_id
        assert len(dog.tasks) == 2

    def test_pet_complete_nonrecurring_task_does_not_grow_list(self, dog):
        task = make_task("once1", "08:00", frequency="once")
        dog.add_task(task)
        result = dog.complete_task("once1")
        assert result is None
        assert len(dog.tasks) == 1
        assert dog.tasks[0].status == "completed"

    def test_complete_unknown_task_returns_none(self, dog):
        assert dog.complete_task("does-not-exist") is None


# --- Conflict detection ---

class TestConflictDetection:
    def test_exact_duplicate_time_flagged(self, owner, dog, cat):
        t1 = make_task("t1", "12:00", duration=15)
        t2 = make_task("t2", "12:00", duration=15)
        dog.add_task(t1)
        cat.add_task(t2)
        conflicts = Scheduler().detect_conflicts(owner)
        assert len(conflicts) == 1
        ids = {conflicts[0][0].task_id, conflicts[0][1].task_id}
        assert ids == {"t1", "t2"}

    def test_overlapping_duration_flagged(self, owner, dog):
        t1 = make_task("t1", "08:00", duration=30)  # 08:00-08:30
        t2 = make_task("t2", "08:15", duration=15)  # 08:15-08:30, overlaps t1
        dog.add_task(t1)
        dog.add_task(t2)
        conflicts = Scheduler().detect_conflicts(owner)
        assert len(conflicts) == 1

    def test_back_to_back_tasks_not_flagged(self, owner, dog):
        t1 = make_task("t1", "08:00", duration=30)  # ends 08:30
        t2 = make_task("t2", "08:30", duration=30)  # starts exactly when t1 ends
        dog.add_task(t1)
        dog.add_task(t2)
        assert Scheduler().detect_conflicts(owner) == []

    def test_completed_tasks_excluded_from_conflicts(self, owner, dog):
        t1 = make_task("t1", "12:00", duration=15, status="completed")
        t2 = make_task("t2", "12:00", duration=15)
        dog.add_task(t1)
        dog.add_task(t2)
        assert Scheduler().detect_conflicts(owner) == []

    def test_get_conflict_warnings_readable_strings(self, owner, dog, cat):
        t1 = make_task("t1", "12:00", duration=15)
        t2 = make_task("t2", "12:00", duration=15)
        dog.add_task(t1)
        cat.add_task(t2)
        warnings = Scheduler().get_conflict_warnings(owner)
        assert len(warnings) == 1
        assert "Conflict" in warnings[0]


# --- Edge cases ---

class TestEdgeCases:
    def test_pet_with_no_tasks_has_empty_schedule(self, owner, dog):
        assert Scheduler().generate_daily_schedule(owner) == []

    def test_owner_with_no_pets_has_no_conflicts(self, owner):
        assert Scheduler().detect_conflicts(owner) == []
        assert Scheduler().get_all_tasks(owner) == []

    def test_invalid_priority_raises_on_task_creation(self):
        with pytest.raises(ValueError):
            make_task("bad", "08:00", priority="urgent")

    def test_invalid_priority_raises_on_filter(self, owner):
        with pytest.raises(ValueError):
            Scheduler().filter_tasks(owner, priority="urgent")

    def test_generate_daily_schedule_excludes_other_dates(self, owner, dog):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        today_task = make_task("today", "08:00", due_date=today)
        tomorrow_task = make_task("tomorrow", "08:00", due_date=tomorrow)
        dog.add_task(today_task)
        dog.add_task(tomorrow_task)
        schedule = Scheduler().generate_daily_schedule(owner, for_date=today)
        assert [t.task_id for t in schedule] == ["today"]


# --- Filtering ---

class TestFiltering:
    def test_filter_by_pet_name(self, owner, dog, cat):
        t1 = make_task("t1", "08:00")
        t2 = make_task("t2", "09:00")
        dog.add_task(t1)
        cat.add_task(t2)
        result = Scheduler().filter_tasks(owner, pet_name="Mochi")
        assert [t.task_id for t in result] == ["t2"]

    def test_filter_by_status_and_priority(self, owner, dog):
        pending_high = make_task("p1", "08:00", priority="high")
        done_high = make_task("p2", "09:00", priority="high", status="completed")
        dog.add_task(pending_high)
        dog.add_task(done_high)
        result = Scheduler().filter_tasks(owner, status="pending", priority="high")
        assert [t.task_id for t in result] == ["p1"]

    def test_filter_with_no_args_returns_all_tasks(self, owner, dog, cat):
        dog.add_task(make_task("t1", "08:00"))
        cat.add_task(make_task("t2", "09:00"))
        result = Scheduler().filter_tasks(owner)
        assert len(result) == 2
