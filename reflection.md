# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    1. a user should be able to add a pet
    2. a user will have his profile under which he will add his pets 
    3. Inside  a pets profile it will contain all the details of the pet
    4. After that  a user can be able schedule the tasks for pet like walk, feeding, grooming on basis of priority
    5. create a daily plan and why it craeted a plan

- What classes did you include, and what responsibilities did you assign to each?

User

Responsible for storing the pet owner’s information.

Attributes:

userId
name
email
password
phoneNumber

Responsibilities:

createProfile()
addPet()
editProfile()
viewPets()

Relationship:

One User can have many Pets.
Pet

Responsible for storing details about each pet.

Attributes:

petId
name
age
type
breed
weight
healthNotes
specialNeeds

Responsibilities:

updatePetDetails()
viewPetProfile()
getPetCareNeeds()

Relationship:

Each Pet belongs to one User.
Each Pet can have many Tasks.
Task

Responsible for storing pet care activities.

Attributes:

taskId
taskName
taskType
description
priority
dueTime
status
frequency

Examples of task types:

Feeding
Walking
Grooming
Medication
Vet Visit
Playtime

Responsibilities:

createTask()
updateTask()
markTaskCompleted()
setPriority()
Schedule

Responsible for organizing tasks by time and priority.

Attributes:

scheduleId
date
taskList

Responsibilities:

addTaskToSchedule()
removeTaskFromSchedule()
sortTasksByPriority()
viewSchedule()
Plan

Responsible for creating the daily care plan.

Attributes:

planId
date
petId
dailyTasks
planReason

Responsibilities:

generateDailyPlan()
explainPlan()
updatePlan()

Example reason:

The plan was created because the pet has a high-priority feeding task in the morning, a walking
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

`Scheduler.detect_conflicts` checks whether two tasks' full `[start, end)` time
windows overlap (using `due_time` + `duration`), instead of the cheaper check of
only flagging tasks with an identical `due_time` string. The overlap check is
more accurate — it also catches a 15-minute vet call at 07:15 colliding with a
30-minute walk that started at 07:00, which an exact-match check would miss —
but it costs an O(n²) pairwise comparison across every pending task, and it
trusts that each task's `duration` estimate is realistic. For a single owner's
daily task list (a handful of tasks per pet), that O(n²) cost is negligible, so
trading a bit of extra computation for catching real, physically-impossible
overlaps was the right call here. It would stop being reasonable if PawPal+
ever scheduled for a shelter with hundreds of pets and tasks per day.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

`detect_conflicts` started as a manual sweep: sort tasks by start time, keep a
running `active` list of tasks whose window hasn't ended yet, and compare each
new task against that list. I asked the assistant how that method could be
simplified for readability, and it suggested replacing the sweep with
`itertools.combinations(tasks, 2)` filtered by the overlap condition — no
sorting, no manual "active window" bookkeeping, just "check every pair."
Before accepting it, I checked the actual complexity: the sweep's active-list
filtering is also O(n) per task in the worst case, so it's O(n²) overall too —
the combinations version isn't slower for a daily task list, just shorter and
easier to read. I ran both versions against the same test data (the 07:00
walk vs. 07:15 vet call, and the two 12:00 nail-trim tasks) and got identical
results, so I kept the simplified version.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
