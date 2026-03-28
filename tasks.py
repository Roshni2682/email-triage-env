
from models import (
    Email, Action1, Action2, Action3,
    Priority, Category, Action, RoutingDepartment
)
from typing import List, Tuple
import json
import random


# ─────────────────────────────────────────────
# EMAIL DATASET
# ─────────────────────────────────────────────

EMAILS = [
    {
        "id": "e001",
        "subject": "URGENT: Server is down, production affected",
        "body": "Our main production server has been unreachable for the last 30 minutes. Customers cannot access the service. We need immediate help!",
        "sender": "ops@clientcorp.com",
        "timestamp": "2024-01-15T09:00:00Z",
        "ground_truth": {
            "is_urgent": True,
            "category": "support",
            "priority": "urgent",
            "action": "escalate",
            "routing": "management"
        }
    },
    {
        "id": "e002",
        "subject": "Monthly Newsletter - January Edition",
        "body": "Welcome to our January newsletter! This month we cover new product launches, team updates, and upcoming events. Enjoy reading!",
        "sender": "newsletter@company.com",
        "timestamp": "2024-01-15T08:00:00Z",
        "ground_truth": {
            "is_urgent": False,
            "category": "newsletter",
            "priority": "low",
            "action": "archive",
            "routing": "none"
        }
    },
    {
        "id": "e003",
        "subject": "Invoice overdue - Account #4521",
        "body": "Your invoice #INV-4521 for $2,500 was due on January 1st and remains unpaid. Please settle your balance immediately to avoid service suspension.",
        "sender": "billing@vendor.com",
        "timestamp": "2024-01-15T10:00:00Z",
        "ground_truth": {
            "is_urgent": True,
            "category": "billing",
            "priority": "high",
            "action": "escalate",
            "routing": "billing"
        }
    },
    {
        "id": "e004",
        "subject": "Congratulations! You have won a prize!",
        "body": "You have been selected as a lucky winner. Click here to claim your $1,000,000 prize. Act now! Limited time offer!",
        "sender": "noreply@totallylegit.ru",
        "timestamp": "2024-01-15T07:00:00Z",
        "ground_truth": {
            "is_urgent": False,
            "category": "spam",
            "priority": "low",
            "action": "delete",
            "routing": "none"
        }
    },
    {
        "id": "e005",
        "subject": "Question about your refund policy",
        "body": "Hi, I bought your product last week and I'm not completely satisfied. Could you please explain your refund process? I'd like to understand my options.",
        "sender": "customer123@gmail.com",
        "timestamp": "2024-01-15T11:00:00Z",
        "ground_truth": {
            "is_urgent": False,
            "category": "inquiry",
            "priority": "medium",
            "action": "reply",
            "routing": "support"
        }
    },
    {
        "id": "e006",
        "subject": "Team meeting rescheduled to Thursday",
        "body": "Hey team, just a quick note that our weekly sync has been moved from Wednesday to Thursday at 2pm. Please update your calendars. Thanks!",
        "sender": "manager@ourcompany.com",
        "timestamp": "2024-01-15T08:30:00Z",
        "ground_truth": {
            "is_urgent": False,
            "category": "internal",
            "priority": "medium",
            "action": "archive",
            "routing": "none"
        }
    },
    {
        "id": "e007",
        "subject": "I am FURIOUS about your terrible service",
        "body": "I have been a customer for 5 years and your latest update completely broke my workflow. I've lost hours of work. This is completely unacceptable and I'm considering canceling my subscription!",
        "sender": "angry.customer@email.com",
        "timestamp": "2024-01-15T12:00:00Z",
        "ground_truth": {
            "is_urgent": True,
            "category": "complaint",
            "priority": "high",
            "action": "escalate",
            "routing": "management"
        }
    },
    {
        "id": "e008",
        "subject": "Can you add dark mode to your app?",
        "body": "Hi support team, I love using your app but would really appreciate a dark mode option. Many apps have this now and it's easier on the eyes at night. Thanks for considering!",
        "sender": "user456@email.com",
        "timestamp": "2024-01-15T13:00:00Z",
        "ground_truth": {
            "is_urgent": False,
            "category": "inquiry",
            "priority": "low",
            "action": "reply",
            "routing": "support"
        }
    },
    {
        "id": "e009",
        "subject": "Double charge on my credit card",
        "body": "I was charged twice for my subscription this month - $29.99 appears twice on my statement. Please refund the duplicate charge immediately. Order ID: ORD-78234.",
        "sender": "upset.user@email.com",
        "timestamp": "2024-01-15T14:00:00Z",
        "ground_truth": {
            "is_urgent": True,
            "category": "billing",
            "priority": "urgent",
            "action": "escalate",
            "routing": "billing"
        }
    },
    {
        "id": "e010",
        "subject": "Partnership opportunity for mutual growth",
        "body": "Hello, I represent XYZ Corp and we'd love to explore a potential partnership with your company. We believe there's a great synergy between our products. Would you be open to a call next week?",
        "sender": "partnerships@xyzcorp.com",
        "timestamp": "2024-01-15T15:00:00Z",
        "ground_truth": {
            "is_urgent": False,
            "category": "inquiry",
            "priority": "medium",
            "action": "forward",
            "routing": "sales"
        }
    },
]


def get_task_emails(task_id: str, seed: int = 42) -> List[dict]:
    rng = random.Random(seed)
    emails = EMAILS.copy()
    rng.shuffle(emails)
    if task_id == "task1":
        return emails[:5]
    elif task_id == "task2":
        return emails[:7]
    else:
        return emails


# ─────────────────────────────────────────────
# TASK DEFINITIONS
# ─────────────────────────────────────────────

TASK_DEFINITIONS = {
    "task1": {
        "name": "Urgency Classification",
        "difficulty": "easy",
        "description": "For each email, determine whether it is urgent (True) or not urgent (False). Focus on keywords like 'URGENT', production issues, complaints, and billing problems.",
        "action_model": "Action1",
        "max_steps": 5,
    },
    "task2": {
        "name": "Category and Priority Assignment",
        "difficulty": "medium",
        "description": "For each email, assign the correct category (spam/support/billing/complaint/inquiry/internal/newsletter) and priority level (low/medium/high/urgent).",
        "action_model": "Action2",
        "max_steps": 7,
    },
    "task3": {
        "name": "Full Email Triage",
        "difficulty": "hard",
        "description": "Perform complete email triage: assign category, priority, recommended action (archive/reply/escalate/delete/forward), routing department, and write a one-line summary.",
        "action_model": "Action3",
        "max_steps": 10,
    },
}


# ─────────────────────────────────────────────
# GRADERS
# ─────────────────────────────────────────────

def grade_task1(action: Action1, ground_truth: dict) -> Tuple[float, dict, str]:
    correct = action.is_urgent == ground_truth["is_urgent"]
    score = 1.0 if correct else 0.0
    breakdown = {"urgency_correct": correct}
    feedback = "Correct urgency classification!" if correct else f"Wrong. Expected is_urgent={ground_truth['is_urgent']}"
    return score, breakdown, feedback


def grade_task2(action: Action2, ground_truth: dict) -> Tuple[float, dict, str]:
    cat_correct = action.category.value == ground_truth["category"]
    pri_correct = action.priority.value == ground_truth["priority"]

    # Priority partial credit: adjacent priorities get 0.5
    priority_score = 1.0 if pri_correct else _adjacent_priority_score(action.priority.value, ground_truth["priority"])
    category_score = 1.0 if cat_correct else 0.0

    score = round((category_score * 0.5) + (priority_score * 0.5), 3)

    breakdown = {
        "category_correct": cat_correct,
        "priority_correct": pri_correct,
        "category_score": category_score,
        "priority_score": priority_score,
    }
    feedback = f"Category: {'✓' if cat_correct else '✗ (expected ' + ground_truth['category'] + ')'}. Priority: {'✓' if pri_correct else '✗ (expected ' + ground_truth['priority'] + ')'}."
    return score, breakdown, feedback


def grade_task3(action: Action3, ground_truth: dict) -> Tuple[float, dict, str]:
    cat_correct = action.category.value == ground_truth["category"]
    pri_correct = action.priority.value == ground_truth["priority"]
    act_correct = action.action.value == ground_truth["action"]
    rout_correct = action.routing.value == ground_truth["routing"]

    priority_score = 1.0 if pri_correct else _adjacent_priority_score(action.priority.value, ground_truth["priority"])

    # Summary quality: basic check (non-empty and reasonable length)
    summary_score = 1.0 if (10 < len(action.summary) <= 100) else 0.5

    breakdown = {
        "category_correct": cat_correct,
        "priority_score": priority_score,
        "action_correct": act_correct,
        "routing_correct": rout_correct,
        "summary_score": summary_score,
    }

    score = round(
        (1.0 if cat_correct else 0.0) * 0.25 +
        priority_score * 0.25 +
        (1.0 if act_correct else 0.0) * 0.25 +
        (1.0 if rout_correct else 0.0) * 0.15 +
        summary_score * 0.10,
        3
    )

    parts = []
    parts.append(f"Category: {'✓' if cat_correct else '✗ expected ' + ground_truth['category']}")
    parts.append(f"Priority: {'✓' if pri_correct else '✗ expected ' + ground_truth['priority']}")
    parts.append(f"Action: {'✓' if act_correct else '✗ expected ' + ground_truth['action']}")
    parts.append(f"Routing: {'✓' if rout_correct else '✗ expected ' + ground_truth['routing']}")
    feedback = " | ".join(parts)

    return score, breakdown, feedback


def _adjacent_priority_score(predicted: str, actual: str) -> float:
    """Give partial credit for adjacent priority levels"""
    order = ["low", "medium", "high", "urgent"]
    if predicted not in order or actual not in order:
        return 0.0
    diff = abs(order.index(predicted) - order.index(actual))
    return 0.5 if diff == 1 else 0.0


GRADERS = {
    "task1": grade_task1,
    "task2": grade_task2,
    "task3": grade_task3,
}