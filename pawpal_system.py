from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Owner:
	name: str
	available_minutes: int
	preferences: dict[str, Any] = field(default_factory=dict)

	def set_available_time(self, minutes: int) -> None:
		pass

	def update_preferences(self, preferences: dict[str, Any]) -> None:
		pass


@dataclass
class Task:
	title: str
	duration_minutes: int
	priority: str
	category: str
	completed: bool = False

	def mark_complete(self) -> None:
		pass

	def to_dict(self) -> dict[str, Any]:
		pass


@dataclass
class Pet:
	name: str
	species: str
	age: int
	owner: Owner
	tasks: list[Task] = field(default_factory=list)

	def get_tasks(self) -> list[Task]:
		pass

	def add_task(self, task: Task) -> None:
		pass

	def remove_task(self, task: Task) -> None:
		pass


@dataclass
class Scheduler:
	pet: Pet
	tasks: list[Task]
	time_budget: int

	def filter_by_time(self) -> list[Task]:
		pass

	def sort_by_priority(self) -> list[Task]:
		pass

	def build_plan(self) -> dict[str, Any]:
		pass

	def explain_plan(self) -> dict[str, Any]:
		pass
