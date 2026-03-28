
"""
Email Triage OpenEnv Environment
Implements the OpenEnv spec: step() / reset() / state() API
"""

from models import (
    Email, Observation, Reward, StepResult, EnvironmentState,
    Action1, Action2, Action3
)
from tasks import TASK_DEFINITIONS, EMAILS, get_task_emails, GRADERS
from typing import Union
import uuid


ActionType = Union[Action1, Action2, Action3]


class EmailTriageEnv:
    """
    A real-world email triage environment for AI agent training.
    
    The agent reads emails one by one and must classify/triage them
    according to the active task difficulty.
    """

    def __init__(self, task_id: str = "task1", seed: int = 42):
        if task_id not in TASK_DEFINITIONS:
            raise ValueError(f"task_id must be one of {list(TASK_DEFINITIONS.keys())}")
        
        self.task_id = task_id
        self.seed = seed
        self.task_def = TASK_DEFINITIONS[task_id]
        self._emails = get_task_emails(task_id, seed)
        self._reset_state()

    def _reset_state(self):
        self._step_index = 0
        self._scores = []
        self._done = False
        self._session_id = str(uuid.uuid4())

    # ─────────────────────────────────────────────
    # OpenEnv Core API
    # ─────────────────────────────────────────────

    def reset(self) -> Observation:
        """Reset environment to initial state. Returns first observation."""
        self._reset_state()
        return self._make_observation()

    def step(self, action: ActionType) -> StepResult:
        """
        Take one step: evaluate the action against the current email.
        Returns observation, reward, done, info.
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        current_email_data = self._emails[self._step_index]
        ground_truth = current_email_data["ground_truth"]

        # Grade the action
        grader = GRADERS[self.task_id]
        score, breakdown, feedback = grader(action, ground_truth)
        self._scores.append(score)

        reward = Reward(
            score=score,
            breakdown=breakdown,
            feedback=feedback
        )

        self._step_index += 1
        max_steps = self.task_def["max_steps"]

        if self._step_index >= max_steps or self._step_index >= len(self._emails):
            self._done = True
            next_obs = None
        else:
            next_obs = self._make_observation()

        info = {
            "session_id": self._session_id,
            "email_id": current_email_data["id"],
            "step": self._step_index,
            "cumulative_score": round(sum(self._scores) / len(self._scores), 4),
            "ground_truth": ground_truth,
        }

        return StepResult(
            observation=next_obs,
            reward=reward,
            done=self._done,
            info=info
        )

    def state(self) -> EnvironmentState:
        """Return current environment state."""
        current_email = None
        if not self._done and self._step_index < len(self._emails):
            e = self._emails[self._step_index]
            current_email = Email(**{k: v for k, v in e.items() if k != "ground_truth"})

        avg_score = round(sum(self._scores) / len(self._scores), 4) if self._scores else 0.0

        return EnvironmentState(
            task_id=self.task_id,
            current_step=self._step_index,
            max_steps=self.task_def["max_steps"],
            total_score=avg_score,
            emails_processed=len(self._scores),
            current_email=current_email
        )

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────

    def _make_observation(self) -> Observation:
        email_data = self._emails[self._step_index]
        email = Email(**{k: v for k, v in email_data.items() if k != "ground_truth"})
        return Observation(
            email=email,
            task_id=self.task_id,
            step_number=self._step_index,
            max_steps=self.task_def["max_steps"],
            task_description=self.task_def["description"]
        )

    def get_task_info(self) -> dict:
        return {
            "task_id": self.task_id,
            **self.task_def,
            "num_emails": len(self._emails),
        }


# ─────────────────────────────────────────────
# Quick sanity check
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Task 1: Urgency Classification ===")
    env = EmailTriageEnv(task_id="task1")
    obs = env.reset()
    print(f"First email: {obs.email.subject}")

    result = env.step(Action1(is_urgent=True))
    print(f"Score: {result.reward.score} | Feedback: {result.reward.feedback}")
    print(f"Done: {result.done}")

    print("\n=== Task 3: Full Triage ===")
    env3 = EmailTriageEnv(task_id="task3")
    obs3 = env3.reset()
    print(f"First email: {obs3.email.subject}")
    result3 = env3.step(Action3(
        category="support",
        priority="urgent",
        action="escalate",
        routing="management",
        summary="Production server down, immediate action needed."
    ))
    print(f"Score: {result3.reward.score} | Feedback: {result3.reward.feedback}")