#!/bin/bash

###############################################################################
# BudgetBite Complete Demo Script
# 
# This script demonstrates the full workflow:
# 1. Extract ingredients from fridge image using Gemini AI
# 2. Query backend database for matching recipes
# 3. Generate creative recipe suggestions  
# 4. Validate the generated recipe
#
# Prerequisites:
# - Backend Flask server running on localhost:5000
# - Python virtual environment activated
# - GEMINI_API_KEY in .env file
###############################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
IMAGE_PATH="${1:-Nichi-Fridge.jpg}"
INGREDIENTS_OUTPUT="ingredients.json"
MATCHED_RECIPES="matched_recipes.json"
GENERATED_RECIPE="generated_recipe.txt"

echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════════════"
echo "          🍽️  BUDGETBITE COMPLETE WORKFLOW DEMO  🍽️"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if image exists
if [ ! -f "$IMAGE_PATH" ]; then
    echo -e "${RED}❌ Error: Image file not found: $IMAGE_PATH${NC}"
    echo -e "${YELLOW}Usage: ./demo.sh <image_path>${NC}"
    echo -e "${YELLOW}Example: ./demo.sh Nichi-Fridge.jpg${NC}"
    exit 1
fi

echo -e "${BLUE}📸 Using image: $IMAGE_PATH${NC}\n"

# Check if backend is running
echo -e "${YELLOW}🔍 Checking if backend server is running...${NC}"
if ! curl -s http://127.0.0.1:5000/ > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend server is not running!${NC}"
    echo -e "${YELLOW}Please start it in another terminal:${NC}"
    echo -e "${CYAN}   cd backend && python app.py${NC}\n"
    exit 1
fi
echo -e "${GREEN}✅ Backend server is running${NC}\n"

# Step 1: Extract ingredients from image
echo -e "${MAGENTA}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Extract Ingredients from Image"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

python src/ingredient_extractor.py "$IMAGE_PATH" "$INGREDIENTS_OUTPUT"
STEP1_EXIT=$?

if [ $STEP1_EXIT -ne 0 ] || [ ! -f "$INGREDIENTS_OUTPUT" ]; then
    echo -e "${RED}❌ Step 1 failed: Ingredient extraction failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Step 1 complete: Ingredients saved to $INGREDIENTS_OUTPUT${NC}\n"
sleep 2

# Step 2: Query backend and match recipes
echo -e "${MAGENTA}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Query Backend Database & Match Recipes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

python src/retrieval.py "$INGREDIENTS_OUTPUT" "$MATCHED_RECIPES"
STEP2_EXIT=$?

if [ $STEP2_EXIT -ne 0 ] || [ ! -f "$MATCHED_RECIPES" ]; then
    echo -e "${RED}❌ Step 2 failed: Recipe matching failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Step 2 complete: Matched recipes saved to $MATCHED_RECIPES${NC}\n"
sleep 2

# Step 3: Generate creative recipe
echo -e "${MAGENTA}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Generate Creative Recipe"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

python src/recipe_generator.py "$MATCHED_RECIPES" "$GENERATED_RECIPE"
STEP3_EXIT=$?

if [ $STEP3_EXIT -ne 0 ] || [ ! -f "$GENERATED_RECIPE" ]; then
    echo -e "${RED}❌ Step 3 failed: Recipe generation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Step 3 complete: Recipe saved to $GENERATED_RECIPE${NC}\n"
sleep 2

# Step 4: Validate generated recipe
echo -e "${MAGENTA}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Validate Generated Recipe"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

python src/validator.py "$IMAGE_PATH" "$GENERATED_RECIPE"
STEP4_EXIT=$?

if [ $STEP4_EXIT -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Step 4 completed with warnings${NC}\n"
else
    echo -e "${GREEN}✅ Step 4 complete: Recipe validated${NC}\n"
fi

# Summary
echo -e "${CYAN}"
echo "═══════════════════════════════════════════════════════════════════"
echo "                    ✨ DEMO COMPLETE ✨"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${GREEN}Generated Files:${NC}"
echo -e "  📄 Ingredients: ${CYAN}$INGREDIENTS_OUTPUT${NC}"
echo -e "  📄 Matched Recipes: ${CYAN}$MATCHED_RECIPES${NC}"
echo -e "  📄 Generated Recipe: ${CYAN}$GENERATED_RECIPE${NC}"
echo ""

echo -e "${YELLOW}To view the generated recipe:${NC}"
echo -e "${CYAN}  cat $GENERATED_RECIPE${NC}"
echo ""

echo -e "${YELLOW}To see matched recipes:${NC}"
echo -e "${CYAN}  cat $MATCHED_RECIPES | python -m json.tool${NC}"
echo ""
