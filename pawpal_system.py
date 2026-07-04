from typing import List

PRIORITY_LEVELS = {"high": 1, "medium": 2, "low": 3}


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

    def update_task(self, **kwargs) -> None:
        allowed = {"task_name", "task_type", "description", "priority", "due_time", "duration", "frequency"}
        for key, value in kwargs.items():
            if key not in allowed:
                raise ValueError(f"Cannot update field: {key}")
            if key == "priority" and value not in PRIORITY_LEVELS:
                raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS)}")
            setattr(self, key, value)

    def mark_task_completed(self) -> None:
        self.status = "completed"

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
        weight: float,
        health_notes: str = "",
        special_needs: str = "",
    ):
        self.pet_id = pet_id
        self.name = name
        self.age = age
        self.pet_type = pet_type
        self.breed = breed
        self.weight = weight
        self.health_notes = health_notes
        self.special_needs = special_needs
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def update_pet_details(self, **kwargs) -> None:
        allowed = {"name", "age", "pet_type", "breed", "weight", "health_notes", "special_needs"}
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
            "weight": self.weight,
            "health_notes": self.health_notes,
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

    def get_pending_tasks(self, owner: Owner) -> List[Task]:
        return [t for t in owner.get_all_tasks() if t.status == "pending"]

    def get_tasks_by_priority(self, owner: Owner, priority: str) -> List[Task]:
        if priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LEVELS)}")
        return [t for t in owner.get_all_tasks() if t.priority == priority]

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        return sorted(tasks, key=lambda t: PRIORITY_LEVELS[t.priority])

    def generate_daily_schedule(self, owner: Owner) -> List[Task]:
        pending = self.get_pending_tasks(owner)
        return self.sort_tasks_by_priority(pending)

    def get_tasks_for_pet(self, owner: Owner, pet_id: str) -> List[Task]:
        for pet in owner.pets:
            if pet.pet_id == pet_id:
                return pet.tasks
        return []
