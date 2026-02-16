# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design focused on clearly seperating data representation logic. Task, Pet and Scheduler
the tasks portion was responsible for representing an individual tasks storing attributes such as name, pet_id, due_time and duration.
the pet task represents a pet and servers as the owner of the taks
]the scheduler is responsible for all schedling logic
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
my design did change during implementation. i intially scheduling logic inside the scheduler class because conflict resolution are system level responsibilities, not properties of a single task. the change improved the seperation of concerns.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

- How did you decide which constraints mattered most?

the scheduler considered priority level, time constraits and recurring frequency
priority is the most important because pet care urgency varies and the time was secondary within each priority lebel because whats most important is more important than whats earliest

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

my scheduler placed a high priority task at 5pm before a medium priority task at 9am
it was reasonable because urgency matters more than the sequence and it also prevents forgotten taks and it matches what the pet owner is thinking such as "what is important" and not the time.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

i used Ai to help me design clean algorithm structures, and to also evaluate potential tradeoffs. 

The kind of prompts there were helpful was explain the time complexity and compare two solutions objectively when comparing what solutions to do.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

There was a moment where a solution returned either a task object or a string warning and i didnt accept it because mixed return types can create bugs 
- How did you evaluate or verify what the AI suggested?
i evalutated it by thinking about how the method would be used in productiion and refactored the turn to be more predictable
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested sorting correctness such as chronological ordering by due time and priority first sorting
and filtering logic such as filter by pet name, completing status and combined filter options.

these tests were important for correctness assurance  and by adding priority scheduling that didnt break existing features. also caught backward compatibility issues with capaitlized priorities. 
**b. Confidence**

- How confident are you that your scheduler works correctly?

I am pretty confident as there are a lot of passing tests and real vailidation but im not sure if multiple users were accessing if it would work still 

- What edge cases would you test next if you had more time?
time zone edge cases especially at midnight and also maximum task duration like for 24 hours
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satified with the claity and modularity of my scheduling logic

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add task deletion and editing and also improve conflict resolution instead of just warnings
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

one important thing I learned is that clear sturcture matters more that clever and complex solutiions. sometimes simplicity should be prefered and AI is more useful when I give it precise contraints and I verify the edge cases, design decisions etc.

Challenge 3:
I did gemini vs chatgpt and asked
"I am building a pet scheduling system in Python.

Design a clean, readable algorithm for handling weekly recurring tasks with automatic conflict resolution.

Requirements:



When a weekly task is marked complete:

Create a new task scheduled exactly 7 days later.

If the new task conflicts (overlapping duration) with another task for the same pet:

Automatically shift it forward in 30-minute increments.

Continue checking until a free slot is found.

Stop searching after 24 hours.

If no free slot is found:

Return a warning message.

Do not crash the program.

Preserve all task attributes except due_time.

Constraints:



Use Python.

Use datetime and timedelta properly.

Write readable, production-quality code.

Include a short explanation of the algorithm’s time complexity.

Prefer clarity over cleverness.

Then:



Provide the full method implementation.

Explain how the conflict detection works.

Suggest one potential optimization."

chatgpt was more pythonic as it used encapsulation and private helper methods making the code easier to read Gemini was more simple and and didnt have an entire lists of taks or instructions to make it work.
