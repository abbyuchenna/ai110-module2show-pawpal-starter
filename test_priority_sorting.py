"""Test script to validate priority-based sorting."""
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency

print("🧪 Testing Advanced Priority Sorting\n")

# Create scheduler and owner
scheduler = Scheduler()
owner = Owner("Test Owner")
pet = Pet(name="TestPet", species="Dog", age=3)

# Create tasks with mixed priorities and times
print("1. Creating test tasks with mixed priorities and times...")

# High priority at 5 PM
task_high_5pm = Task(
    id=1,
    description="High priority task (5 PM)",
    duration_minutes=30,
    priority=Priority.HIGH,
    due_time=datetime(2026, 2, 15, 17, 0),  # 5:00 PM
    frequency=Frequency.ONE_TIME,
)

# Medium priority at 9 AM
task_medium_9am = Task(
    id=2,
    description="Medium priority task (9 AM)",
    duration_minutes=20,
    priority=Priority.MEDIUM,
    due_time=datetime(2026, 2, 15, 9, 0),  # 9:00 AM
    frequency=Frequency.ONE_TIME,
)

# Low priority at 8 AM
task_low_8am = Task(
    id=3,
    description="Low priority task (8 AM)",
    duration_minutes=15,
    priority=Priority.LOW,
    due_time=datetime(2026, 2, 15, 8, 0),  # 8:00 AM
    frequency=Frequency.ONE_TIME,
)

# High priority at 10 AM
task_high_10am = Task(
    id=4,
    description="High priority task (10 AM)",
    duration_minutes=25,
    priority=Priority.HIGH,
    due_time=datetime(2026, 2, 15, 10, 0),  # 10:00 AM
    frequency=Frequency.ONE_TIME,
)

# Medium priority at 2 PM
task_medium_2pm = Task(
    id=5,
    description="Medium priority task (2 PM)",
    duration_minutes=40,
    priority=Priority.MEDIUM,
    due_time=datetime(2026, 2, 15, 14, 0),  # 2:00 PM
    frequency=Frequency.ONE_TIME,
)

# Add all tasks to pet
pet.add_task(task_high_5pm)
pet.add_task(task_medium_9am)
pet.add_task(task_low_8am)
pet.add_task(task_high_10am)
pet.add_task(task_medium_2pm)

owner.add_pet(pet)
scheduler.set_owner(owner)

print(f"   ✓ Created 5 tasks with mixed priorities and times\n")

# Test the sorting method
print("2. Testing sort_by_priority_and_time()...")
all_tasks = [task for _, task in scheduler.get_all_tasks()]
sorted_tasks = scheduler.sort_by_priority_and_time(all_tasks)

print("\n   📋 Sorted Task Order:")
priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
for i, task in enumerate(sorted_tasks, 1):
    emoji = priority_emoji[task.priority.value]
    time_str = task.due_time.strftime("%I:%M %p") if task.due_time else "N/A"
    print(f"   {i}. {emoji} {task.priority.value:6} | {time_str} | {task.description}")

# Validate sorting rules
print("\n3. Validating sorting rules...")

# Check that High priority tasks come first
assert sorted_tasks[0].priority == Priority.HIGH, "First task should be HIGH priority"
assert sorted_tasks[1].priority == Priority.HIGH, "Second task should be HIGH priority"
print("   ✓ High priority tasks appear first")

# Check that within High priority, earlier times come first
assert sorted_tasks[0].due_time.hour == 10, "First High task should be at 10 AM"
assert sorted_tasks[1].due_time.hour == 17, "Second High task should be at 5 PM"
print("   ✓ Within High priority, earlier times come first")

# Check that Medium tasks come after High
assert sorted_tasks[2].priority == Priority.MEDIUM, "Third task should be MEDIUM priority"
assert sorted_tasks[3].priority == Priority.MEDIUM, "Fourth task should be MEDIUM priority"
print("   ✓ Medium priority tasks come after High")

# Check that Low tasks come last
assert sorted_tasks[4].priority == Priority.LOW, "Last task should be LOW priority"
print("   ✓ Low priority tasks come last")

# Verify the key requirement: High at 5 PM before Medium at 9 AM
high_5pm_index = next(i for i, t in enumerate(sorted_tasks) if t.id == 1)
medium_9am_index = next(i for i, t in enumerate(sorted_tasks) if t.id == 2)
assert high_5pm_index < medium_9am_index, "High priority at 5 PM should come before Medium at 9 AM"
print("   ✓ High priority at 5 PM appears before Medium at 9 AM")

print("\n✅ All priority sorting tests passed!")
print("\n📊 Summary:")
print(f"   • Priority order: High → Medium → Low")
print(f"   • Within each priority: earliest time first")
print(f"   • Visual indicators: 🔴 High, 🟡 Medium, 🟢 Low")
