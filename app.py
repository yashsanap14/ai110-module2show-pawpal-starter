import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** helps a pet owner plan daily care tasks — walks, feeding, meds, grooming — and
builds a conflict-free, priority-aware schedule for the day.
"""
)

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("u1", owner_name, "", "", "")
owner = st.session_state.owner
owner.name = owner_name

scheduler = Scheduler()

st.markdown("### Add a Pet")

col1, col2, col3, col4 = st.columns(4)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed", value="")
with col4:
    age = st.number_input("Age", min_value=0, max_value=30, value=1)

if st.button("Add pet"):
    pet_id = f"p{len(owner.pets) + 1}"
    owner.add_pet(Pet(pet_id, pet_name, int(age), species, breed))
    st.success(f"Added {pet_name} to {owner.name}'s pets.")

if owner.pets:
    st.write("Current pets:")
    st.table([p.view_pet_profile() for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.markdown("### Schedule a Task")
st.caption("Tasks are added to the selected pet, then feed into the scheduler below.")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_type = st.selectbox(
            "Task type", ["walking", "feeding", "grooming", "medication", "vet visit", "playtime"]
        )
    with col3:
        due_time = st.text_input("Due time", value="08:00")
    with col4:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    col5, col6 = st.columns(2)
    with col5:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col6:
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])

    if st.button("Add task"):
        task_id = f"t{len(owner.get_all_tasks()) + 1}"
        selected_pet.add_task(
            Task(
                task_id,
                task_title,
                task_type,
                "",
                priority,
                due_time,
                duration=int(duration),
                frequency=frequency,
            )
        )
        st.success(f"Added '{task_title}' for {selected_pet.name} at {due_time}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        task_to_pet = {t.task_id: p.name for p in owner.pets for t in p.tasks}
        st.table(
            [
                {
                    "pet": task_to_pet[t.task_id],
                    "task": t.task_name,
                    "due_time": t.due_time,
                    "duration": t.duration,
                    "priority": t.priority,
                    "status": t.status,
                    "repeats": t.frequency,
                }
                for t in all_tasks
            ]
        )

        st.markdown("#### Mark a Task Complete")
        st.caption("Completing a daily/weekly task auto-schedules its next occurrence.")
        pending_tasks = [t for t in all_tasks if t.status == "pending"]
        if pending_tasks:
            task_labels = {
                f"{task_to_pet[t.task_id]} — {t.task_name} ({t.due_time})": t for t in pending_tasks
            }
            selected_label = st.selectbox("Task", list(task_labels.keys()))
            if st.button("Mark complete"):
                task = task_labels[selected_label]
                pet = next(p for p in owner.pets if p.pet_id == task.pet_id)
                next_task = pet.complete_task(task.task_id)
                if next_task is not None:
                    st.success(
                        f"Completed '{task.task_name}'. Since it repeats {task.frequency}, "
                        f"the next occurrence is scheduled for {next_task.due_date} at {next_task.due_time}."
                    )
                else:
                    st.success(f"Completed '{task.task_name}'.")
        else:
            st.caption("No pending tasks to complete.")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before scheduling tasks.")

st.divider()

st.subheader("Today's Schedule")
st.caption("Builds today's schedule from every pet's pending tasks, sorted by time or priority.")

sort_order = st.radio("Sort by", ["Time", "Priority"], horizontal=True)

if st.button("Generate schedule"):
    schedule = scheduler.generate_daily_schedule(owner)
    if sort_order == "Priority":
        schedule = scheduler.sort_tasks_by_priority(schedule)

    conflicts = scheduler.get_conflict_warnings(owner)
    if conflicts:
        st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) found — resolve these before the day starts:")
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts — you're all set for today!")

    if schedule:
        task_to_pet = {t.task_id: p.name for p in owner.pets for t in p.tasks}
        st.table(
            [
                {
                    "time": t.due_time,
                    "task": t.task_name,
                    "pet": task_to_pet[t.task_id],
                    "duration": t.duration,
                    "priority": t.priority,
                }
                for t in schedule
            ]
        )
    else:
        st.info("No pending tasks due today.")
