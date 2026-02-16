from datetime import datetime
from pawpal_system import Task, Pet, Priority, Frequency


def test_mark_complete():
    task = Task(
        id=1,
        description="Feed",
        duration_minutes=10,
        priority=Priority.MEDIUM,
        due_time=datetime.now(),
        frequency=Frequency.ONE_TIME,
    )

    task.mark_complete()
    assert task.is_completed is True


def test_add_task_to_pet():
    pet = Pet("Rocky", "Dog", 3)

    task = Task(
        id=1,
        description="Walk",
        duration_minutes=20,
        priority=Priority.HIGH,
        due_time=datetime.now(),
        frequency=Frequency.ONE_TIME,
    )

    pet.add_task(task)

    assert len(pet.tasks) == 1
