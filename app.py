import streamlit as st
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state for Owner and Scheduler
if "owner" not in st.session_state:
    # Load owner from JSON if it exists, otherwise create new
    st.session_state.owner = Owner.load_from_json()

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
    st.session_state.scheduler.set_owner(st.session_state.owner)

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant that helps you manage tasks for your pets
with smart scheduling based on priority and available time.
"""
)

st.divider()

# ========== ADD PET SECTION ==========
st.subheader("🐕 Add a Pet")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet Name", value="", placeholder="e.g., Mochi")
    with col2:
        species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)

    submitted = st.form_submit_button("Add Pet")

    if submitted:
        if not pet_name:
            st.error("Please enter a pet name!")
        else:
            try:
                new_pet = Pet(name=pet_name, species=species, age=age)
                st.session_state.owner.add_pet(new_pet)
                st.session_state.owner.save_to_json()
                st.success(f"✅ Added {pet_name} the {species}!")
            except ValueError as e:
                st.error(f"Error adding pet: {e}")

# Display current pets
if st.session_state.owner.pets:
    st.write("**Your Pets:**")
    pet_data = [{"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.tasks)}
                for p in st.session_state.owner.pets]
    st.table(pet_data)
else:
    st.info("No pets yet. Add your first pet above!")

st.divider()

# ========== ADD TASK SECTION ==========
st.subheader("📋 Add a Task")

if not st.session_state.owner.pets:
    st.warning("Please add a pet first before creating tasks.")
else:
    with st.form("add_task_form"):
        # Select which pet the task is for
        pet_names = [p.name for p in st.session_state.owner.pets]
        selected_pet_name = st.selectbox("For Pet", pet_names)

        task_description = st.text_input("Task Description", placeholder="e.g., Morning walk")

        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority_str = st.selectbox("Priority", ["High", "Medium", "Low"], index=0)
        with col3:
            frequency_str = st.selectbox("Frequency", ["one_time", "daily", "weekly", "monthly"], index=0)

        # Date and time picker
        col4, col5 = st.columns(2)
        with col4:
            task_date = st.date_input("Due Date", value=datetime.now().date())
        with col5:
            task_time = st.time_input("Due Time", value=datetime.now().time())

        task_submitted = st.form_submit_button("Add Task")

        if task_submitted:
            if not task_description:
                st.error("Please enter a task description!")
            else:
                try:
                    # Convert priority and frequency strings to enums
                    priority_enum = Priority.HIGH if priority_str == "High" else Priority.MEDIUM if priority_str == "Medium" else Priority.LOW
                    frequency_enum = Frequency.ONE_TIME if frequency_str == "one_time" else Frequency.DAILY if frequency_str == "daily" else Frequency.WEEKLY if frequency_str == "weekly" else Frequency.MONTHLY

                    # Combine date and time
                    due_datetime = datetime.combine(task_date, task_time)

                    # Generate unique task ID using Scheduler
                    task_id = st.session_state.scheduler.generate_task_id()

                    # Create the task
                    new_task = Task(
                        id=task_id,
                        description=task_description,
                        duration_minutes=duration,
                        priority=priority_enum,
                        due_time=due_datetime,
                        frequency=frequency_enum
                    )

                    # Add task to selected pet
                    selected_pet = st.session_state.scheduler.get_pet_by_name(selected_pet_name)
                    if selected_pet:
                        selected_pet.add_task(new_task)
                        st.session_state.owner.save_to_json()
                        st.success(f"✅ Added task '{task_description}' for {selected_pet_name}!")
                    else:
                        st.error(f"Could not find pet: {selected_pet_name}")

                except ValueError as e:
                    st.error(f"Error adding task: {e}")

# Display all tasks
all_tasks = st.session_state.scheduler.get_all_tasks()
if all_tasks:
    st.write("**All Tasks:**")

    # Priority emoji mapping
    priority_emoji = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢"
    }

    task_display = []
    for pet_name, task in all_tasks:
        priority_indicator = f"{priority_emoji[task.priority.value]} {task.priority.value}"
        task_display.append({
            "Pet": pet_name,
            "Task": task.description,
            "Duration": f"{task.duration_minutes} min",
            "Priority": priority_indicator,
            "Due": task.due_time.strftime("%m/%d %I:%M %p") if task.due_time else "N/A",
            "Status": "✅ Done" if task.is_completed else "⏳ Pending"
        })
    st.table(task_display)
else:
    st.info("No tasks yet. Add a task above!")

st.divider()

# ========== GENERATE SCHEDULE SECTION ==========
st.subheader("📅 Today's Schedule")

col1, col2 = st.columns([2, 1])
with col1:
    available_minutes = st.number_input("Available minutes for today", min_value=1, max_value=1440, value=120)
with col2:
    st.write("")  # spacing
    st.write("")  # spacing
    generate_btn = st.button("Generate Schedule", type="primary")

if generate_btn:
    if not st.session_state.owner.pets:
        st.warning("Please add pets and tasks first!")
    else:
        schedule = st.session_state.scheduler.generate_daily_schedule(
            available_minutes=available_minutes,
            target_date=datetime.now()
        )

        if not schedule:
            st.info("No tasks scheduled for today. Try adding tasks with today's date!")
        else:
            st.success(f"✅ Generated schedule with {len(schedule)} task(s)")

            total_time = sum(task.duration_minutes for _, task in schedule)
            st.metric("Total Scheduled Time", f"{total_time} / {available_minutes} minutes")

            st.write("**Scheduled Tasks (by priority & time):**")

            # Priority emoji mapping
            priority_emoji = {
                "High": "🔴",
                "Medium": "🟡",
                "Low": "🟢"
            }

            for i, (pet_name, task) in enumerate(schedule, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        priority_icon = priority_emoji[task.priority.value]
                        st.markdown(f"**{i}. {priority_icon} {task.description}** (for {pet_name})")
                        st.caption(f"⏰ {task.due_time.strftime('%I:%M %p')} | ⏱️ {task.duration_minutes} min | Priority: {task.priority.value}")
                    with col2:
                        if st.button(f"Mark Done", key=f"complete_{task.id}"):
                            task.mark_complete()
                            st.session_state.owner.save_to_json()
                            st.rerun()
                    st.divider()
