# Product Requirements Document (PRD)

### Overview
1. Problem + target users
2. Goal/success metrics
3. MVP user stories
4. MVP scope vs. non-goals
5. Acceptance criteria
6. Assumptions + constraints

### Section 1 Problem + target users
- The problem that exists today is high grocery prices, and the people, especially college students, who suffer because of it, resulting in poor nutrition. A lack of healthy meals results in chronic diseases like heart disease, type 2 diabetes, obesity, hypertension, and certain cancers.

### Section 2 Goal/success metrics
- Accuracy: The app should identify food with a 85% accuracy rate. 
- Time Saved: The app should save users time when planning and cooking meals. Save users an average of 15 minutes for each meal.
- User Satisfaction: Conduct a user survey to weigh the effectiveness and usability of the app. 

### Section 3 MVP user stories
1. Basic user story: As a student, I want a way to come up with a quick and affordable meal using the ingredients and cooking methods available to me, so that I can eat a good, healthy meal at an affordable price and save time having to come up with a meal.

2. User Story As a mom, I want a healthy, affordable meal to feed my kids, so that I can save time and money, and my kids will be well-fed and have nutritious food to eat.

### Section 4 MVP scope vs. non-goals
**Must have Features**
- Camera
- AI to detect the food/ingredients in image
- UI

**Nice-to-have features**
- Calories tracking

**Explicit non-goals**
- That will cook for you
- Idk work in progress


### Section 5 Acceptance criteria

Allow the user to take pictures of their food/ingredients
Produce a meal suggestion within 10 seconds
Handle an edge case when the user takes a picture that contains no food/ingredients
Fail safely when the edge case happens and display an error message to the user

### Section 6 Assumptions + constraints
- Data access (what data you do/don’t have): 
- Time constraints (what can be done by Milestone 2):
- Ethics/privacy limits (safety boundaries, consent): Safeguards on the AI 
- Platform constraints (APIs, cost limits, deployment limits):
