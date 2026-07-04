from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner("u1", "Alex", "alex@email.com", "secret", "555-1234")

dog = Pet("p1", "Biscuit", 3, "Dog", "Golden Retriever")
cat = Pet("p2", "Mochi", 5, "Cat", "Siamese", special_needs="Needs hairball supplement")

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks added out of chronological order on purpose, to prove sorting works ---
evening_walk = Task("t3", "Evening Walk",   "walking",  "Evening stroll",               "medium", "18:00", duration=30)
breakfast_dog = Task("t2", "Breakfast",     "feeding",  "1 cup dry kibble",             "high",   "08:00", duration=10)
morning_walk = Task("t1", "Morning Walk",   "walking",  "30 min walk around the block", "high",   "07:00", duration=30)
grooming = Task("t5", "Grooming",           "grooming", "Brush coat, check for mats",   "low",    "14:00", duration=20,
                 frequency="daily")
breakfast_cat = Task("t4", "Breakfast",     "feeding",  "Wet food + hairball supplement","high",  "08:30", duration=10)
playtime = Task("t6", "Playtime",           "playtime", "Feather wand session",         "medium", "17:00", duration=15)
vet_call = Task("t7", "Vet Follow-up Call", "other",    "Call clinic about test results","low",   "07:15", duration=15)
# Same due_time as each other, for different pets -> exact-time conflict
nail_trim_dog = Task("t8", "Nail Trim", "grooming", "Trim front + back nails", "medium", "12:00", duration=15)
nail_trim_cat = Task("t9", "Nail Trim", "grooming", "Trim front + back nails", "medium", "12:00", duration=15)

for task in (evening_walk, breakfast_dog, morning_walk):
    dog.add_task(task)
for task in (grooming, breakfast_cat, playtime, vet_call):
    cat.add_task(task)
dog.add_task(nail_trim_dog)
cat.add_task(nail_trim_cat)

scheduler = Scheduler()
pet_names = {p.pet_id: p.name for p in owner.pets}

# --- Step 2: sorting, demoed directly on the shuffled list above ---
print("Sorted by time (input order was shuffled):")
for t in scheduler.sort_tasks_by_time([evening_walk, breakfast_dog, morning_walk, breakfast_cat]):
    print(f"  {t.due_time}  {t.task_name}")

# --- Step 2: filtering by completion status and by pet name ---
print("\nFilter -> status='pending', pet_name='Mochi':")
for t in scheduler.filter_tasks(owner, status="pending", pet_name="Mochi"):
    print(f"  {t.due_time}  {t.task_name}")

# --- Step 3: completing a recurring task auto-schedules its next occurrence ---
next_occurrence = cat.complete_task(grooming.task_id)
print(f"\nCompleted '{grooming.task_name}' (status={grooming.status}).")
if next_occurrence:
    print(f"Auto-scheduled next occurrence: '{next_occurrence.task_name}' "
          f"on {next_occurrence.due_date} at {next_occurrence.due_time} "
          f"(status={next_occurrence.status})")

# --- Today's schedule (chronological, only today's pending tasks) ---
schedule = scheduler.generate_daily_schedule(owner)

print("\n" + "=" * 52)
print("        TODAY'S SCHEDULE — PawPal+")
print("=" * 52)
print(f"  Owner : {owner.name}")
print(f"  Pets  : {', '.join(p.name for p in owner.view_pets())}")
print("-" * 52)
print(f"  {'TIME':<8} {'TASK':<18} {'PET':<10} {'DUR':>5}  PRIORITY")
print("-" * 52)

for task in schedule:
    pet_name = pet_names.get(task.pet_id, "?")
    tag = " (recurring)" if task.frequency != "once" else ""
    print(f"  {task.due_time:<8} {task.task_name:<18} {pet_name:<10} {task.duration:>4}m  [{task.priority}]{tag}")

print("=" * 52)
print(f"  {len(schedule)} tasks scheduled  |  all pending")
print("=" * 52)

# --- Step 4: conflict detection (same time, and overlapping durations) ---
warnings = scheduler.get_conflict_warnings(owner)
print(f"\n{len(warnings)} schedule conflict(s) found:" if warnings else "\nNo schedule conflicts detected.")
for warning in warnings:
    print(f"  ! {warning}")
