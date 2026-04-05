

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

Notes and Comments:
The pricing is an estimate based on data from the Kroger API. Full-sized grocery items are used when calculating prices. For example, if a recipe calls for 2 eggs, the price of an entire carton of eggs will be returned.

Three different pricing strategies are available:

- Cheapest
- Average (Top 3)
- Most Expensive

The total cost will vary depending on the pricing strategy selected by the user.

### Test Case 7 - Expensive Meal

- **Input:**
<img width="450" height="238" alt="image" src="https://github.com/user-attachments/assets/8e32e6c8-efe3-45ef-a66e-2f935590e6a6" />

**Normalized Ingredients:**
 1. beef chuck roast (meat): 1.34 lbs
 2. ground beef (meat): 1.15 lbs
 3. beef soup bones (meat): 1.15 lbs
 4. pork shoulder (meat): 12.53 lbs
 5. whole chicken (poultry): 5.85 lbs
 6. russet potatoes (produce): 4 count
 7. hamburger buns (bakery): 8 count
 8. garlic (produce): 3 bulbs
 9. celery (produce): 1 container
10. beef stock (pantry): 32 fl oz
11. chocolate pudding (snacks): 8 cups
12. avocado oil (pantry): 1 bottle
13. strawberry banana smoothie (beverages): 52 fl oz
14. fruit juice (beverages): 32 fl oz
15. iceberg lettuce (produce): 1 bag
16. romaine lettuce (produce): 1 bag
17. carrot (produce): 1 bag
18. pea pods (produce): 1 bag
19. radish (produce): 1 bag
20. red cabbage (produce): 1 bag
    
**Retrieved Recipe(s):**
1. ALGERIAN KEFTA (MEATBALLS)
   - Category: Beef
   - Match: 2/8 ingredients (25%)
   - Missing: 6 ingredients

2. GARLICKY PRAWNS WITH SHERRY
   - Category: Seafood
   - Match: 1/5 ingredients (20%)
   - Missing: 4 ingredients

3. KOFTA BURGERS
   - Category: Lamb
   - Match: 2/11 ingredients (18%)
   - Missing: 9 ingredients
  
**Generated Output Summary:**
  - Recipe Name: Garlicky Beef Kofta Burgers with Root Vegetable Slaw
  - Category: Main Course
  - Prep Time: 25 minutes
  - Servings: 4

Ingredients:
  - 1 lb ground beef
  - 4 hamburger buns
  - 2 large russet potatoes
  - 4 cloves garlic, minced
  - 1 stalk celery, very finely minced
  - 1/4 cup beef stock
  - 1 cup red cabbage, shredded
  - 1 large carrot, grated
  - 4 radishes, thinly sliced
  - 1/2 cup pea pods, thinly sliced lengthwise
  - 2 tbsp fruit juice (for the slaw dressing)
  - 4 leaves iceberg lettuce
  - 3 tbsp avocado oil (plus more for frying)
  - Salt and pepper to taste

Instructions:
1. **Prepare the Potatoes:** Scrub the russet potatoes and cut them into thin wedges or fries. Toss with 1 tablespoon of avocado oil, salt, and pepper. Arrange on a baking sheet and roast at 425°F (220°C) for 20-25 minutes until golden and crisp.
2. **Make the Slaw:** In a medium bowl, combine the shredded red cabbage, grated carrot, sliced radishes, and pea pods. Whisk together the fruit juice, 1 tablespoon of avocado oil, salt, and pepper. Toss the dressing with the vegetables and set aside to marinate.
3. **Prepare the Kofta Patties:** In a large bowl, combine the ground beef, minced garlic, and finely minced celery. Add the beef stock (this keeps the patties moist, mimicking the texture of traditional kefta). Season generously with salt and pepper. Form into 4 oval or round patties, pressing a small indentation in the center of each to prevent bulging.
4. **Cook the Beef:** Heat a splash of avocado oil in a heavy skillet over medium-high heat. Sear the patties for 4–5 minutes per side, or until cooked to your desired level of doneness.
5. **Toast the Buns:** While the meat rests, split the hamburger buns and toast them in the same skillet (using the leftover juices and fat for extra flavor) until golden brown.
6. **Assemble:** Place a leaf of iceberg lettuce on the bottom bun. Top with the garlicky beef patty. Pile a generous amount of the crunchy root vegetable slaw on top of the meat. Finish with the top bun and serve alongside the hot potato wedges.

Chef's Notes:
• The finely minced celery and beef stock are the "secret" to keeping these burgers juicy and flavorful without the need for traditional binders like breadcrumbs.
• Using fruit juice in the slaw provides a necessary hit of acidity and sweetness that balances the richness of the beef and the punch of the raw garlic. 
• For an even deeper garlic flavor, you can mash one of the garlic cloves with a pinch of salt and a teaspoon of avocado oil to create a "garlic paste" to spread directly onto the toasted buns.

**Validation Result:**
  - Total Extracted: 20
  - Validated (high confidence): 20
  - Filtered (low confidence): 0
  - Ingredients mentioned in recipe: 11

VALIDATION FAILED
Found 8 unmatched ingredients in recipe:
  - thinly
  - shredded
  - lengthwise
  - tbsp
  - leaves
  - very
  - grated
  - stalk

DETAILED ANALYSIS

Expected ingredients: avocado oil, beef chuck roast, beef soup bones, beef stock, carrots, celery, chocolate pudding, garlic, ground beef, hamburger buns, iceberg lettuce, mixed fruit juice, pea pods, pork shoulder, radishes, red cabbage, romaine lettuce, russet potatoes, strawberry banana juice, whole chicken
Mentioned in recipe: avocado oil, beef stock, celery, garlic, ground beef, hamburger buns, iceberg lettuce, pea pods, radishes, red cabbage, russet potatoes

Unused ingredients: beef chuck roast, beef soup bones, carrots, chocolate pudding, mixed fruit juice, pork shoulder, romaine lettuce, strawberry banana juice, whole chicken

**Budget Result:**

  KROGER PRICING REQUEST
  - Ingredients: ground beef, hamburger buns, russet potatoes, garlic, celery, beef stock, red cabbage, shredded, carrot, radishes, thinly, pea pods, thinly, fruit juice, leaves iceberg lettuce, Salt and pepper
  - Zip: 78201
  - Strategy: first

KROGER PRICING RESULT
Item Prices:
  - ground beef: $13.99
  - hamburger buns: $3.79
  - russet potatoes: $1.49
  - garlic: $1.49
  - celery: $1.79
  - beef stock: N/A (no_price)
  - red cabbage, shredded: $1.79
  - carrot: $1.25
  - radishes, thinly: $1.79
  - pea pods, thinly: $2.69
  - fruit juice: $3.49
  - leaves iceberg lettuce: $2.99
  - Salt and pepper: $4.99

Priced Count: 12 / 13 \
Estimated Total: $41.54 \
Location: 01100002 (78201) \
Missing: beef stock \
Tier: medium | Selected Tier: expensive | Result: fail 
- **Pass/Fail:**
-   Fail: Asked for an expensive meal and returned a medium meal 

---

### Test Case 8 - Medium Meal

- **Input:**

  <img width="400" height="200" alt="image" src="https://github.com/user-attachments/assets/580b2621-f32b-4083-a29e-76f1f2cfe0e9" />

**Normalized Ingredients:**
 1. potato (vegetable): 1 bag
 2. tofu (protein): 1 package
 3. carrot (vegetable): 1 bag
 4. raspberry (fruit): 1 bag
 5. blueberry (fruit): 1 container
 6. baby spinach (vegetable): 1 container
 7. great northern bean (canned goods): 1 can
 8. garbanzo bean (canned goods): 1 can
 9. egg (dairy): 1 carton
10. greek yogurt (dairy): 1 container
11. baby bella mushroom (vegetable): 1 container
12. apple (fruit): 3 None
13. bell pepper (vegetable): 1 None
14. grape tomato (vegetable): 1 container
15. cucumber (vegetable): 2 None
16. ravioli (pasta): 1 bag
17. salad kit (vegetable): 1 bag
18. banana (fruit): 1 bunch
19. english muffin (bakery): 1 package
20. chocolate syrup (condiment): 1 bottle
21. ice cream (dessert): 1 pint
    
**Retrieved Recipe(s):**
  
1. BREAKFAST POTATOES
   - Category: Breakfast
   - Match: 2/8 ingredients (25%)
   - Missing: 6 ingredients

2. APPLE CAKE
   - Category: Dessert
   - Match: 2/9 ingredients (22%)
   - Missing: 7 ingredients

3. FISH SOUP (UKHA)
   - Category: Seafood
   - Match: 2/9 ingredients (22%)
   - Missing: 7 ingredients
     
**Generated Output Summary:**
  - Recipe Name: Garden Harvest Breakfast Skillet
  - Category: Main Course
  - Prep Time: 15 minutes
  - Servings: 2

**Ingredients:**
  - 2 medium potatoes, diced into 1/2-inch cubes
  - 1 carrot, peeled and finely diced
  - 1 bell pepper, chopped
  - 1 cup baby bella mushrooms, sliced
  - 1/2 cup grape tomatoes, halved
  - 1/2 cup garbanzo beans, drained and rinsed
  - 1 cup baby spinach
  - 2 eggs
  - 2 English muffins
  - 1/4 cup Greek yogurt
  - Cooking oil
  - Salt and pepper

**Instructions:**
1. Heat 2 tablespoons of cooking oil in a large skillet over medium heat.
2. Add the diced potatoes and carrots to the skillet. Season generously with salt and pepper. Cook for 10–12 minutes, stirring occasionally, until the potatoes are golden brown and tender.
3. Stir in the sliced mushrooms and bell peppers. Sauté for another 5 minutes until the mushrooms have softened and the peppers are tender.
4. Add the garbanzo beans and grape tomatoes to the pan. Cook for 2 minutes, allowing the tomatoes to just begin to soften.
5. Fold in the baby spinach and stir for about 1 minute until it is just wilted.
6. Use a spoon to create two small wells in the vegetable mixture. Crack one egg into each well. 
7. Cover the skillet with a lid and cook for 3–4 minutes, or until the egg whites are fully set but the yolks remain runny.
8. While the eggs finish, toast the English muffins until golden.
9. Serve the hash warm with a dollop of Greek yogurt on top to add creaminess, with the toasted English muffins on the side.

**Chef's Notes:**
The Greek yogurt in this recipe serves as a tangy, high-protein alternative to sour cream. If you prefer your potatoes extra crispy, ensure they are patted dry with a paper towel before adding them to the hot oil. For an extra layer of texture, you can lightly toast the garbanzo beans in the oil first before adding the other vegetables

**Validation Result:**
  - Total Extracted: 21
  - Validated (high confidence): 21
  - Filtered (low confidence): 0
  - Ingredients mentioned in recipe: 8

VALIDATION FAILED \
Found 8 unmatched ingredients in recipe:
  - drained
  - rinsed
  - halved
  - cubes
  - into
  - spinach
  - inch
  - peeled

DETAILED ANALYSIS 

Expected ingredients: baby bella mushrooms, bananas, blueberries, carrots, chocolate syrup, cucumber, eggs, english muffins, garbanzo beans, grape tomatoes, great northern beans, greek yogurt, ice cream, mixed greens, orange bell pepper, potatoes, raspberries, ravioli, red apples, salad kit, tofu
Mentioned in recipe: baby bella mushrooms, carrots, eggs, english muffins, garbanzo beans, grape tomatoes, greek yogurt, potatoes

Unused ingredients: bananas, blueberries, chocolate syrup, cucumber, great northern beans, ice cream, mixed greens, orange bell pepper, raspberries, ravioli, red apples, salad kit, tofu

**Budget Result:**
KROGER PRICING REQUEST \
Ingredients: potatoes, carrot, bell pepper, baby bella mushrooms, grape tomatoes, garbanzo beans, baby spinach, eggs, English muffins, Greek yogurt \
Zip: 78201 \
Strategy: average_top3 

KROGER PRICING RESULT 

Item Prices:
  - potatoes: $3.32
  - carrot: $1.25
  - bell pepper: $1.19
  - baby bella mushrooms: N/A (no_price)
  - grape tomatoes: $2.29
  - garbanzo beans: N/A (no_price)
  - baby spinach: N/A (no_price)
  - eggs: $1.52
  - English muffins: $2.52
  - Greek yogurt: $1.42

Priced Count: 7 / 10 \
Estimated Total: $13.51 \
Location: 01100002 (78201) \
Missing: baby bella mushrooms, garbanzo beans, baby spinach \
Tier: cheap | Selected Tier: medium | Result: fail 

- **Pass/Fail:**
  - Fail user selected a medium price tier returned cheap. Missed 3 ingredients in the price.

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
- **Passed:** 2
- **Failed:** 2
- **Common Issues:**
- **Key Improvements Needed:**

---
