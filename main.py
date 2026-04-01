from pawpal_system import Owner, Pet, Task


def print_todays_schedule(owner: Owner) -> None:
	print("Today's Schedule")
	print("=" * 16)

	all_tasks = owner.get_all_tasks()
	ordered_tasks = sorted(all_tasks, key=lambda task: task.time_of_day or "")

	for task in ordered_tasks:
		time_label = task.time_of_day if task.time_of_day else "No set time"
		pet_name = task.pet.name if task.pet else "Unknown pet"
		print(
			f"{time_label} - {pet_name}: {task.title} "
			f"({task.duration_minutes} min, {task.priority} priority)"
		)


def main() -> None:
	owner = Owner(name="Maya", available_minutes=120)

	pet1 = Pet(name="Luna", species="Dog", age=4, owner=owner)
	pet2 = Pet(name="Milo", species="Cat", age=2, owner=owner)

	pet1.add_task(
		Task(
			title="Morning Walk",
			duration_minutes=30,
			priority="high",
			category="exercise",
			time_of_day="07:30",
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
	pet1.add_task(
		Task(
			title="Evening Medication",
			duration_minutes=5,
			priority="medium",
			category="medication",
			time_of_day="19:00",
		)
	)

	print_todays_schedule(owner)


if __name__ == "__main__":
	main()
