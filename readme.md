
# 📧 Email Triage OpenEnv

A **real-world email triage environment** for AI agent training, built for the OpenEnv × Scaler Hackathon.

An AI agent reads incoming emails and must classify, prioritize, and route them — simulating the daily inbox management work done by support teams worldwide.

---

## 🎯 Tasks

| Task | Difficulty | Description | Max Steps |
|------|------------|-------------|-----------|
| `task1` | Easy | Binary urgency classification | 5 |
| `task2` | Medium | Category + Priority assignment | 7 |
| `task3` | Hard | Full triage: category, priority, action, routing, summary | 10 |

---

## 🔧 Action & Observation Spaces

### Observation Space
```json
{
  "email": {
    "id": "string",
    "subject": "string",
    "body": "string",
    "sender": "string",
    "timestamp": "ISO 8601 string"
  },
  "task_id": "string",
  "step_number": "int",
  "max_steps": "int",
  "task_description": "string"
}
```

### Action Spaces

**Task 1 (Easy)**
```json
{ "is_urgent": true }
```

**Task 2 (Medium)**
```json
{
  "category": "spam | support | billing | complaint | inquiry | internal | newsletter",
  "priority": "low | medium | high | urgent"
}
```

**Task 3 (Hard)**
```json
{
  "category": "spam | support | billing | complaint | inquiry | internal | newsletter",
  "priority": "low | medium | high | urgent",
  "action": "archive | reply | escalate | delete | forward",
  "routing": "support | billing | management | sales | none",
  "summary": "One-line summary (max 100 chars)"
}
```

### Reward
- Returns a float in `[0.0, 1.0]`
- **Partial credit** awarded per field — not just binary win/loss
- Task 1: binary correct/incorrect
- Task 2: 50% category + 50% priority (adjacent priorities get 0.5)
- Task 3: 25% category + 25% priority + 25% action + 15% routing + 10% summary

---

## 🚀 Setup & Running

### Local
```bash
pip install -r requirements.txt

# Run baseline agent
python baseline.py

# Start API server
uvicorn server:app --reload --port 7860
```

### Docker
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/reset` | Start new episode, returns session_id + first observation |
| POST | `/step` | Submit action, get reward + next observation |
| GET | `/state/{session_id}` | Get current environment state |
| GET | `/info/{task_id}` | Get task metadata |
| GET | `/health` | Health check |

### Example Usage
```python
import requests

BASE = "http://localhost:7860"

# Start episode
r = requests.post(f"{BASE}/reset", json={"task_id": "task3", "seed": 42})
session_id = r.json()["session_id"]
obs = r.json()["observation"]

# Step
result = requests.post(f"{BASE}/step", json={
    "session_id": session_id,
    "action": {
        "category": "support",
        "priority": "urgent",
        "action": "escalate",
        "routing": "management",
        "summary": "Production server is down, customers affected."
    }
})
print(result.json()["reward"])
```

---

## 📊 Baseline Results

Keyword-heuristic baseline agent (seed=42):

| Task | Score |
|------|-------|
| task1 | ~0.80 |
| task2 | ~0.65 |
| task3 | ~0.55 |

Run `python baseline.py` to reproduce.

---

## 📁 Project Structure
```
email-triage-env/
├── environment.py   # Core OpenEnv: step() / reset() / state()
├── models.py        # Pydantic models for obs/action/reward
├── tasks.py         # 3 tasks, email dataset, graders
├── baseline.py      # Reproducible baseline inference script
├── server.py        # FastAPI server for HF Spaces
├── openenv.yaml     # OpenEnv metadata
├── Dockerfile
├── requirements.txt
└── README.md
```