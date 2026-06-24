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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
