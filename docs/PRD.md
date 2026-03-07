# Product Requirements Document (PRD)

### Overview
**Budget Bite** leverages the **Gemini API** for intelligent ingredient recognition and a **SQLite** database (seeded by **TheMealDB API**) to provide verified, grounded recipe recommendations for budget-conscious students.
1. Problem + target users
2. Goal/success metrics
3. MVP user stories
4. MVP scope vs. non-goals
5. Acceptance criteria
6. Assumptions + constraints

### Section 1 Problem + target users
* **The Problem:** Rising grocery costs and "food deserts" lead students to poor nutritional choices. Lack of affordable, healthy meal ideas contributes to long-term health risks like type 2 diabetes and hypertension.
* **Target Users:** * **Primary:** College students (TAMUSA) with limited budgets and kitchen tools.
    * **Secondary:** Busy parents needing quick, verified, and low-cost family meals.

### Section 2 Goal/success metrics
Success is defined by the app's ability to accurately translate a visual or text input into a verified recipe from the local cache.

| Metric | Target | Definition |
| :--- | :--- | :--- |
| **Grounding Accuracy** | 98% | % of recipes suggested that exist within the SQLite cache/TheMealDB. |
| **Gemini Recognition** | 90% | Success rate of the Gemini API correctly identifying ingredients from user photos. |
| **Local Cache Latency** | < 2 Seconds | Response time for retrieving recipes already stored in SQLite. |
| **API Fetch Latency** | < 6 Seconds | Response time when fetching new data from TheMealDB and updating SQLite. |

### Section 3 MVP user stories
1. Basic user story: As a student, I want a way to come up with a quick and affordable meal using the ingredients and cooking methods available to me, so that I can eat a good, healthy meal at an affordable price and save time having to come up with a meal.
2. I am a student with milk, cheese, and eggs, very few ingredients so the app offers the available recipes with the ingredients, but also offers recommendations of recipes with an appropriate budget tier depending on how much the ingredients cost to make the recommended.
3. User Story: As a mom, I want a healthy, affordable meal to feed my kids, so that I can save time and money, and my kids will be well-fed and have nutritious food to eat.

### Section 4 MVP scope vs. non-goals
**Must-Have Features**
- Gemini API Integration
- SQLite Database
- TheMealDB Grounding
- React Frontend

**Nice-to-have features**
- Nutritional Overlays
- Calorie Tracking

**Explicit non-goals**
- Will not be a budget tracker just budget how much the food costs.
- Will not strictly count your calories, it will provide information on calories consumed based on meals 
- tailor to a specific demographic, like Hispanic or white, but many different cultures

### Section 5 Acceptance criteria

- Allow the user to take pictures of their food/ingredients
- Produce a meal suggestion within 10 seconds
- Handle an edge case when the user takes a picture that contains no food/ingredients
- Fail safely when the edge case happens and display an error message to the user
- Give recommendations for ordering cheap ingredients.

### Section 6 Assumptions + constraints
* **Gemini API Limits:** We assume the free/student tier of Gemini provides enough RPM (requests per minute) for the demo.
* **TheMealDB Schema:** We assume the "Ingredient" fields in TheMealDB are consistent enough for basic string-matching or fuzzy-matching.
* **SQLite Maintenance:** The local database must be structured to prevent duplicate recipe entries during API fetches.
* **Milestone 1 Priority:** Demonstrating the "Full Loop"—Gemini identifies an item $\rightarrow$ SQLite is queried $\rightarrow$ A grounded recipe from TheMealDB is displayed.
