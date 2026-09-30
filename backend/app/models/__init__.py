"""SQLAlchemy ORM models for SkillPulse India.

Importing this package registers every mapper on the shared Base.metadata.
"""

from app.models.course import Course, course_skill
from app.models.district import District
from app.models.employer_signal import EmployerSignal
from app.models.job import JobPosting
from app.models.metrics import DemandPoint, SkillMetric
from app.models.recommendation import CourseAlignment, Recommendation
from app.models.skill import Skill
from app.models.training_provider import TrainingProvider

__all__ = [
    "District",
    "Skill",
    "JobPosting",
    "Course",
    "course_skill",
    "TrainingProvider",
    "EmployerSignal",
    "SkillMetric",
    "DemandPoint",
    "Recommendation",
    "CourseAlignment",
]
