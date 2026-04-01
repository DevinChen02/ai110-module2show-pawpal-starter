from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Owner:
	name: str
	available_minutes: int
	preferences: dict[str, Any] = field(default_factory=dict)
	pets: list[Pet] = field(default_factory=list)

	def __post_init__(self) -> None:
		"""Validate owner initialization values."""
		if self.available_minutes < 0:
			raise ValueError("available_minutes must be >= 0")

	def set_available_time(self, minutes: int) -> None:
		"""Set the owner's available time budget in minutes."""
		if minutes < 0:
			raise ValueError("minutes must be >= 0")
		self.available_minutes = minutes

	def update_preferences(self, preferences: dict[str, Any]) -> None:
		"""Merge new preference values into the owner's preferences."""
		self.preferences.update(preferences)

	def add_pet(self, pet: Pet) -> None:
		"""Register a pet with this owner if not already present."""
		if pet not in self.pets:
			self.pets.append(pet)

	def remove_pet(self, pet: Pet) -> None:
		"""Remove a pet from this owner's registry."""
		if pet in self.pets:
			self.pets.remove(pet)

	def get_all_tasks(self) -> list[Task]:
		"""Return a flattened list of tasks across all owned pets."""
		all_tasks: list[Task] = []
		for pet in self.pets:
			all_tasks.extend(pet.get_tasks())
		return all_tasks


@dataclass
class Task:
	title: str
	duration_minutes: int
	priority: Literal["low", "medium", "high"]
	category: str
	frequency: str = "daily"
	time_of_day: str | None = None
	pet: Pet | None = None
	completed: bool = False

	def __post_init__(self) -> None:
		"""Validate task initialization values."""
		if self.duration_minutes <= 0:
			raise ValueError("duration_minutes must be > 0")

	def mark_complete(self) -> None:
		"""Mark this task as completed."""
		self.completed = True

	def to_dict(self) -> dict[str, Any]:
		"""Serialize this task into a dictionary representation."""
		return {
			"title": self.title,
			"duration_minutes": self.duration_minutes,
			"priority": self.priority,
			"category": self.category,
			"frequency": self.frequency,
			"time_of_day": self.time_of_day,
			"pet": self.pet.name if self.pet else None,
			"completed": self.completed,
		}


@dataclass
class Pet:
	name: str
	species: str
	age: int
	owner: Owner
	tasks: list[Task] = field(default_factory=list)

	def __post_init__(self) -> None:
		"""Validate pet initialization values and register with owner."""
		if self.age < 0:
			raise ValueError("age must be >= 0")
		self.owner.add_pet(self)

	def get_tasks(self) -> list[Task]:
		"""Return a copy of this pet's task list."""
		return list(self.tasks)

	def add_task(self, task: Task) -> None:
		"""Attach a task to this pet and set task ownership."""
		task.pet = self
		if task not in self.tasks:
			self.tasks.append(task)

	def remove_task(self, task: Task) -> None:
		"""Detach a task from this pet and clear task ownership."""
		if task in self.tasks:
			self.tasks.remove(task)
		if task.pet is self:
			task.pet = None


@dataclass
class Scheduler:
	pet: Pet
	# Keep these optional in the skeleton so implementations can default to pet/owner state.
	tasks: list[Task] | None = None
	time_budget: int | None = None

	def _candidate_tasks(self) -> list[Task]:
		"""Collect incomplete tasks relevant to this scheduling context."""
		if self.tasks is not None:
			return [task for task in self.tasks if not task.completed]
		if self.pet.owner.pets:
			return [task for task in self.pet.owner.get_all_tasks() if not task.completed]
		return [task for task in self.pet.get_tasks() if not task.completed]

	def _budget(self) -> int:
		"""Return a non-negative time budget for scheduling."""
		budget = self.time_budget if self.time_budget is not None else self.pet.owner.available_minutes
		return max(0, budget)

	def filter_by_time(self) -> list[Task]:
		"""Filter candidate tasks to those that fit the total budget."""
		budget = self._budget()
		return [task for task in self._candidate_tasks() if task.duration_minutes <= budget]

	def sort_by_priority(self) -> list[Task]:
		"""Sort schedulable tasks by priority and tie-breaker rules."""
		priority_rank = {"high": 3, "medium": 2, "low": 1}
		return sorted(
			self.filter_by_time(),
			key=lambda task: (-priority_rank[task.priority], task.duration_minutes, task.title.lower()),
		)

	def build_plan(self) -> dict[str, Any]:
		"""Build a schedule plan that fits tasks into the available budget."""
		budget = self._budget()
		scheduled: list[Task] = []
		skipped: list[dict[str, Any]] = []
		time_used = 0

		for task in self.sort_by_priority():
			if time_used + task.duration_minutes <= budget:
				scheduled.append(task)
				time_used += task.duration_minutes
			else:
				skipped.append(
					{
						"task": task.to_dict(),
						"reason": "Not enough remaining time budget",
					}
				)

		return {
			"scheduled_tasks": [task.to_dict() for task in scheduled],
			"skipped_tasks": skipped,
			"total_time_used": time_used,
			"remaining_minutes": budget - time_used,
			"time_budget": budget,
		}

	def explain_plan(self) -> dict[str, Any]:
		"""Return the generated plan along with human-readable reasoning."""
		plan = self.build_plan()
		explanation: list[str] = []

		for task in plan["scheduled_tasks"]:
			explanation.append(
				f"Included '{task['title']}' ({task['duration_minutes']} min) because it fits the budget and has {task['priority']} priority."
			)

		for skipped in plan["skipped_tasks"]:
			task = skipped["task"]
			explanation.append(
				f"Skipped '{task['title']}' ({task['duration_minutes']} min): {skipped['reason']}."
			)

		return {
			"plan": plan,
			"reasoning": explanation,
		}
