# Structured Recipe Knowledge Base

You must implement:

A structured recipe database (JSON, SQL, etc.)
Fields including:
- Recipe name
- Ingredient list
- Steps
- Optional nutrition/cost info

Create:

Document:

## The Meal DB
- Link: https://www.themealdb.com/api.php
- Total Number of Recipes: 598
- Total Number of Ingredients: 877
- Categories: 14
- Different Countries: 37

Source of recipes - https://www.themealdb.com/api.php

Number of recipes indexed - 
Preprocessing steps 
1. Query using the main ingredient in the SQLite Database
2. Filter the number of recipes to only the ones that use 90% percet of the ingredients
3. Take into account Spices like salt, pepper, etc. Assume the user has basic seasoning
4. Provide the LLM with filtered recipes
       
Hard-coded recipes in prompts are not acceptable.
