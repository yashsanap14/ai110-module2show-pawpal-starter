from typing import List


class User:
    def __init__(self, user_id: str, name: str, email: str, password: str, phone_number: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.pets: List["Pet"] = []

    def create_profile(self) -> None:
        pass

    def add_pet(self, pet: "Pet") -> None:
        pass

    def edit_profile(self, **kwargs) -> None:
        pass

    def view_pets(self) -> List["Pet"]:
        pass


class Pet:
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
        self.tasks: List["Task"] = []

    def update_pet_details(self, **kwargs) -> None:
        pass

    def view_pet_profile(self) -> dict:
        pass

    def get_pet_care_needs(self) -> List[str]:
        pass


class Task:
    def __init__(
        self,
        task_id: str,
        task_name: str,
        task_type: str,
        description: str,
        priority: str,
        due_time: str,
        status: str = "pending",
        frequency: str = "once",
    ):
        self.task_id = task_id
        self.task_name = task_name
        self.task_type = task_type
        self.description = description
        self.priority = priority
        self.due_time = due_time
        self.status = status
        self.frequency = frequency

    def create_task(self) -> None:
        pass

    def update_task(self, **kwargs) -> None:
        pass

    def mark_task_completed(self) -> None:
        pass

    def set_priority(self, priority: str) -> None:
        pass


class Schedule:
    def __init__(self, schedule_id: str, date: str):
        self.schedule_id = schedule_id
        self.date = date
        self.task_list: List[Task] = []

    def add_task_to_schedule(self, task: Task) -> None:
        pass

    def remove_task_from_schedule(self, task_id: str) -> None:
        pass

    def sort_tasks_by_priority(self) -> List[Task]:
        pass

    def view_schedule(self) -> List[Task]:
        pass


class Plan:
    def __init__(self, plan_id: str, date: str, pet_id: str):
        self.plan_id = plan_id
        self.date = date
        self.pet_id = pet_id
        self.daily_tasks: List[Task] = []
        self.plan_reason: str = ""

    def generate_daily_plan(self, pet: Pet, tasks: List[Task]) -> None:
        pass

    def explain_plan(self) -> str:
        pass

    def update_plan(self, tasks: List[Task]) -> None:
        pass
