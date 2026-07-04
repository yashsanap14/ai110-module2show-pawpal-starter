from datetime import date, timedelta
from itertools import combinations
from typing import List, Optional, Tuple

PRIORITY_LEVELS = {"high": 1, "medium": 2, "low": 3}
RECURRING_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' into minutes since midnight so times can be compared/added."""
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


class Task:
    """A single pet care activity."""

    def __init__(
        self,
        task_id: str,
        task_name: str,
        task_type: str,
        description: str,
        priority: str,
        due_time: str,
        duration: int = 30,
        status: str = "pending",
        frequency: str = "once",
        due_date: date = None,
    ):
        if priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS)}")
        self.task_id = task_id
        self.task_name = task_name
        self.task_type = task_type
        self.description = description
        self.priority = priority
        self.due_time = due_time
        self.duration = duration  # minutes
        self.status = status
        self.frequency = frequency
        self.due_date = due_date if due_date is not None else date.today()
        self.pet_id = None  # stamped by Pet.add_task

    def start_minutes(self) -> int:
        """Due time as minutes since midnight, for sorting and overlap math."""
        return _time_to_minutes(self.due_time)

    def end_minutes(self) -> int:
        """Minute this task finishes: start_minutes() + duration."""
        return self.start_minutes() + self.duration

    def update_task(self, **kwargs) -> None:
        allowed = {"task_name", "task_type", "description", "priority", "due_time", "duration", "frequency"}
        for key, value in kwargs.items():
            if key not in allowed:
                raise ValueError(f"Cannot update field: {key}")
            if key == "priority" and value not in PRIORITY_LEVELS:
                raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS)}")
            setattr(self, key, value)

    def mark_task_completed(self) -> Optional["Task"]:
        """Mark this task done. If it's daily/weekly, return a new Task for the
        next occurrence (due_date advanced via timedelta) so history isn't lost."""
        self.status = "completed"
        if self.frequency not in RECURRING_INTERVALS:
            return None
        next_due_date = self.due_date + RECURRING_INTERVALS[self.frequency]
        return Task(
            task_id=f"{self.task_id}-{next_due_date.isoformat()}",
            task_name=self.task_name,
            task_type=self.task_type,
            description=self.description,
            priority=self.priority,
            due_time=self.due_time,
            duration=self.duration,
            frequency=self.frequency,
            due_date=next_due_date,
        )

    def set_priority(self, priority: str) -> None:
        if priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS)}")
        self.priority = priority

    def __repr__(self) -> str:
        return f"Task({self.task_name!r}, priority={self.priority}, status={self.status})"


class Pet:
    """Stores pet details and owns a list of tasks."""

    def __init__(
        self,
        pet_id: str,
        name: str,
        age: int,
        pet_type: str,
        breed: str,
        special_needs: str = "",
    ):
        self.pet_id = pet_id
        self.name = name
        self.age = age
        self.pet_type = pet_type
        self.breed = breed
        self.special_needs = special_needs
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        task.pet_id = self.pet_id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task complete; if it recurs, schedule and return its next occurrence."""
        for task in self.tasks:
            if task.task_id == task_id:
                next_task = task.mark_task_completed()
                if next_task is not None:
                    self.add_task(next_task)
                return next_task
        return None

    def update_pet_details(self, **kwargs) -> None:
        allowed = {"name", "age", "pet_type", "breed", "special_needs"}
        for key, value in kwargs.items():
            if key not in allowed:
                raise ValueError(f"Cannot update field: {key}")
            setattr(self, key, value)

    def view_pet_profile(self) -> dict:
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "age": self.age,
            "type": self.pet_type,
            "breed": self.breed,
            "special_needs": self.special_needs,
            "task_count": len(self.tasks),
        }

    def get_pet_care_needs(self) -> List[str]:
        needs = []
        if self.special_needs:
            needs.append(self.special_needs)
        needs += [t.task_name for t in self.tasks if t.status == "pending"]
        return needs

    def __repr__(self) -> str:
        return f"Pet({self.name!r}, type={self.pet_type})"


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, owner_id: str, name: str, email: str, password: str, phone_number: str):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def view_pets(self) -> List[Pet]:
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        # Flattens every pet's task list — this is the bridge Scheduler calls
        return [task for pet in self.pets for task in pet.tasks]

    def edit_profile(self, **kwargs) -> None:
        allowed = {"name", "email", "phone_number"}
        for key, value in kwargs.items():
            if key not in allowed:
                raise ValueError(f"Cannot update field: {key}")
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"Owner({self.name!r}, pets={len(self.pets)})"


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def get_all_tasks(self, owner: Owner) -> List[Task]:
        return owner.get_all_tasks()

    def filter_tasks(
        self,
        owner: Owner,
        pet_id: str = None,
        pet_name: str = None,
        status: str = None,
        task_type: str = None,
        priority: str = None,
    ) -> List[Task]:
        """Return every task across the owner's pets matching all given
        filters (pet_id, pet_name, status, task_type, priority). Unset
        filters are skipped, so calling with no args returns all tasks."""
        if priority is not None and priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS)}")
        tasks = owner.get_all_tasks()
        if pet_id is not None:
            tasks = [t for t in tasks if t.pet_id == pet_id]
        if pet_name is not None:
            matching_ids = {p.pet_id for p in owner.pets if p.name == pet_name}
            tasks = [t for t in tasks if t.pet_id in matching_ids]
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if task_type is not None:
            tasks = [t for t in tasks if t.task_type == task_type]
        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]
        return tasks

    def get_pending_tasks(self, owner: Owner) -> List[Task]:
        """Shortcut for filter_tasks(owner, status='pending')."""
        return self.filter_tasks(owner, status="pending")

    def get_tasks_by_priority(self, owner: Owner, priority: str) -> List[Task]:
        """Shortcut for filter_tasks(owner, priority=priority)."""
        return self.filter_tasks(owner, priority=priority)

    def get_tasks_for_pet(self, owner: Owner, pet_id: str) -> List[Task]:
        """Shortcut for filter_tasks(owner, pet_id=pet_id)."""
        return self.filter_tasks(owner, pet_id=pet_id)

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort by priority tier (high, medium, low); within a tier, sort
        chronologically instead of falling back to insertion order."""
        return sorted(tasks, key=lambda t: (PRIORITY_LEVELS[t.priority], t.start_minutes()))

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort chronologically by due_time (via Task.start_minutes()); ties
        at the same time are broken by priority tier."""
        return sorted(tasks, key=lambda t: (t.start_minutes(), PRIORITY_LEVELS[t.priority]))

    def generate_daily_schedule(self, owner: Owner, for_date: date = None) -> List[Task]:
        """Build the chronological schedule of pending tasks due on for_date
        (defaults to today), so tasks auto-scheduled for a future date via
        recurring rollover don't show up before their day arrives."""
        if for_date is None:
            for_date = date.today()
        pending_today = [t for t in self.get_pending_tasks(owner) if t.due_date == for_date]
        return self.sort_tasks_by_time(pending_today)

    def detect_conflicts(self, owner: Owner) -> List[Tuple[Task, Task]]:
        """Flag any two pending tasks (same pet or different pets) whose
        [start, end) windows overlap — an owner can't be in two places at once.
        Simplified from a manual sweep to itertools.combinations: same O(n^2)
        cost for a day's task list, but no active-window bookkeeping to follow."""
        tasks = self.get_pending_tasks(owner)
        return [
            (a, b)
            for a, b in combinations(tasks, 2)
            if a.start_minutes() < b.end_minutes() and b.start_minutes() < a.end_minutes()
        ]

    def get_conflict_warnings(self, owner: Owner) -> List[str]:
        """Lightweight wrapper: turns detect_conflicts pairs into printable
        warning strings instead of raw Task objects, so callers can just log
        or display them — no exceptions raised for a schedule that overlaps."""
        pet_names = {p.pet_id: p.name for p in owner.pets}
        return [
            f"Conflict: {pet_names.get(a.pet_id, '?')}'s '{a.task_name}' ({a.due_time}) "
            f"overlaps {pet_names.get(b.pet_id, '?')}'s '{b.task_name}' ({b.due_time})"
            for a, b in self.detect_conflicts(owner)
        ]
