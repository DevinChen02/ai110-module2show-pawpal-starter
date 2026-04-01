from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_mark_complete_daily_task_creates_next_occurrence() -> None:
	owner = Owner(name="Alex", available_minutes=60)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	task = Task(
		title="Daily Walk",
		duration_minutes=20,
		priority="medium",
		category="exercise",
		frequency="daily",
	)
	pet.add_task(task)

	task.mark_complete()

	assert len(pet.get_tasks()) == 2
	next_task = [pet_task for pet_task in pet.get_tasks() if pet_task is not task][0]
	assert next_task.completed is False
	assert next_task.frequency == "daily"
	assert next_task.due_date == date.today() + timedelta(days=1)


def test_mark_complete_weekly_task_creates_next_occurrence() -> None:
	owner = Owner(name="Alex", available_minutes=60)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	task = Task(
		title="Weekly Grooming",
		duration_minutes=30,
		priority="low",
		category="hygiene",
		frequency="weekly",
	)
	pet.add_task(task)

	task.mark_complete()

	assert len(pet.get_tasks()) == 2
	next_task = [pet_task for pet_task in pet.get_tasks() if pet_task is not task][0]
	assert next_task.completed is False
	assert next_task.frequency == "weekly"
	assert next_task.due_date == date.today() + timedelta(days=7)


def test_mark_complete_non_recurring_task_does_not_create_next_occurrence() -> None:
	owner = Owner(name="Alex", available_minutes=60)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	task = Task(
		title="One-off Vet Visit",
		duration_minutes=45,
		priority="high",
		category="health",
		frequency="once",
	)
	pet.add_task(task)

	task.mark_complete()

	assert len(pet.get_tasks()) == 1


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


def test_scheduler_sort_by_time_orders_hhmm_and_puts_empty_last() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)

	pet.add_task(
		Task(
			title="No Time Task",
			duration_minutes=10,
			priority="low",
			category="general",
			time_of_day=None,
		)
	)
	pet.add_task(
		Task(
			title="Morning Feed",
			duration_minutes=10,
			priority="high",
			category="feeding",
			time_of_day="08:00",
		)
	)
	pet.add_task(
		Task(
			title="Walk",
			duration_minutes=20,
			priority="medium",
			category="exercise",
			time_of_day="07:30",
		)
	)

	scheduler = Scheduler(pet=pet)
	ordered = scheduler.sort_by_time()

	assert [task.title for task in ordered] == ["Walk", "Morning Feed", "No Time Task"]


def test_scheduler_filter_tasks_by_completion_status() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)

	completed_task = Task(
		title="Completed Task",
		duration_minutes=10,
		priority="medium",
		category="general",
	)
	completed_task.mark_complete()
	incomplete_task = Task(
		title="Incomplete Task",
		duration_minutes=15,
		priority="high",
		category="general",
	)

	pet.add_task(completed_task)
	pet.add_task(incomplete_task)

	scheduler = Scheduler(pet=pet)

	assert [task.title for task in scheduler.filter_tasks(completed=True)] == ["Completed Task"]
	assert [task.title for task in scheduler.filter_tasks(completed=False)] == ["Incomplete Task"]


def test_scheduler_filter_tasks_by_pet_name_case_insensitive() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet1 = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	pet2 = Pet(name="Mochi", species="Cat", age=2, owner=owner)

	pet1.add_task(
		Task(
			title="Walk Buddy",
			duration_minutes=20,
			priority="high",
			category="exercise",
		)
	)
	pet2.add_task(
		Task(
			title="Feed Mochi",
			duration_minutes=10,
			priority="high",
			category="feeding",
		)
	)

	scheduler = Scheduler(pet=pet1)
	filtered = scheduler.filter_tasks(pet_name="mochi")

	assert [task.title for task in filtered] == ["Feed Mochi"]


def test_scheduler_filter_tasks_combines_completion_and_pet_name() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet1 = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	pet2 = Pet(name="Mochi", species="Cat", age=2, owner=owner)

	buddys_task = Task(
		title="Buddy Walk",
		duration_minutes=15,
		priority="medium",
		category="exercise",
	)
	completed_mochi_task = Task(
		title="Mochi Meds",
		duration_minutes=5,
		priority="high",
		category="medication",
	)
	completed_mochi_task.mark_complete()
	incomplete_mochi_task = Task(
		title="Mochi Play",
		duration_minutes=10,
		priority="low",
		category="enrichment",
	)

	pet1.add_task(buddys_task)
	pet2.add_task(completed_mochi_task)
	pet2.add_task(incomplete_mochi_task)

	scheduler = Scheduler(pet=pet1)
	filtered = scheduler.filter_tasks(completed=False, pet_name="Mochi")

	assert [task.title for task in filtered] == ["Mochi Play"]


def test_scheduler_detect_time_conflicts_returns_warning_messages() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet1 = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	pet2 = Pet(name="Mochi", species="Cat", age=2, owner=owner)

	pet1.add_task(
		Task(
			title="Morning Walk",
			duration_minutes=20,
			priority="high",
			category="exercise",
			time_of_day="08:00",
		)
	)
	pet2.add_task(
		Task(
			title="Feed Breakfast",
			duration_minutes=10,
			priority="high",
			category="feeding",
			time_of_day="08:00",
		)
	)
	pet2.add_task(
		Task(
			title="Litter Scoop",
			duration_minutes=15,
			priority="low",
			category="hygiene",
			time_of_day="09:00",
		)
	)

	scheduler = Scheduler(pet=pet1)
	conflicts = scheduler.detect_time_conflicts()

	assert len(conflicts) == 1
	assert conflicts[0] == (
		"Warning: time conflict at 08:00 for Buddy: Morning Walk, Mochi: Feed Breakfast."
	)


def test_sorting_correctness_returns_tasks_in_chronological_order() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)

	pet.add_task(
		Task(
			title="Late Task",
			duration_minutes=10,
			priority="low",
			category="general",
			time_of_day="11:30",
		)
	)
	pet.add_task(
		Task(
			title="Early Task",
			duration_minutes=15,
			priority="high",
			category="exercise",
			time_of_day="07:15",
		)
	)
	pet.add_task(
		Task(
			title="Middle Task",
			duration_minutes=20,
			priority="medium",
			category="feeding",
			time_of_day="09:00",
		)
	)

	scheduler = Scheduler(pet=pet)
	ordered = scheduler.sort_by_time()

	assert [task.time_of_day for task in ordered] == ["07:15", "09:00", "11:30"]


def test_recurrence_logic_daily_complete_creates_following_day_task() -> None:
	owner = Owner(name="Alex", available_minutes=60)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)
	task = Task(
		title="Daily Walk",
		duration_minutes=20,
		priority="medium",
		category="exercise",
		frequency="daily",
	)
	pet.add_task(task)

	task.mark_complete()

	tasks = pet.get_tasks()
	assert len(tasks) == 2
	new_task = [pet_task for pet_task in tasks if pet_task is not task][0]
	assert new_task.due_date == date.today() + timedelta(days=1)
	assert new_task.completed is False


def test_conflict_detection_flags_duplicate_times() -> None:
	owner = Owner(name="Alex", available_minutes=120)
	pet = Pet(name="Buddy", species="Dog", age=3, owner=owner)

	pet.add_task(
		Task(
			title="Walk",
			duration_minutes=20,
			priority="high",
			category="exercise",
			time_of_day="08:00",
		)
	)
	pet.add_task(
		Task(
			title="Feed",
			duration_minutes=10,
			priority="high",
			category="feeding",
			time_of_day="08:00",
		)
	)

	scheduler = Scheduler(pet=pet)
	conflicts = scheduler.detect_time_conflicts()

	assert len(conflicts) == 1
	assert "time conflict at 08:00" in conflicts[0]
	assert "Buddy: Walk" in conflicts[0]
	assert "Buddy: Feed" in conflicts[0]
