
"""
Baseline Inference Script for Email Triage Environment
Uses keyword-based heuristics as a reproducible baseline agent.
Run: python baseline.py
"""

import re
from environment import EmailTriageEnv
from models import Action1, Action2, Action3, Category, Priority, Action, RoutingDepartment


# ─────────────────────────────────────────────
# Heuristic Baseline Agent
# ─────────────────────────────────────────────

URGENT_KEYWORDS = ["urgent", "down", "cannot access", "furious", "double charge",
                   "broken", "immediately", "critical", "asap", "emergency", "overdue"]

SPAM_KEYWORDS = ["winner", "prize", "congratulations", "click here", "limited time",
                 "act now", "million", "selected", "lucky"]

BILLING_KEYWORDS = ["invoice", "charge", "payment", "billing", "refund", "subscription",
                    "overdue", "account", "double charge"]

COMPLAINT_KEYWORDS = ["furious", "unacceptable", "terrible", "angry", "worst", "cancel",
                      "disgusting", "frustrated", "disappointed"]

SUPPORT_KEYWORDS = ["broken", "not working", "error", "help", "issue", "problem",
                    "cannot", "unable", "bug", "crash", "down"]

NEWSLETTER_KEYWORDS = ["newsletter", "edition", "monthly", "weekly digest", "subscribe",
                       "unsubscribe", "updates from"]

INTERNAL_KEYWORDS = ["team", "meeting", "rescheduled", "internal", "colleague",
                     "our company", "office", "hr", "staff"]


def classify_email(subject: str, body: str):
    """Heuristic classifier based on keyword matching."""
    text = (subject + " " + body).lower()

    # Determine if urgent
    is_urgent = any(kw in text for kw in URGENT_KEYWORDS)

    # Determine category
    if any(kw in text for kw in SPAM_KEYWORDS):
        category = Category.SPAM
    elif any(kw in text for kw in BILLING_KEYWORDS):
        category = Category.BILLING
    elif any(kw in text for kw in COMPLAINT_KEYWORDS):
        category = Category.COMPLAINT
    elif any(kw in text for kw in SUPPORT_KEYWORDS):
        category = Category.SUPPORT
    elif any(kw in text for kw in NEWSLETTER_KEYWORDS):
        category = Category.NEWSLETTER
    elif any(kw in text for kw in INTERNAL_KEYWORDS):
        category = Category.INTERNAL
    else:
        category = Category.INQUIRY

    # Determine priority
    if any(kw in text for kw in ["urgent", "immediately", "asap", "emergency", "double charge"]):
        priority = Priority.URGENT
    elif any(kw in text for kw in ["overdue", "down", "furious", "broken", "complaint"]):
        priority = Priority.HIGH
    elif category in [Category.NEWSLETTER, Category.SPAM]:
        priority = Priority.LOW
    else:
        priority = Priority.MEDIUM

    # Determine action
    if category == Category.SPAM:
        action = Action.DELETE
        routing = RoutingDepartment.NONE
    elif priority in [Priority.URGENT, Priority.HIGH] and category in [Category.COMPLAINT, Category.SUPPORT]:
        action = Action.ESCALATE
        routing = RoutingDepartment.MANAGEMENT
    elif category == Category.BILLING:
        action = Action.ESCALATE
        routing = RoutingDepartment.BILLING
    elif category == Category.INTERNAL or category == Category.NEWSLETTER:
        action = Action.ARCHIVE
        routing = RoutingDepartment.NONE
    elif category == Category.INQUIRY and "partnership" in text:
        action = Action.FORWARD
        routing = RoutingDepartment.SALES
    elif category in [Category.INQUIRY, Category.SUPPORT]:
        action = Action.REPLY
        routing = RoutingDepartment.SUPPORT
    else:
        action = Action.REPLY
        routing = RoutingDepartment.SUPPORT

    summary = subject[:80] + ("..." if len(subject) > 80 else "")

    return is_urgent, category, priority, action, routing, summary


# ─────────────────────────────────────────────
# Run Baseline on All Tasks
# ─────────────────────────────────────────────

def run_baseline(task_id: str, seed: int = 42) -> float:
    env = EmailTriageEnv(task_id=task_id, seed=seed)
    obs = env.reset()

    episode_scores = []
    step = 0

    print(f"\n{'='*50}")
    print(f"Task: {task_id.upper()} | Seed: {seed}")
    print(f"{'='*50}")

    while obs is not None:
        email = obs.email
        subject = email.subject
        body = email.body

        is_urgent, category, priority, action, routing, summary = classify_email(subject, body)

        # Build correct action type based on task
        if task_id == "task1":
            agent_action = Action1(is_urgent=is_urgent)
        elif task_id == "task2":
            agent_action = Action2(category=category, priority=priority)
        else:
            agent_action = Action3(
                category=category,
                priority=priority,
                action=action,
                routing=routing,
                summary=summary
            )

        result = env.step(agent_action)
        episode_scores.append(result.reward.score)

        print(f"Step {step+1}: {subject[:50]}")
        print(f"  Score: {result.reward.score:.3f} | {result.reward.feedback}")

        obs = result.observation
        step += 1

    avg = sum(episode_scores) / len(episode_scores)
    print(f"\nFinal Average Score: {avg:.4f} over {len(episode_scores)} emails")
    return avg


def main():
    print("Email Triage Environment — Baseline Inference Script")
    print("Reproducible seed: 42\n")

    results = {}
    for task_id in ["task1", "task2", "task3"]:
        score = run_baseline(task_id, seed=42)
        results[task_id] = score

    print("\n" + "="*50)
    print("BASELINE SUMMARY")
    print("="*50)
    for task_id, score in results.items():
        print(f"  {task_id}: {score:.4f}")
    overall = sum(results.values()) / len(results)
    print(f"  Overall: {overall:.4f}")
    print("="*50)


if __name__ == "__main__":
    main()