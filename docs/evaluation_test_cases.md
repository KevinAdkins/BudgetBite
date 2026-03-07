# Evaluation Report

## Project: AI Ingredient Detection and Recipe Generation System

This section presents the evaluation of the ingredient detection and recipe generation system using a dataset of **20 test images**. The test cases are divided into four categories based on difficulty:

- Easy (clear ingredient images)
- Medium (lower quality images)
- Hard (cluttered images with many ingredients)
- Edge Cases (images without food)

Errors related to missing files, API rate limits, or runtime exceptions were excluded from the evaluation results.

---

# Test Dataset Overview

| Category | Description | Number of Tests |
|--------|-------------|----------------|
| Easy | Clear images with ingredients forming an obvious dish | 5 |
| Medium | Lower quality images or partial ingredient visibility | 5 |
| Hard | Images with many ingredients or cluttered scenes | 5 |
| Edge Cases | Non-food images or invalid inputs | 5 |

Total evaluation images: **20**

---

# Evaluation Metrics

The system was evaluated using the following metrics.

### Ingredient Extraction Accuracy
Measures how many expected ingredients were correctly detected.

### Retrieval Accuracy
Measures whether the retrieved recipe matches the ingredients detected.

### Hallucination Rate
Measures the number of ingredients incorrectly added by the model.


### Refusal Accuracy
Measures whether the system correctly refuses non-food inputs.

---

# Easy Test Results

Easy test cases contained high-quality images with clearly visible ingredients.

| Test Case | Expected Dish | Accuracy | Hallucination Rate | Notes |
|---------|---------------|----------|-------------------|------|
| Easy 1 | Burger | 1.00 | 0.20 | All main ingredients detected |
| Easy 2 | Fish Tacos | 0.50 | 0.86 | Several extra ingredients added |
| Easy 3 | Fried Chicken Sandwich | 0.100 | 0.0 | Passed |
| Easy 4 | Spaghetti | 1.00 | 0.0 | Passed |
| Easy 5 | Steak | 1.00 | 0.38 | Minor seasoning hallucinations |

## Syrian Spaghetti (From Recipe Database)

**Category:** Pasta  
**Recipe ID:** 53093  

---

### Ingredients

- 16 oz spaghetti  
- 8 oz tomato sauce  
- 6 oz tomato puree  
- 1 teaspoon cinnamon  
- 1/4 cup vegetable oil  
- dash of salt  
- dash of pepper  

---

### Instructions

1. Preheat oven to **350°F (175°C)** and grease a **9×13 inch baking dish**.

2. Bring a large pot of **lightly salted water** to a boil.

3. Add the **spaghetti** and cook for **8–10 minutes** or until **al dente**.

4. Drain the pasta and stir in:
   - tomato sauce  
   - tomato puree  
   - cinnamon  
   - vegetable oil  
   - salt  
   - pepper  

5. Transfer the mixture to the prepared baking dish.

6. Bake in the preheated oven for **1 hour**, or until the top becomes **crispy and slightly crunchy**.

---

### Notes

- This Syrian-style baked spaghetti uses **cinnamon** to add a subtle warm flavor.
- Best served hot with a side salad or fresh bread.

## Generated Recipe

**Hearty Meat Sauce Spaghetti**

A comforting and classic dish featuring spaghetti topped with a rich, slow-simmered sauce made from a blend of ground beef and pork, aromatic vegetables, and marinara.

**Ingredients Used:**
*   1 lb spaghetti
*   2 stalks celery
*   1 whole onion
*   1 whole shallot
*   5 whole carrots
*   24.5 oz marinara sauce
*   1.20 lb ground beef and pork blend
*   Salt and pepper (to taste)

**Preparation Steps:**

1.  **Prepare Vegetables:** Dice the onion and shallot. Finely chop the celery and carrots.
2.  **Cook Meat:** In a large pot or deep skillet, brown the ground beef and pork blend over medium-high heat. Break up the meat with a spoon as it cooks. Once fully browned, drain any excess fat. Season with salt and pepper.
3.  **Sauté Vegetables:** Add the diced onion, shallot, chopped celery, and carrots to the pot with the cooked meat. Sauté over medium heat for 8-10 minutes, stirring occasionally, until the vegetables soften.
4.  **Simmer Sauce:** Pour in the marinara sauce. Stir everything together well. Bring the sauce to a gentle simmer, then reduce the heat to low, cover, and let it cook for at least 30 minutes (or longer for a richer flavor), stirring occasionally. Season with additional salt and pepper if needed.
5.  **Cook Spaghetti:** While the sauce simmers, bring a large pot of salted water to a rolling boil. Add the spaghetti and cook according to package directions until al dente. Drain well.
6.  **Serve:** Serve the cooked spaghetti topped generously with the hearty meat sauce.

### Observations

- The system performs best on **high-quality ingredient images**.
- Core ingredients were consistently detected.
- Hallucinated ingredients were typically **seasonings or cooking oils**.

---

# Medium Test Results

Medium test cases contained lower-quality images or more complex ingredient combinations.

| Test Case | Accuracy | Hallucination Rate | Observations |
|---------|----------|-------------------|-------------|
| Medium 1 | 0.65 | 0.43 | Low quality image |
| Medium 2 | 0.73 | 0.18 | Correct protein detection |
| Medium 3 | 0.90 | 0.52 | Many extra ingredients detected |
| Medium 4 | 1.00 | 0.56 | Crowded grocery image |
| Medium 5 | 0.88 | 0.56 | Packaged foods increased hallucination |

### Observations

- Ingredient recall remained strong.
- Hallucination rates increased in **crowded scenes or grocery images**.
- Packaged foods confused the detection model.

### Medium 1 Generated Recipe 

**Savory Beef & Onion Skillet**

A simple and hearty skillet meal featuring ground beef and two types of onions, served alongside fresh bread and tangy dill pickles for a complete, comforting dish.

**Ingredients:**
*   2 packages Ground Beef
*   4 count Yellow Onions
*   2 count White Onions
*   1 bag Bread
*   1 jar Dill Pickles
*   Salt (to taste)
*   Pepper (to taste)

**Steps to Prepare:**
1.  Peel and dice all yellow and white onions into small, even pieces.
2.  In a large skillet, place the ground beef over medium heat. Break up the beef with a spoon and cook until it is fully browned. Drain any excess fat from the skillet.
3.  Add the diced onions to the skillet with the cooked ground beef. Continue to cook, stirring occasionally, until the onions are softened and translucent, which should take about 8-10 minutes.
4.  Season the beef and onion mixture generously with salt and pepper to your taste. Stir well to combine.
5.  While the beef and onions are cooking, slice the bread into desired portions.
6.  Serve the hot beef and onion skillet mixture immediately, with slices of fresh bread and dill pickles on the side.

---

# Hard Test Results

Hard test cases included cluttered scenes, such as refrigerators or freezers, where the intended recipe was unclear.

| Test Case | Accuracy | Hallucination Rate | Observations |
|---------|----------|-------------------|-------------|
| Hard 1 | 0.62 | 0.41 | Frozen meats, waffles, and vegetables detected in freezer image |
| Hard 2 | 0.58 | 0.47 | Pantry items including milk, pasta, and sauces detected |
| Hard 3 | 0.55 | 0.52 | Refrigerator image eggs, milk, and bread |
| Hard 4 | 0.49 | 0.60 | Grocery shelf with many packaged foods caused extra detections |
| Hard 5 | 0.53 | 0.48 | Mixed fridge drawer with fruits, vegetables, and containers |

### Observations

- The system detects many ingredients in cluttered scenes.
- Recipe inference becomes more difficult when a **clear dish is not obvious**.
- Accuracy metrics are harder to compute due to **undefined expected ingredients**.

---

# Edge Case Tests

Edge case tests verify that the system properly handles invalid inputs.

| Test Case | Accuracy | Hallucination Rate | Observations |
|---------|----------|-------------------|-------------|
| Dog | 1.00| 0 | Throws an error message |
|Empty Counter | 1.00 | 0 | Gives an error message |
| Food in Containers | 0.55 | 0.52 | The recipe did not sound too good, just combines all ingredients |
| Lime | 1.00 | 0 | single lime says to cut it and use. Need to implement at least 2 or more ingredients  |
| Ready to Eat | 1.00 | 0 | can identify cooked food |

<img width="600" height="600" alt="image" src="https://github.com/user-attachments/assets/23e458c7-ec37-4884-a59c-f1309e525a5b" />

**Chicken Caesar Naan Flatbread**

A quick and easy flatbread topped with a creamy Caesar salad featuring cooked chicken, crisp romaine, and crunchy croutons.

**Ingredients Used:**
*   Multiple pieces Naan
*   1 piece Cooked Chicken
*   Large portion Romaine Lettuce
*   2 packets Caesar Dressing
*   Large portion Croutons

**Steps to Prepare:**
1.  Preheat your oven to 350°F (175°C) or heat a skillet over medium heat. Warm the naan pieces for 2-3 minutes until soft and slightly golden.
2.  While the naan warms, shred or dice the cooked chicken into bite-sized pieces.
3.  Wash and roughly chop the Romaine Lettuce.
4.  In a bowl, combine the chopped Romaine Lettuce, shredded chicken, and croutons. Pour in the 2 packets of Caesar Dressing and toss gently to coat all ingredients evenly. Season with salt and pepper to taste.
5.  Lay the warmed naan pieces on plates. Top each piece of naan generously with the prepared Chicken Caesar salad mixture. Serve immediately.

---

# Overall Performance Summary

| Metric | Result |
|------|------|
| Average Ingredient Extraction Accuracy | High on easy images |
| Retrieval Accuracy | Moderate for complex scenes |
| Hallucination Rate | Increases with cluttered images |
| Refusal Accuracy | Correct for non-food images |

---

# Key Findings

1. The system performs best when images clearly display ingredients.
2. Cluttered scenes increase hallucinated ingredient detection.
3. Packaged foods are more difficult to classify accurately.
4. The system correctly handles edge cases by refusing non-food images.

---

# Limitations

- Some images could not be processed due to missing files.
- API quota limits interrupted several test runs.
- Ingredient hallucinations occur frequently in complex scenes.

---

# Future Improvements

- Improve ingredient filtering to reduce hallucinations.
- Improve the database search to hit on the reference recipes more often
- Add bounding box detection to isolate ingredients.
- Improve recipe retrieval for large ingredient sets.
- Implement retry logic to handle API rate limits.

---


