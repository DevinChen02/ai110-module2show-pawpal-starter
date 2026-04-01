import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")


def initialize_session_objects() -> None:
    """Create persistent domain objects once per Streamlit session."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="Jordan", available_minutes=120)

    if "pet" not in st.session_state:
        st.session_state.pet = Pet(
            name="Mochi",
            species="dog",
            age=2,
            owner=st.session_state.owner,
        )


def task_table_rows() -> list[dict[str, object]]:
    """Return task rows for table display."""
    return [task.to_dict() for task in st.session_state.pet.get_tasks()]


initialize_session_objects()

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

st.subheader("Adding a Pet")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
pet_name = st.text_input("Pet name", value=st.session_state.pet.name)
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Pet age", min_value=0, max_value=50, value=int(st.session_state.pet.age))

st.session_state.owner.name = owner_name

if st.button("Add or update pet"):
    st.session_state.pet = Pet(
        name=pet_name,
        species=species,
        age=int(age),
        owner=st.session_state.owner,
    )
    st.success(f"Saved pet profile for {st.session_state.pet.name}.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.pet.add_task(
        Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category="general",
        )
    )

rows = task_table_rows()

if rows:
    st.write("Current tasks:")
    st.table(rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a schedule from your current tasks and available time.")

if st.button("Generate schedule"):
    scheduler = Scheduler(pet=st.session_state.pet)
    explained_plan = scheduler.explain_plan()
    plan = explained_plan["plan"]

    st.success("Schedule generated.")
    st.write(f"Time budget: {plan['time_budget']} minutes")
    st.write(f"Total time used: {plan['total_time_used']} minutes")
    st.write(f"Remaining minutes: {plan['remaining_minutes']}")

    st.markdown("### Scheduled tasks")
    if plan["scheduled_tasks"]:
        st.table(plan["scheduled_tasks"])
    else:
        st.info("No tasks were scheduled.")

    if plan["skipped_tasks"]:
        st.markdown("### Skipped tasks")
        skipped_rows = [
            {
                "title": item["task"]["title"],
                "duration_minutes": item["task"]["duration_minutes"],
                "priority": item["task"]["priority"],
                "reason": item["reason"],
            }
            for item in plan["skipped_tasks"]
        ]
        st.table(skipped_rows)

    st.markdown("### Why this plan")
    for reason in explained_plan["reasoning"]:
        st.write(f"- {reason}")
