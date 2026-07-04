import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("u1", owner_name, "", "", "")
owner = st.session_state.owner
owner.name = owner_name

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
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        task_id = f"t{len(owner.get_all_tasks()) + 1}"
        selected_pet.add_task(
            Task(task_id, task_title, task_type, "", priority, due_time, duration=int(duration))
        )

    if owner.get_all_tasks():
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
                }
                for t in owner.get_all_tasks()
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before scheduling tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a daily schedule from every pet's pending tasks, sorted by priority.")

if st.button("Generate schedule"):
    scheduler = Scheduler()
    schedule = scheduler.generate_daily_schedule(owner)
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
        st.info("No pending tasks to schedule yet.")
