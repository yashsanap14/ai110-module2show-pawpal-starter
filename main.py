from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("u1", "Alex", "alex@email.com", "secret", "555-1234")

dog = Pet("p1", "Biscuit", 3, "Dog", "Golden Retriever", 28.5)
cat = Pet("p2", "Mochi", 5, "Cat", "Siamese", 4.2, special_needs="Needs hairball supplement")

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks for Biscuit ---
dog.add_task(Task("t1", "Morning Walk",   "walking",   "30 min walk around the block", "high",   "07:00", duration=30))
dog.add_task(Task("t2", "Breakfast",      "feeding",   "1 cup dry kibble",             "high",   "08:00", duration=10))
dog.add_task(Task("t3", "Evening Walk",   "walking",   "Evening stroll",               "medium", "18:00", duration=30))

# --- Tasks for Mochi ---
cat.add_task(Task("t4", "Breakfast",      "feeding",   "Wet food + hairball supplement","high",  "08:30", duration=10))
cat.add_task(Task("t5", "Grooming",       "grooming",  "Brush coat, check for mats",   "low",   "14:00", duration=20))
cat.add_task(Task("t6", "Playtime",       "playtime",  "Feather wand session",         "medium","17:00", duration=15))

# --- Generate schedule ---
scheduler = Scheduler()
schedule = scheduler.generate_daily_schedule(owner)

# --- Print Today's Schedule ---
print("=" * 52)
print("        TODAY'S SCHEDULE — PawPal+")
print("=" * 52)
print(f"  Owner : {owner.name}")
print(f"  Pets  : {', '.join(p.name for p in owner.view_pets())}")
print("-" * 52)
print(f"  {'TIME':<8} {'TASK':<18} {'PET':<10} {'DUR':>5}  PRIORITY")
print("-" * 52)

# Build a pet lookup so we can show which pet each task belongs to
task_to_pet = {t.task_id: pet.name for pet in owner.pets for t in pet.tasks}

for task in schedule:
    pet_name = task_to_pet.get(task.task_id, "?")
    print(f"  {task.due_time:<8} {task.task_name:<18} {pet_name:<10} {task.duration:>4}m  [{task.priority}]")

print("=" * 52)
print(f"  {len(schedule)} tasks scheduled  |  all pending")
print("=" * 52)
