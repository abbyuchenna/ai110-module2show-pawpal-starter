"""Quick test script to validate JSON persistence."""
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Priority, Frequency
import os

# Clean up any existing test file
if os.path.exists("test_data.json"):
    os.remove("test_data.json")

print("🧪 Testing JSON Persistence\n")

# Create test data
print("1. Creating test data...")
owner = Owner("Test Owner")
pet = Pet(name="TestDog", species="Dog", age=3)
task = Task(
    id=1,
    description="Morning walk",
    duration_minutes=30,
    priority=Priority.HIGH,
    due_time=datetime(2026, 2, 15, 8, 0),
    frequency=Frequency.DAILY,
)
pet.add_task(task)
owner.add_pet(pet)
print(f"   ✓ Created owner '{owner.name}' with pet '{pet.name}' and 1 task")

# Save to JSON
print("\n2. Saving to test_data.json...")
owner.save_to_json("test_data.json")
print("   ✓ Saved successfully")

# Verify file exists
print("\n3. Verifying file exists...")
assert os.path.exists("test_data.json"), "File not created!"
print("   ✓ File exists")

# Load from JSON
print("\n4. Loading from test_data.json...")
loaded_owner = Owner.load_from_json("test_data.json")
print(f"   ✓ Loaded owner '{loaded_owner.name}'")

# Verify data integrity
print("\n5. Verifying data integrity...")
assert loaded_owner.name == "Test Owner", "Owner name mismatch"
assert len(loaded_owner.pets) == 1, "Pet count mismatch"
loaded_pet = loaded_owner.pets[0]
assert loaded_pet.name == "TestDog", "Pet name mismatch"
assert loaded_pet.species == "Dog", "Species mismatch"
assert loaded_pet.age == 3, "Age mismatch"
assert len(loaded_pet.tasks) == 1, "Task count mismatch"
loaded_task = loaded_pet.tasks[0]
assert loaded_task.description == "Morning walk", "Task description mismatch"
assert loaded_task.priority == Priority.HIGH, "Priority mismatch"
assert loaded_task.frequency == Frequency.DAILY, "Frequency mismatch"
assert loaded_task.due_time.year == 2026, "Due time year mismatch"
print("   ✓ All data matches!")

# Test missing file handling
print("\n6. Testing missing file handling...")
missing_owner = Owner.load_from_json("nonexistent.json")
assert missing_owner.name == "Pet Owner", "Default owner not created"
assert len(missing_owner.pets) == 0, "Should have no pets"
print("   ✓ Gracefully handles missing file")

# Clean up
print("\n7. Cleaning up...")
os.remove("test_data.json")
print("   ✓ Test file removed")

print("\n✅ All persistence tests passed!")
