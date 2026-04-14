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
# Usage:
#   ./demo.sh [image_path] [--price-tier cheap|medium|expensive]

IMAGE_PATH="Nichi-Fridge.jpg"
PRICING_TIER="${PRICE_TIER:-medium}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --price-tier)
            if [[ -z "$2" || "$2" == --* ]]; then
                echo -e "${RED}❌ Error: --price-tier requires a value: cheap, medium, or expensive${NC}"
                exit 1
            fi
            PRICING_TIER="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./demo.sh [image_path] [--price-tier cheap|medium|expensive]"
            echo "Example: ./demo.sh Nichi-Fridge.jpg --price-tier cheap"
            exit 0
            ;;
        *)
            if [[ "$1" == --* ]]; then
                echo -e "${RED}❌ Error: Unknown option: $1${NC}"
                echo -e "${YELLOW}Usage: ./demo.sh [image_path] [--price-tier cheap|medium|expensive]${NC}"
                exit 1
            fi
            IMAGE_PATH="$1"
            shift
            ;;
    esac
done

PRICING_TIER=$(echo "$PRICING_TIER" | tr '[:upper:]' '[:lower:]')
case "$PRICING_TIER" in
    cheap)
        PRICING_STRATEGY="cheapest"
        ;;
    medium)
        PRICING_STRATEGY="average_top3"
        ;;
    expensive)
        PRICING_STRATEGY="first"
        ;;
    *)
        echo -e "${RED}❌ Error: Invalid price tier '$PRICING_TIER'. Use cheap, medium, or expensive.${NC}"
        exit 1
        ;;
esac

INGREDIENTS_OUTPUT="ingredients.json"
MATCHED_RECIPES="matched_recipes.json"
GENERATED_RECIPE="generated_recipe.txt"
PRICING_API_URL="${PRICING_API_URL:-http://127.0.0.1:5001/api/pricing/ingredients}"
PRICING_ZIP_CODE="${KROGER_ZIP_CODE:-78201}"

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
echo -e "${BLUE}💵 Price tier: $PRICING_TIER (strategy: $PRICING_STRATEGY)${NC}\n"

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

# Check if any ingredients were actually detected
INGREDIENT_COUNT=$(python -c "import json; data=json.load(open('$INGREDIENTS_OUTPUT')); print(len(data.get('ingredients', [])))" 2>/dev/null || echo "0")
if [ "$INGREDIENT_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ Step 1 failed: No ingredients detected in image${NC}"
    echo -e "${YELLOW}Please use an image containing food items${NC}"
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

python src/recipe_generator.py "$MATCHED_RECIPES" "$GENERATED_RECIPE" --ingredients-file "$INGREDIENTS_OUTPUT"
STEP3_EXIT=$?

if [ $STEP3_EXIT -ne 0 ] || [ ! -f "$GENERATED_RECIPE" ]; then
    echo -e "${RED}❌ Step 3 failed: Recipe generation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Step 3 complete: Recipe saved to $GENERATED_RECIPE${NC}\n"
sleep 2

# Step 4: Estimate Kroger pricing
echo -e "${MAGENTA}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Estimate Kroger Pricing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

echo -e "${BLUE}🧾 Ingredient names sent to Kroger will be parsed from: $GENERATED_RECIPE${NC}\n"

PRICING_OUTPUT=$(python src/pricing.py \
    --recipe-file "$GENERATED_RECIPE" \
    --zip-code "$PRICING_ZIP_CODE" \
    --strategy "$PRICING_STRATEGY" \
    --api-url "$PRICING_API_URL" 2>&1)
STEP4_EXIT=$?

echo "$PRICING_OUTPUT"

TIER_SUMMARY=$(echo "$PRICING_OUTPUT" | grep '^Tier: ' | tail -n 1)
if [[ "$TIER_SUMMARY" =~ ^Tier:\ ([^[:space:]]+)\ \|\ Selected\ Tier:\ ([^[:space:]]+)\ \|\ Result:\ ([^[:space:]]+)$ ]]; then
    GENERATED_TIER="${BASH_REMATCH[1]}"
    SELECTED_TIER="${BASH_REMATCH[2]}"
    TIER_RESULT="${BASH_REMATCH[3]}"
    echo -e "${BLUE}🧪 Tier check: selected=${SELECTED_TIER}, generated=${GENERATED_TIER}, result=${TIER_RESULT}${NC}"
fi

if [ $STEP4_EXIT -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Step 4 completed with warnings (pricing unavailable or partial)${NC}\n"
else
    echo -e "${GREEN}✅ Step 4 complete: Kroger pricing estimated${NC}\n"
fi
sleep 2

# Step 5: Validate generated recipe
echo -e "${MAGENTA}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Validate Generated Recipe"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

python src/validator.py "$IMAGE_PATH" "$GENERATED_RECIPE"
STEP5_EXIT=$?

if [ $STEP5_EXIT -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Step 5 completed with warnings${NC}\n"
else
    echo -e "${GREEN}✅ Step 5 complete: Recipe validated${NC}\n"
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
