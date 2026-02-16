# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

PawPal+ now includes intelligent algorithmic features for enhanced task management. The system implements **chronological sorting** using tuple-based comparison to arrange tasks by due time, placing unscheduled tasks at the end. **Flexible filtering** enables querying tasks by pet name, completion status, or both, using composable filter logic for efficient queries. **Conflict detection** employs pairwise comparison (O(n²)) to identify overlapping time windows between tasks, distinguishing same-pet versus cross-pet conflicts using interval overlap algorithms. The scheduler uses a **greedy first-fit approach** to generate daily plans, prioritizing tasks by importance and time while respecting available minutes—a practical strategy balancing efficiency and readability, though not guaranteeing optimal solutions in all cases. **Automatic recurring task regeneration** handles daily, weekly, and monthly frequencies by creating successor tasks when items are completed, ensuring continuous care schedules without manual updates. These enhancements make PawPal+ an algorithmically-aware scheduling assistant suitable for real-world pet care coordination.
