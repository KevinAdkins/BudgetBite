

## ✅ Successful Recipe Cases (4)

### Test Case 1

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

### Test Case 2

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

### Test Case 3

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

### Test Case 4

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

## ❌ Refusal Cases (2)

### Test Case 5

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

### Test Case 6

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

## 💸 Budget-Failure Cases (2)

### Test Case 7

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

### Test Case 8

- **Input:**
- **Normalized Ingredients:**
- **Retrieved Recipe(s):**
- **Generated Output Summary:**
- **Validation Result:**
- **Budget Result:**
- **Pass/Fail:**

---

## ⚠️ Edge Cases (2)

### Test Case 9 - Non Food Image

- **Input:**\
  <img width="149" height="148" alt="image" src="https://github.com/user-attachments/assets/395d64f7-39cc-420e-980a-18e4e5ea7c54" />

- **Normalized Ingredients:** None since there are no ingredients in the image
- **Retrieved Recipe(s):** None
- **Generated Output Summary:** None
- **Validation Result:** None
- **Budget Result:** None
- **Pass/Fail:** Passed it threw an error when the image passed had no food items\
<img width="514" height="435" alt="image" src="https://github.com/user-attachments/assets/ff61b909-8354-45d5-b209-73ce0a53241b" />


---

### Test Case 10 - Food In Containers

- **Input:** Food in plastic containners in the fridge. Difficult to tell what it is. \
  <img width="567" height="325" alt="image" src="https://github.com/user-attachments/assets/ccc19240-c2b9-4244-bb8b-b3f18e55b6ac" />
- **Normalized Ingredients:** Not very accurate
  1. cheddar cheese (Dairy): 1.5 cups
  2. stew (Prepared Meals): 2 cups
  3. carrots (Vegetables): 1 cup
- **Retrieved Recipe(s):** Not the best retrived recipes
1. FISH SOUP (UKHA)
   - Category: Seafood
   - Match: 1/9 ingredients (11%)
   - Missing: 8 ingredients
2. CARROT CAKE
   - Category: Dessert
   - Match: 1/12 ingredients (8%)
   - Missing: 11 ingredients
3. LAMB TAGINE
   - Category: Lamb
   - Match: 1/15 ingredients (7%)
   - Missing: 14 ingredients
  
  **Generated Output Summary:**
- Recipe Name: Cheesy Carrot-Crusted Stew Bake
- Category: Main Course
- Prep Time: 10 minutes
- Servings: 2 servings

Ingredients:
- 2 cups pre-made stew (beef, lamb, or vegetable)
- 2 large carrots
- 1/2 cup cheddar cheese, shredded
- 1 tbsp cooking oil
- Salt and pepper to taste

Instructions:
1. **Prepare the Carrots:** Peel the carrots. Grate one carrot using a box grater and thinly slice the other into rounds.
2. **Sauté:** Heat the cooking oil in a small oven-safe skillet or saucepan over medium heat. Add the sliced carrots and sauté for 4-5 minutes until they begin to soften and develop a slight sweetness (inspired by the aromatics in tagine and soup).
3. **Simmer the Stew:** Pour the pre-made stew into the skillet with the sliced carrots. Bring to a gentle simmer, stirring occasionally to combine the flavors. Season with a pinch of salt and pepper if needed.
4. **Create the Topping:** In a small bowl, toss the shredded cheddar cheese with the grated carrot. This mixture provides a unique texture inspired by the moisture of carrot cake but kept savory.
5. **Bake/Melt:** Spread the cheese and grated carrot mixture evenly over the top of the simmering stew. 
6. **Finish:** If using an oven-safe skillet, place it under a broiler for 2-3 minutes until the cheese is bubbly and golden brown. Alternatively, cover the pan with a lid for 3-5 minutes until the cheese is completely melted and the grated carrots are tender.
7. **Serve:** Let it sit for a minute before serving directly from the pan.

Chef's Notes:
The grated carrot mixed into the cheese topping adds a natural sweetness and extra body to the dish, similar to how carrots function in a cake. If your "stew" ingredient is quite thick, add a splash of water or broth while simmering to ensure it doesn't dry out during the cheese-melting phase.

**Validation Result:**

- Total Extracted: 3
- Validated (high confidence): 3
- Filtered (low confidence): 0
- Ingredients mentioned in recipe: 2

VALIDATION FAILED:

Found 3 unmatched ingredients in recipe:
  - ⚠ pasta
  - ⚠ tbsp
  - ⚠ reserved

DETAILED ANALYSIS:
- Expected ingredients: carrots, corn, shredded cheddar cheese
- Mentioned in recipe: carrots, shredded cheddar cheese

Unused ingredients: corn
- **Budget Result:** \
  KROGER PRICING REQUEST 
  - Ingredients: pre-made stew, carrots, cheddar cheese, shredded, Salt and pepper to taste
  - Zip: 78201
  - Strategy: average_top3

  KROGER PRICING RESULT 
  - Priced Count: 3 / 4 
  - Estimated Total: $12.89
  - Location: 01100002 (78201)
  - Missing: Salt and pepper to taste
  - Tier: cheap
- **Pass/Fail:**
  -  Fail, this is a tough image to pull ingredients from

---

## 📊 Summary

- **Total Tests:** 10
- **Passed:**
- **Failed:**
- **Common Issues:**
- **Key Improvements Needed:**

---
