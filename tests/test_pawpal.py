from pawpal_system import Owner, Pet, Task


def test_task_mark_complete_changes_status() -> None:
	task = Task(
		title="Walk",
		duration_minutes=20,
		priority="medium",
		category="exercise",
	)

	assert task.completed is False
	task.mark_complete()
	assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
	owner = Owner(name="Alex", available_minutes=60)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)

	initial_count = len(pet.get_tasks())
	task = Task(
		title="Feed Dinner",
		duration_minutes=10,
		priority="high",
		category="feeding",
	)

	pet.add_task(task)

	assert len(pet.get_tasks()) == initial_count + 1
