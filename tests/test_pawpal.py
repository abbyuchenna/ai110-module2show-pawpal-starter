"""
Comprehensive test suite for PawPal+ scheduler system.

Tests cover:
- Task sorting (chronological ordering)
- Task filtering (by pet, status, combined)
- Recurring task automation (DAILY, WEEKLY, MONTHLY)
- Conflict detection (overlap detection)
- Edge cases (None values, empty lists, invalid inputs)
"""

from datetime import datetime, timedelta
import pytest
from pawpal_system import (
    Task,
    Pet,
    Owner,
    Scheduler,
    Priority,
    Frequency,
)


# ============================================================
# SORTING TESTS
# ============================================================


def test_sort_tasks_chronologically():
    """
    Test that tasks are sorted in chronological order by due_time.
    This is the core sorting algorithm - tasks should appear earliest first.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)
    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()

    # Add tasks OUT OF ORDER
    task1 = Task(1, "Task 3PM", 30, Priority.HIGH, now.replace(hour=15), Frequency.ONE_TIME)
    task2 = Task(2, "Task 9AM", 30, Priority.HIGH, now.replace(hour=9), Frequency.ONE_TIME)
    task3 = Task(3, "Task 12PM", 30, Priority.HIGH, now.replace(hour=12), Frequency.ONE_TIME)

    unsorted = [task1, task2, task3]
    sorted_tasks = scheduler.sort_tasks_by_time(unsorted)

    # Verify chronological order: 9AM -> 12PM -> 3PM
    assert sorted_tasks[0].description == "Task 9AM"
    assert sorted_tasks[1].description == "Task 12PM"
    assert sorted_tasks[2].description == "Task 3PM"


def test_sort_tasks_with_none_at_end():
    """
    Test that tasks with None due_time are placed at the end.
    This ensures unscheduled tasks don't cause sorting errors.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    now = datetime.now()

    task1 = Task(1, "Scheduled", 30, Priority.HIGH, now.replace(hour=10), Frequency.ONE_TIME)
    task2 = Task(2, "Unscheduled", 30, Priority.HIGH, None, Frequency.ONE_TIME)
    task3 = Task(3, "Also Scheduled", 30, Priority.HIGH, now.replace(hour=8), Frequency.ONE_TIME)

    unsorted = [task1, task2, task3]
    sorted_tasks = scheduler.sort_tasks_by_time(unsorted)

    # Scheduled tasks first (8AM, 10AM), then None
    assert sorted_tasks[0].description == "Also Scheduled"
    assert sorted_tasks[1].description == "Scheduled"
    assert sorted_tasks[2].description == "Unscheduled"
    assert sorted_tasks[2].due_time is None


def test_sort_empty_task_list():
    """
    Test that sorting an empty list returns an empty list.
    Edge case: prevents crashes when no tasks exist.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    sorted_tasks = scheduler.sort_tasks_by_time([])
    assert sorted_tasks == []


# ============================================================
# FILTERING TESTS
# ============================================================


def test_filter_by_pet_name():
    """
    Test filtering tasks by a specific pet name.
    Should return only tasks belonging to that pet.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    dog = Pet("Rocky", "Dog", 4)
    cat = Pet("Luna", "Cat", 2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    now = datetime.now()

    # Add tasks for different pets
    task1 = Task(1, "Walk Rocky", 30, Priority.HIGH, now, Frequency.ONE_TIME)
    task2 = Task(2, "Feed Luna", 10, Priority.MEDIUM, now, Frequency.ONE_TIME)
    task3 = Task(3, "Play with Rocky", 20, Priority.LOW, now, Frequency.ONE_TIME)

    dog.add_task(task1)
    cat.add_task(task2)
    dog.add_task(task3)

    # Filter for Rocky's tasks
    rocky_tasks = scheduler.filter_tasks(pet_name="Rocky")

    assert len(rocky_tasks) == 2
    assert all(task.pet_name == "Rocky" for task in rocky_tasks)


def test_filter_by_completion_status():
    """
    Test filtering tasks by completion status.
    Should separate completed from pending tasks.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()

    task1 = Task(1, "Completed Task", 30, Priority.HIGH, now, Frequency.ONE_TIME, is_completed=True)
    task2 = Task(2, "Pending Task", 30, Priority.HIGH, now, Frequency.ONE_TIME, is_completed=False)
    task3 = Task(3, "Another Pending", 30, Priority.HIGH, now, Frequency.ONE_TIME, is_completed=False)

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    # Filter for pending tasks only
    pending = scheduler.filter_tasks(completed=False)
    assert len(pending) == 2
    assert all(not task.is_completed for task in pending)

    # Filter for completed tasks only
    completed = scheduler.filter_tasks(completed=True)
    assert len(completed) == 1
    assert all(task.is_completed for task in completed)


def test_filter_combined_pet_and_status():
    """
    Test combined filtering by both pet name and completion status.
    Should apply both filters simultaneously.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    dog = Pet("Rocky", "Dog", 4)
    cat = Pet("Luna", "Cat", 2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    now = datetime.now()

    task1 = Task(1, "Walk Rocky", 30, Priority.HIGH, now, Frequency.ONE_TIME, is_completed=True)
    task2 = Task(2, "Feed Rocky", 10, Priority.MEDIUM, now, Frequency.ONE_TIME, is_completed=False)
    task3 = Task(3, "Feed Luna", 10, Priority.MEDIUM, now, Frequency.ONE_TIME, is_completed=False)

    dog.add_task(task1)
    dog.add_task(task2)
    cat.add_task(task3)

    # Filter for Rocky's pending tasks
    rocky_pending = scheduler.filter_tasks(pet_name="Rocky", completed=False)

    assert len(rocky_pending) == 1
    assert rocky_pending[0].description == "Feed Rocky"
    assert rocky_pending[0].pet_name == "Rocky"
    assert not rocky_pending[0].is_completed


def test_filter_no_parameters_returns_all():
    """
    Test that calling filter with no parameters returns all tasks.
    Default behavior should not filter anything.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()

    task1 = Task(1, "Task 1", 30, Priority.HIGH, now, Frequency.ONE_TIME)
    task2 = Task(2, "Task 2", 30, Priority.HIGH, now, Frequency.ONE_TIME, is_completed=True)

    pet.add_task(task1)
    pet.add_task(task2)

    all_tasks = scheduler.filter_tasks()
    assert len(all_tasks) == 2


# ============================================================
# RECURRING TASK TESTS
# ============================================================


def test_complete_daily_task_creates_next():
    """
    Test that completing a DAILY task creates tomorrow's instance.
    Core recurring task feature - ensures continuous scheduling.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()
    task = Task(
        id=scheduler.generate_task_id(),
        description="Daily walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        due_time=now,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    # Complete the task
    was_created = scheduler.complete_task(task, "Buddy")

    assert was_created is True
    assert task.is_completed is True

    # Verify new task was created
    all_tasks = scheduler.filter_tasks(pet_name="Buddy")
    assert len(all_tasks) == 2

    # Find the new task (not completed)
    new_task = [t for t in all_tasks if not t.is_completed][0]
    assert new_task.description == "Daily walk"
    assert new_task.due_time == now + timedelta(days=1)


def test_complete_weekly_task_creates_next():
    """
    Test that completing a WEEKLY task creates next week's instance.
    Verifies weekly recurrence logic.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()
    task = Task(
        id=scheduler.generate_task_id(),
        description="Weekly grooming",
        duration_minutes=60,
        priority=Priority.MEDIUM,
        due_time=now,
        frequency=Frequency.WEEKLY,
    )
    pet.add_task(task)

    was_created = scheduler.complete_task(task, "Buddy")

    assert was_created is True

    all_tasks = scheduler.filter_tasks(pet_name="Buddy")
    new_task = [t for t in all_tasks if not t.is_completed][0]

    # Verify next week's date (7 days later)
    assert new_task.due_time == now + timedelta(weeks=1)


def test_complete_one_time_no_recurrence():
    """
    Test that completing a ONE_TIME task does NOT create a new instance.
    Prevents infinite task generation for one-off events.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()
    task = Task(
        id=scheduler.generate_task_id(),
        description="Vet appointment",
        duration_minutes=60,
        priority=Priority.HIGH,
        due_time=now,
        frequency=Frequency.ONE_TIME,
    )
    pet.add_task(task)

    was_created = scheduler.complete_task(task, "Buddy")

    assert was_created is False
    assert task.is_completed is True

    # Should only have 1 task (the original, now completed)
    all_tasks = scheduler.filter_tasks(pet_name="Buddy")
    assert len(all_tasks) == 1


def test_recurring_task_new_id():
    """
    Test that the regenerated recurring task has a new unique ID.
    Prevents ID collisions in the system.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()
    original_id = scheduler.generate_task_id()
    task = Task(
        id=original_id,
        description="Daily task",
        duration_minutes=30,
        priority=Priority.HIGH,
        due_time=now,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    scheduler.complete_task(task, "Buddy")

    all_tasks = scheduler.filter_tasks(pet_name="Buddy")
    new_task = [t for t in all_tasks if not t.is_completed][0]

    # New task must have different ID
    assert new_task.id != original_id


def test_recurring_task_none_due_time_no_generation():
    """
    Test that tasks with None due_time don't generate recurring instances.
    Edge case: unscheduled recurring tasks should not recur.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    task = Task(
        id=scheduler.generate_task_id(),
        description="Unscheduled daily",
        duration_minutes=30,
        priority=Priority.HIGH,
        due_time=None,  # No time set
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    was_created = scheduler.complete_task(task, "Buddy")

    assert was_created is False


# ============================================================
# CONFLICT DETECTION TESTS
# ============================================================


def test_detect_same_time_conflict():
    """
    Test that tasks with identical start times are detected as conflicts.
    Most obvious conflict case - same pet, same time.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now().replace(hour=10, minute=0)

    task1 = Task(1, "Walk", 30, Priority.HIGH, now, Frequency.ONE_TIME)
    task2 = Task(2, "Grooming", 45, Priority.MEDIUM, now, Frequency.ONE_TIME)

    pet.add_task(task1)
    pet.add_task(task2)

    conflicts = scheduler.detect_all_conflicts()

    assert len(conflicts) == 1
    assert "SAME PET" in conflicts[0]
    assert "Walk" in conflicts[0]
    assert "Grooming" in conflicts[0]


def test_detect_partial_overlap_conflict():
    """
    Test that partially overlapping tasks are detected.
    Algorithm correctness: not just same start time, but any overlap.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()

    # Task 1: 10:00 AM - 10:30 AM (30 min)
    task1 = Task(1, "Walk", 30, Priority.HIGH, now.replace(hour=10, minute=0), Frequency.ONE_TIME)

    # Task 2: 10:15 AM - 10:45 AM (30 min) - overlaps by 15 minutes
    task2 = Task(2, "Play", 30, Priority.HIGH, now.replace(hour=10, minute=15), Frequency.ONE_TIME)

    pet.add_task(task1)
    pet.add_task(task2)

    conflicts = scheduler.detect_all_conflicts()

    assert len(conflicts) == 1


def test_no_conflict_sequential_tasks():
    """
    Test that sequential non-overlapping tasks have no conflicts.
    Ensures no false positives - back-to-back tasks are OK.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()

    # Task 1: 10:00 AM - 10:30 AM
    task1 = Task(1, "Walk", 30, Priority.HIGH, now.replace(hour=10, minute=0), Frequency.ONE_TIME)

    # Task 2: 10:30 AM - 11:00 AM (starts exactly when task1 ends)
    task2 = Task(2, "Feed", 30, Priority.HIGH, now.replace(hour=10, minute=30), Frequency.ONE_TIME)

    pet.add_task(task1)
    pet.add_task(task2)

    conflicts = scheduler.detect_all_conflicts()

    assert len(conflicts) == 0


def test_completed_tasks_ignored_in_conflicts():
    """
    Test that completed tasks are excluded from conflict detection.
    Only future/pending tasks should trigger warnings.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now().replace(hour=10, minute=0)

    task1 = Task(1, "Walk", 30, Priority.HIGH, now, Frequency.ONE_TIME, is_completed=True)
    task2 = Task(2, "Grooming", 45, Priority.MEDIUM, now, Frequency.ONE_TIME)

    pet.add_task(task1)
    pet.add_task(task2)

    conflicts = scheduler.detect_all_conflicts()

    # No conflict because task1 is completed
    assert len(conflicts) == 0


def test_conflict_detection_cross_pet():
    """
    Test that conflicts are detected across different pets.
    Owner can only do one thing at a time, even for different pets.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    dog = Pet("Rocky", "Dog", 4)
    cat = Pet("Luna", "Cat", 2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    now = datetime.now().replace(hour=10, minute=0)

    task1 = Task(1, "Walk Rocky", 30, Priority.HIGH, now, Frequency.ONE_TIME)
    task2 = Task(2, "Feed Luna", 20, Priority.HIGH, now, Frequency.ONE_TIME)

    dog.add_task(task1)
    cat.add_task(task2)

    conflicts = scheduler.detect_all_conflicts()

    assert len(conflicts) == 1
    assert "DIFFERENT PETS" in conflicts[0]


# ============================================================
# EDGE CASE & VALIDATION TESTS
# ============================================================


def test_invalid_task_duration():
    """
    Test that creating a task with invalid duration raises ValueError.
    Data validation: duration must be positive.
    """
    with pytest.raises(ValueError, match="Duration must be greater than 0"):
        Task(
            id=1,
            description="Invalid task",
            duration_minutes=0,  # Invalid!
            priority=Priority.HIGH,
            due_time=datetime.now(),
            frequency=Frequency.ONE_TIME,
        )


def test_invalid_task_description():
    """
    Test that creating a task with empty description raises ValueError.
    Data validation: description must be non-empty.
    """
    with pytest.raises(ValueError, match="Description cannot be empty"):
        Task(
            id=1,
            description="",  # Invalid!
            duration_minutes=30,
            priority=Priority.HIGH,
            due_time=datetime.now(),
            frequency=Frequency.ONE_TIME,
        )


def test_task_overlap_with_none_time():
    """
    Test that tasks with None due_time don't cause crashes in overlap detection.
    Edge case: unscheduled tasks should return False for overlaps.
    """
    task1 = Task(1, "Task 1", 30, Priority.HIGH, None, Frequency.ONE_TIME)
    task2 = Task(2, "Task 2", 30, Priority.HIGH, datetime.now(), Frequency.ONE_TIME)

    # Should not crash, should return False
    assert task1.overlaps_with(task2) is False
    assert task2.overlaps_with(task1) is False


def test_get_end_time_with_none():
    """
    Test that get_end_time() returns None when due_time is None.
    Edge case: prevents crashes in time calculations.
    """
    task = Task(1, "Task", 30, Priority.HIGH, None, Frequency.ONE_TIME)
    assert task.get_end_time() is None


def test_scheduler_with_no_owner():
    """
    Test that scheduler operations work correctly when no owner is set.
    Edge case: prevents crashes on uninitialized scheduler.
    """
    scheduler = Scheduler()

    # Should return empty list, not crash
    assert scheduler.get_all_tasks() == []
    assert scheduler.filter_tasks() == []


def test_filter_nonexistent_pet():
    """
    Test filtering for a pet that doesn't exist returns empty list.
    Edge case: graceful handling of invalid queries.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    # Filter for pet that doesn't exist
    results = scheduler.filter_tasks(pet_name="Nonexistent")
    assert results == []


# ============================================================
# INTEGRATION TESTS
# ============================================================


def test_full_workflow_sort_filter_complete():
    """
    Integration test: demonstrates full workflow of sorting, filtering, and completing tasks.
    Tests that all Phase 4 features work together correctly.
    """
    scheduler = Scheduler()
    owner = Owner("Test Owner")
    scheduler.set_owner(owner)

    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    now = datetime.now()

    # Add multiple tasks out of order
    task1 = Task(scheduler.generate_task_id(), "Task 3PM", 30, Priority.HIGH, now.replace(hour=15), Frequency.DAILY)
    task2 = Task(scheduler.generate_task_id(), "Task 9AM", 30, Priority.HIGH, now.replace(hour=9), Frequency.ONE_TIME)
    task3 = Task(scheduler.generate_task_id(), "Task 12PM", 30, Priority.MEDIUM, now.replace(hour=12), Frequency.ONE_TIME)

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    # Step 1: Get all tasks
    all_tasks = scheduler.filter_tasks()
    assert len(all_tasks) == 3

    # Step 2: Sort them
    sorted_tasks = scheduler.sort_tasks_by_time(all_tasks)
    assert sorted_tasks[0].description == "Task 9AM"

    # Step 3: Filter pending only
    pending = scheduler.filter_tasks(completed=False)
    assert len(pending) == 3

    # Step 4: Complete a recurring task
    scheduler.complete_task(task1, "Buddy")

    # Step 5: Verify new task created
    all_tasks_after = scheduler.filter_tasks()
    assert len(all_tasks_after) == 4  # Original 3 + 1 new recurring

    # Step 6: Verify conflicts
    conflicts = scheduler.detect_all_conflicts()
    # Should have no conflicts (tasks at different times)
    assert len(conflicts) == 0
