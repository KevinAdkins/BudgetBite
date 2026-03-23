TEST_CASES = [
    # ── Easy ──────────────────────────────────────────────────────
    {
        "id": "easy_01",
        "difficulty": "easy",
        "image": "foodimages/easy/burger.jpg",
        "expected_ingredients": ["ground beef", "bun", "lettuce", "tomato", "cheese", "onion", "pickle", "cheese", "mayonnaise"],
        "expected_dish_type": "burger",
        "should_detect_food": True,
    },
    {
        "id": "easy_02",
        "difficulty": "easy",
        "image": "foodimages/easy/fish-tacos.jpg",
        "expected_ingredients": ["fish", "tortilla", "salsa", "cheese"],
        "expected_dish_type": "tacos",
        "should_detect_food": True,
    },
    {
        "id": "easy_03",
        "difficulty": "easy",
        "image": "foodimages/easy/fried-chicken-sandwich.jpg",
        "expected_ingredients": ["chicken", "bun", "lettuce", "tomato", "cheese"],
        "expected_dish_type": "sandwich",
        "should_detect_food": True,
    },
    {
        "id": "easy_04",
        "difficulty": "easy",
        "image": "foodimages/easy/spaghetti.jpg",
        "expected_ingredients": ["pasta", "tomato", "ground beef", "garlic"],
        "expected_dish_type": "pasta",
        "should_detect_food": True,
    },
    {
        "id": "easy_05",
        "difficulty": "easy",
        "image": "foodimages/easy/steak.jpg",
        "expected_ingredients": ["steak", "salt", "pepper", "garlic", "butter"],
        "expected_dish_type": "steak",
        "should_detect_food": True,
    },

    # ── Medium ─────────────────────────────────────────────────────
    {
        "id": "medium_01",
        "difficulty": "medium",
        "image": "foodimages/medium/bad-quality.jpg",
        "expected_ingredients": ["chicken", "banana", "milk", "potato", "onions", "ground beef"],
        "expected_dish_type": None,
        "should_detect_food": True,
    },
    {
        "id": "medium_02",
        "difficulty": "medium",
        "image": "foodimages/medium/GeneralTsosChicken.jpg",
        "expected_ingredients": ["eggs", "chicken", "soy sauce", "mushroom", "chicken stock", "cornstarch", "garlic", "ginger", "sugar", "vinegar", "green onion"],
        "expected_dish_type": None,
        "should_detect_food": True,
    },
    {
        "id": "medium_03",
        "difficulty": "medium",
        "image": "foodImages/medium/grocery-haul.webp",
        "expected_ingredients": ["eggs", "tofu", "bananas", "mushroom", "apple", "carrots", "peppers", "jalapeno", "beans", "blueberries"],
        "expected_dish_type": None,
        "should_detect_food": True,
    },
     {
        "id": "medium_04",
        "difficulty": "medium",
        "image": "foodImages/medium/grocery-items.webp",
        "expected_ingredients": ["potatoes", "tomato", "cheese", "pineapple", "bacon", "cilantro", "radish", "garlic", "ginger", "tortilla", "onion"],
        "expected_dish_type": None,
        "should_detect_food": True,
    },
    {
        "id": "medium_05",
        "difficulty": "medium",
        "image": "foodImages/medium/junk-food.webp",
        "expected_ingredients": ["eggs", "grapes", "banana", "cans", "milk","pasta", "blueberries", "raspberries"],
        "expected_dish_type": None,
        "should_detect_food": True,
    },

    # ── Hard ───────────────────────────────────────────────────────
    {
        "id": "hard_01",
        "difficulty": "hard",
        "image": "foodImages/hard/freezer.jpg",
        "expected_ingredients": [],   # anything valid is acceptable
        "expected_dish_type": None,   # AI decides
        "should_detect_food": True,
    },
    {
        "id": "hard_01",
        "difficulty": "hard",
        "image": "foodimages/hard/fridge1.webp",
        "expected_ingredients": [],   # anything valid is acceptable
        "expected_dish_type": None,   # AI decides
        "should_detect_food": True,
    },
    {   
        "id": "hard_01",
        "difficulty": "hard",
        "image": "foodimages/hard/fridge2.jpg",
        "expected_ingredients": [],   # anything valid is acceptable
        "expected_dish_type": None,   # AI decides
        "should_detect_food": True,
    },
    {
        "id": "hard_01",
        "difficulty": "hard",
        "image": "foodimages/hard/fridge3.jpg",
        "expected_ingredients": [],   # anything valid is acceptable
        "expected_dish_type": None,   # AI decides
        "should_detect_food": True,
    },
    {
        "id": "hard_01",
        "difficulty": "hard",
        "image": "foodImages/hard/Nichi-Fridge.jpg",
        "expected_ingredients": [],   # anything valid is acceptable
        "expected_dish_type": None,   # AI decides
        "should_detect_food": True,
    },


    # ── Edge cases ─────────────────────────────────────────────────
    {
        "id": "edge_01",
        "difficulty": "edge",
        "image": "foodImages/edge/dogImage.jpeg",
        "expected_ingredients": [],
        "expected_dish_type": None,
        "should_detect_food": False,  # should raise ValueError
    },
    {
        "id": "edge_02",
        "difficulty": "edge",
        "image": "foodImages/edge/empty-counter.jpg",
        "expected_ingredients": [],
        "expected_dish_type": None,
        "should_detect_food": False,  # should raise ValueError
    },
    {
        "id": "edge_03",
        "difficulty": "edge",
        "image": "foodImages/edge/food-in-containers.jpg",
        "expected_ingredients": [],
        "expected_dish_type": None,
        "should_detect_food": True,  # should raise ValueError
    },
    {
        "id": "edge_04",
        "difficulty": "edge",
        "image": "foodImages/edge/lime.jpeg",
        "expected_ingredients": [],
        "expected_dish_type": None,
        "should_detect_food": True,  # should raise ValueError
    },
    {
        "id": "edge_05",
        "difficulty": "edge",
        "image": "foodImages/edge/ready-to-eat.webp",
        "expected_ingredients": ["chicken", "nann", "lettuce","croutons"],
        "expected_dish_type": None,
        "should_detect_food": True,  # should raise ValueError
    },
]