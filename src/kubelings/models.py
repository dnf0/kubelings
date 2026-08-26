"""Data models for Kubelings curriculum, chapters, and exercises."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ExerciseStatus(str, Enum):
    """Execution and completion status of an exercise."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Exercise:
    """Represents an individual exercise in the curriculum."""

    name: str
    title: str
    path: str
    chapter_name: str
    hints: list[str] = field(default_factory=list)
    requires_cluster: bool = False

    @property
    def file_path(self) -> Path:
        """Return the filesystem Path for the exercise starter file."""
        return Path(self.path)

    @property
    def solution_path(self) -> Path:
        """Return the filesystem Path for the reference solution file."""
        return Path(self.path.replace("exercises/", "solutions/"))


@dataclass
class Chapter:
    """Represents a chapter grouping multiple related exercises."""

    number: int
    name: str
    title: str
    description: str
    exercises: list[Exercise] = field(default_factory=list)


@dataclass
class Manifest:
    """Curriculum manifest containing all chapters and exercises."""

    chapters: list[Chapter] = field(default_factory=list)

    @property
    def all_exercises(self) -> list[Exercise]:
        """Flattened list of all exercises across all chapters in order."""
        exercises: list[Exercise] = []
        for chapter in self.chapters:
            exercises.extend(chapter.exercises)
        return exercises
