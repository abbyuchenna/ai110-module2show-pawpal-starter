from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency


def print_tasks(tasks, title):
    """Helper function to print tasks in a clean format."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

    if not tasks:
        print("  (No tasks found)")
        return

    for task in tasks:
        status = "✅" if task.is_completed else "⏳"
        time_str = task.due_time.strftime('%I:%M %p') if task.due_time else "No time set"
        print(f"{status} {time_str:12} | {task.pet_name:10} | {task.description}")

    print()


def main():
    # Setup owner and scheduler
    owner = Owner("Abigail")
    scheduler = Scheduler()
    scheduler.set_owner(owner)

    # Create pets
    dog = Pet("Rocky", "Dog", 4)
    cat = Pet("Luna", "Cat", 2)
    bird = Pet("Tweety", "Bird", 1)

    owner.add_pet(dog)
    owner.add_pet(cat)
    owner.add_pet(bird)

    # Add tasks OUT OF CHRONOLOGICAL ORDER (intentionally mixed up!)
    now = datetime.now()

    # Task added first, but scheduled for 2pm (afternoon)
    task1 = Task(
        id=scheduler.generate_task_id(),
        description="Afternoon walk",
        duration_minutes=30,
        priority=Priority.MEDIUM,
        due_time=now.replace(hour=14, minute=0),
        frequency=Frequency.DAILY,
    )
    dog.add_task(task1)

    # Task added second, but scheduled for 8am (morning) - COMPLETED
    task2 = Task(
        id=scheduler.generate_task_id(),
        description="Feed breakfast",
        duration_minutes=10,
        priority=Priority.HIGH,
        due_time=now.replace(hour=8, minute=0),
        frequency=Frequency.DAILY,
        is_completed=True,  # Already done!
    )
    cat.add_task(task2)

    # Task added third, but scheduled for 6pm (evening)
    task3 = Task(
        id=scheduler.generate_task_id(),
        description="Vet appointment",
        duration_minutes=60,
        priority=Priority.HIGH,
        due_time=now.replace(hour=18, minute=30),
        frequency=Frequency.ONE_TIME,
    )
    dog.add_task(task3)

    # Task added fourth, but scheduled for 11am (late morning) - COMPLETED
    task4 = Task(
        id=scheduler.generate_task_id(),
        description="Clean litter box",
        duration_minutes=15,
        priority=Priority.MEDIUM,
        due_time=now.replace(hour=11, minute=0),
        frequency=Frequency.DAILY,
        is_completed=True,  # Already done!
    )
    cat.add_task(task4)

    # Task added fifth, but scheduled for 9:30am (morning)
    task5 = Task(
        id=scheduler.generate_task_id(),
        description="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        due_time=now.replace(hour=9, minute=30),
        frequency=Frequency.DAILY,
    )
    dog.add_task(task5)

    # Task added sixth, but scheduled for 4pm (afternoon)
    task6 = Task(
        id=scheduler.generate_task_id(),
        description="Refill water bowl",
        duration_minutes=5,
        priority=Priority.LOW,
        due_time=now.replace(hour=16, minute=0),
        frequency=Frequency.DAILY,
    )
    bird.add_task(task6)

    # Task added last, no time set (should appear at end)
    task7 = Task(
        id=scheduler.generate_task_id(),
        description="Buy bird treats",
        duration_minutes=20,
        priority=Priority.LOW,
        due_time=None,  # No specific time
        frequency=Frequency.ONE_TIME,
    )
    bird.add_task(task7)

    print("\n" + "🐾" * 30)
    print("   PAWPAL+ TASK MANAGEMENT DEMO")
    print("🐾" * 30)

    # Demonstration 1: ALL TASKS SORTED BY TIME
    all_tasks = scheduler.filter_tasks()  # Get all tasks
    sorted_tasks = scheduler.sort_tasks_by_time(all_tasks)
    print_tasks(sorted_tasks, "📋 ALL TASKS (Sorted by Time)")

    # Demonstration 2: ONLY INCOMPLETE TASKS
    incomplete_tasks = scheduler.filter_tasks(completed=False)
    sorted_incomplete = scheduler.sort_tasks_by_time(incomplete_tasks)
    print_tasks(sorted_incomplete, "⏳ INCOMPLETE TASKS ONLY")

    # Demonstration 3: TASKS FOR A SPECIFIC PET (Rocky the dog)
    rocky_tasks = scheduler.filter_tasks(pet_name="Rocky")
    sorted_rocky = scheduler.sort_tasks_by_time(rocky_tasks)
    print_tasks(sorted_rocky, "🐕 ROCKY'S TASKS")

    # Demonstration 4: COMBINATION - Luna's incomplete tasks
    luna_incomplete = scheduler.filter_tasks(pet_name="Luna", completed=False)
    sorted_luna_incomplete = scheduler.sort_tasks_by_time(luna_incomplete)
    print_tasks(sorted_luna_incomplete, "🐱 LUNA'S INCOMPLETE TASKS")

    # Demonstration 5: AUTOMATIC RECURRING TASK REGENERATION
    print("\n" + "=" * 60)
    print("  🔄 RECURRING TASK REGENERATION DEMO")
    print("=" * 60)

    # Find Rocky's morning walk (it's a DAILY recurring task)
    rocky_tasks = scheduler.filter_tasks(pet_name="Rocky", completed=False)
    morning_walk = None
    for task in rocky_tasks:
        if task.description == "Morning walk":
            morning_walk = task
            break

    if morning_walk:
        print(f"\n  Original task: {morning_walk.description}")
        print(f"  Due: {morning_walk.due_time.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"  Frequency: {morning_walk.frequency.value}")
        print(f"  Status: {'✅ Complete' if morning_walk.is_completed else '⏳ Pending'}")

        # Count tasks before completing
        tasks_before = len(scheduler.filter_tasks(pet_name="Rocky"))
        print(f"\n  Rocky's total tasks BEFORE completion: {tasks_before}")

        # Complete the task (this should auto-generate the next occurrence)
        print(f"\n  >>> Completing '{morning_walk.description}'...")
        was_regenerated = scheduler.complete_task(morning_walk, "Rocky")

        # Count tasks after completing
        tasks_after = len(scheduler.filter_tasks(pet_name="Rocky"))
        print(f"  Rocky's total tasks AFTER completion: {tasks_after}")

        if was_regenerated:
            print(f"  ✅ New recurring task automatically created!")

            # Find and show the new task
            rocky_all = scheduler.filter_tasks(pet_name="Rocky")
            new_walk = None
            for task in rocky_all:
                if (
                    task.description == "Morning walk"
                    and not task.is_completed
                    and task.id != morning_walk.id
                ):
                    new_walk = task
                    break

            if new_walk:
                print(f"\n  New task: {new_walk.description}")
                print(f"  Due: {new_walk.due_time.strftime('%Y-%m-%d %I:%M %p')}")
                print(f"  Frequency: {new_walk.frequency.value}")
                print(f"  Status: {'✅ Complete' if new_walk.is_completed else '⏳ Pending'}")
                print(f"  Task ID: {new_walk.id} (original was {morning_walk.id})")

                # Show time difference
                time_diff = new_walk.due_time - morning_walk.due_time
                print(f"  Time shift: +{time_diff.days} day(s)")
        else:
            print(f"  ℹ️  No new task created (not a recurring task)")

    print("=" * 60 + "\n")

    # Demonstration 6: CONFLICT DETECTION
    print("=" * 60)
    print("  ⚠️  CONFLICT DETECTION DEMO")
    print("=" * 60)

    print("\n  Adding conflicting tasks to test detection...")

    # Conflict 1: Same pet, exact same time
    conflict_task_1 = Task(
        id=scheduler.generate_task_id(),
        description="Grooming session",
        duration_minutes=45,
        priority=Priority.MEDIUM,
        due_time=now.replace(hour=14, minute=0),  # Same as "Afternoon walk"
        frequency=Frequency.ONE_TIME,
    )
    dog.add_task(conflict_task_1)
    print("  ✓ Added 'Grooming session' for Rocky at 2:00 PM (conflicts with Afternoon walk)")

    # Conflict 2: Different pets, overlapping time
    conflict_task_2 = Task(
        id=scheduler.generate_task_id(),
        description="Bird vet checkup",
        duration_minutes=90,  # Long duration
        priority=Priority.HIGH,
        due_time=now.replace(hour=15, minute=30),  # Starts at 3:30 PM
        frequency=Frequency.ONE_TIME,
    )
    bird.add_task(conflict_task_2)
    print(
        "  ✓ Added 'Bird vet checkup' for Tweety at 3:30 PM "
        "(overlaps with Tweety's 4:00 PM task)"
    )

    # Conflict 3: Different pets, same exact time
    conflict_task_3 = Task(
        id=scheduler.generate_task_id(),
        description="Luna's playtime",
        duration_minutes=30,
        priority=Priority.LOW,
        due_time=now.replace(hour=14, minute=0),  # Same as Rocky's tasks
        frequency=Frequency.ONE_TIME,
    )
    cat.add_task(conflict_task_3)
    print("  ✓ Added 'Luna's playtime' for Luna at 2:00 PM (same time as Rocky's tasks)")

    # Run conflict detection
    print("\n  Running conflict detection...")
    conflicts = scheduler.detect_all_conflicts()

    print(f"\n  Found {len(conflicts)} conflict(s):\n")

    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  ✅ No conflicts detected!")

    print("\n" + "=" * 60 + "\n")

    print("=" * 60)
    print("  Algorithm Demonstration Complete!")
    print("  - Tasks were added OUT OF ORDER")
    print("  - sort_tasks_by_time() arranged them chronologically")
    print("  - filter_tasks() selected by pet/status")
    print("  - complete_task() auto-generates recurring tasks")
    print("  - detect_all_conflicts() finds scheduling conflicts")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
