
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Category(str, Enum):
    SPAM = "spam"
    SUPPORT = "support"
    BILLING = "billing"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    INTERNAL = "internal"
    NEWSLETTER = "newsletter"


class Action(str, Enum):
    ARCHIVE = "archive"
    REPLY = "reply"
    ESCALATE = "escalate"
    DELETE = "delete"
    FORWARD = "forward"


class RoutingDepartment(str, Enum):
    SUPPORT = "support"
    BILLING = "billing"
    MANAGEMENT = "management"
    SALES = "sales"
    NONE = "none"


class Email(BaseModel):
    id: str
    subject: str
    body: str
    sender: str
    timestamp: str


class Observation(BaseModel):
    email: Email
    task_id: str
    step_number: int
    max_steps: int
    task_description: str


class Action1(BaseModel):
    """Task 1: Simple urgency classification"""
    is_urgent: bool = Field(..., description="Whether the email is urgent")


class Action2(BaseModel):
    """Task 2: Category + Priority classification"""
    category: Category
    priority: Priority


class Action3(BaseModel):
    """Task 3: Full triage"""
    category: Category
    priority: Priority
    action: Action
    routing: RoutingDepartment
    summary: str = Field(..., description="One-line summary of the email", max_length=100)


class Reward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    breakdown: dict
    feedback: str


class StepResult(BaseModel):
    observation: Optional[Observation]
    reward: Reward
    done: bool
    info: dict


class EnvironmentState(BaseModel):
    task_id: str
    current_step: int
    max_steps: int
    total_score: float
    emails_processed: int
    current_email: Optional[Email]