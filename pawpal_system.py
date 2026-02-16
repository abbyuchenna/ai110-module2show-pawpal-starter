from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any
import json
import os


class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


@dataclass
class Task:
    id: int
    description: str
    duration_minutes: int
    priority: Priority
    due_time: Optional[datetime]
    frequency: Frequency
    is_completed: bool = False
    pet_name: Optional[str] = None

    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be greater than 0.")
        if not self.description:
            raise ValueError("Description cannot be empty.")

    def mark_complete(self) -> None:
        self.is_completed = True

    def get_end_time(self) -> Optional[datetime]:
        if self.due_time is None:
            return None
        return self.due_time + timedelta(minutes=self.duration_minutes)

    def overlaps_with(self, other_task: "Task") -> bool:
        if not self.due_time or not other_task.due_time:
            return False

        self_end = self.get_end_time()
        other_end = other_task.get_end_time()

        return self.due_time < other_end and other_task.due_time < self_end

    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.value,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "frequency": self.frequency.value,
            "is_completed": self.is_completed,
            "pet_name": self.pet_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary loaded from JSON."""
        # Handle backward compatibility for lowercase priority values
        priority_str = data["priority"]
        if priority_str == "high":
            priority_str = "High"
        elif priority_str == "medium":
            priority_str = "Medium"
        elif priority_str == "low":
            priority_str = "Low"

        return cls(
            id=data["id"],
            description=data["description"],
            duration_minutes=data["duration_minutes"],
            priority=Priority(priority_str),
            due_time=datetime.fromisoformat(data["due_time"]) if data["due_time"] else None,
            frequency=Frequency(data["frequency"]),
            is_completed=data.get("is_completed", False),
            pet_name=data.get("pet_name"),
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            raise ValueError("Pet name cannot be empty.")
        if not self.species:
            raise ValueError("Species cannot be empty.")
        if self.age < 0:
            raise ValueError("Age cannot be negative.")

    def add_task(self, task: Task) -> None:
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        return self.tasks

    def get_pending_tasks(self) -> List[Task]:
        return [task for task in self.tasks if not task.is_completed]

    def to_dict(self) -> Dict[str, Any]:
        """Convert Pet to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        """Create Pet from dictionary loaded from JSON."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
        )
        # Reconstruct tasks
        pet.tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return pet


class Owner:
    """Represents a pet owner managing multiple pets."""

    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        all_tasks = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet.name, task))
        return all_tasks

    def save_to_json(self, filepath: str = "data.json") -> None:
        """
        Save owner and all pet data to JSON file.

        Args:
            filepath: Path to JSON file (default: data.json)
        """
        data = {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """
        Load owner and all pet data from JSON file.

        Args:
            filepath: Path to JSON file (default: data.json)

        Returns:
            Owner object with all pets and tasks restored.
            If file doesn't exist, returns empty Owner with default name.
        """
        if not os.path.exists(filepath):
            return cls("Pet Owner")

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            owner = cls(data.get("name", "Pet Owner"))
            owner.pets = [Pet.from_dict(pet_data) for pet_data in data.get("pets", [])]
            return owner
        except (json.JSONDecodeError, KeyError, ValueError):
            # If file is corrupted or invalid, return empty owner
            return cls("Pet Owner")


class Scheduler:
    def __init__(self):
        self.owner: Optional[Owner] = None
        self._next_task_id: int = 1

    def set_owner(self, owner: Owner) -> None:
        self.owner = owner
        self._sync_task_id_counter()

    def _sync_task_id_counter(self) -> None:
        """Sync task ID counter with existing tasks to avoid ID collisions."""
        if not self.owner:
            return

        max_id = 0
        for pet in self.owner.pets:
            for task in pet.tasks:
                max_id = max(max_id, task.id)

        self._next_task_id = max_id + 1

    def generate_task_id(self) -> int:
        task_id = self._next_task_id
        self._next_task_id += 1
        return task_id

    def get_pet_by_name(self, name: str) -> Optional[Pet]:
        if not self.owner:
            return None
        for pet in self.owner.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> List[Tuple[str, Task]]:
        if not self.owner:
            return []
        return self.owner.get_all_tasks()

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by their due_time in chronological order.
        Tasks with None due_time are placed at the end.

        Time complexity: O(n log n) where n = number of tasks
        """
        return sorted(
            tasks,
            key=lambda task: (task.due_time is None, task.due_time)
        )

    def sort_by_priority_and_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority first (High → Medium → Low), then by due_time.
        Tasks with None due_time are placed at the end within each priority level.

        Time complexity: O(n log n) where n = number of tasks
        """
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(
            tasks,
            key=lambda task: (
                priority_order[task.priority.value],
                task.due_time is None,
                task.due_time
            )
        )

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """
        Filter tasks by pet name and/or completion status.

        Args:
            pet_name: If provided, only return tasks for this pet
            completed: If provided, only return tasks with matching completion status

        Returns:
            List of Task objects matching the filter criteria

        Time complexity: O(n) where n = total number of tasks
        """
        # Get all tasks as (pet_name, task) tuples
        all_tasks = self.get_all_tasks()

        # Apply filters using list comprehension
        filtered = [
            task
            for pet, task in all_tasks
            if (pet_name is None or pet == pet_name)
            and (completed is None or task.is_completed == completed)
        ]

        return filtered

    def complete_task(self, task: Task, pet_name: str) -> bool:
        """
        Mark a task as complete and automatically generate the next recurring instance.

        For recurring tasks (DAILY, WEEKLY, MONTHLY), this creates a new task
        due at the next occurrence time and adds it to the same pet.

        Args:
            task: The task to complete
            pet_name: The name of the pet this task belongs to

        Returns:
            True if a new recurring task was created, False otherwise

        Time complexity: O(1)
        """
        # Mark the original task as complete
        task.mark_complete()

        # Check if this is a recurring task
        if task.frequency == Frequency.ONE_TIME or not task.due_time:
            return False

        # Calculate next due time based on frequency
        next_due_time = None
        if task.frequency == Frequency.DAILY:
            next_due_time = task.due_time + timedelta(days=1)
        elif task.frequency == Frequency.WEEKLY:
            next_due_time = task.due_time + timedelta(weeks=1)
        elif task.frequency == Frequency.MONTHLY:
            next_due_time = task.due_time + timedelta(days=30)

        if not next_due_time:
            return False

        # Create new recurring task with same properties
        new_task = Task(
            id=self.generate_task_id(),
            description=task.description,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            due_time=next_due_time,
            frequency=task.frequency,
            is_completed=False,
        )

        # Add to the correct pet
        pet = self.get_pet_by_name(pet_name)
        if pet:
            pet.add_task(new_task)
            return True

        return False

    def check_conflicts(self, new_task: Task) -> bool:
        for _, existing_task in self.get_all_tasks():
            if existing_task.overlaps_with(new_task):
                return True
        return False

    def detect_all_conflicts(self) -> List[str]:
        """
        Detect all time conflicts across all tasks and return warning messages.

        Checks every pair of tasks for overlapping time windows. Conflicts can occur
        between tasks for the same pet OR different pets.

        Returns:
            List of warning strings describing each conflict.
            Empty list if no conflicts exist.

        Time complexity: O(n²) where n = total number of tasks
        """
        warnings = []
        all_tasks = self.get_all_tasks()

        # Compare every pair of tasks
        for i in range(len(all_tasks)):
            pet_name_1, task_1 = all_tasks[i]

            for j in range(i + 1, len(all_tasks)):
                pet_name_2, task_2 = all_tasks[j]

                # Skip completed tasks (no conflict if already done)
                if task_1.is_completed or task_2.is_completed:
                    continue

                # Check if tasks overlap
                if task_1.overlaps_with(task_2):
                    # Format time strings
                    time_1 = task_1.due_time.strftime("%I:%M %p") if task_1.due_time else "N/A"
                    time_2 = task_2.due_time.strftime("%I:%M %p") if task_2.due_time else "N/A"

                    # Determine conflict type
                    same_pet = pet_name_1 == pet_name_2
                    conflict_type = "SAME PET" if same_pet else "DIFFERENT PETS"

                    # Build warning message
                    warning = (
                        f"⚠️  CONFLICT ({conflict_type}): "
                        f"'{task_1.description}' ({pet_name_1} @ {time_1}) "
                        f"overlaps with '{task_2.description}' ({pet_name_2} @ {time_2})"
                    )
                    warnings.append(warning)

        return warnings

    def generate_daily_schedule(
        self,
        available_minutes: int,
        target_date: Optional[datetime] = None,
    ) -> List[Tuple[str, Task]]:

        if not self.owner:
            return []

        if target_date is None:
            target_date = datetime.now()

        # Filter tasks for target date & incomplete
        tasks = [
            (pet_name, task)
            for pet_name, task in self.get_all_tasks()
            if not task.is_completed
            and task.due_time
            and task.due_time.date() == target_date.date()
        ]

        # Sort by priority (HIGH first) then time
        priority_order = {
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }

        tasks.sort(key=lambda x: (priority_order[x[1].priority], x[1].due_time))

        scheduled = []
        used_minutes = 0

        for pet_name, task in tasks:
            if used_minutes + task.duration_minutes <= available_minutes:
                scheduled.append((pet_name, task))
                used_minutes += task.duration_minutes

        return scheduled

    def generate_recurring_tasks(self, start_date: datetime, end_date: datetime) -> int:
        if not self.owner:
            return 0

        count = 0

        for pet in self.owner.pets:
            for task in list(pet.tasks):
                if task.frequency == Frequency.ONE_TIME or not task.due_time:
                    continue

                current_date = task.due_time

                while current_date <= end_date:
                    if current_date >= start_date:
                        new_task = Task(
                            id=self.generate_task_id(),
                            description=task.description,
                            duration_minutes=task.duration_minutes,
                            priority=task.priority,
                            due_time=current_date,
                            frequency=task.frequency,
                        )
                        pet.add_task(new_task)
                        count += 1

                    if task.frequency == Frequency.DAILY:
                        current_date += timedelta(days=1)
                    elif task.frequency == Frequency.WEEKLY:
                        current_date += timedelta(weeks=1)
                    elif task.frequency == Frequency.MONTHLY:
                        current_date += timedelta(days=30)

        return count
