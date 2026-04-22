# BudgetBite
Senior Project <br>
An app that can take a picture of what you have and come up with a meal idea.<br>
The goal is to keep it budget-friendly while recommending you healthy meals to make.

# Team Members and Our Roles
**Jorge Munoz:** Team Leader & AI Developer<br>
**Kevin Adkins:** Frontend Developer<br>
**Alvaro Gonzalez:** Database Developer<br>
**David Abundis:** Wireframe Developer & Frontend Developer<br>
**Eric Gerner:** Backend Developer<br>

# How to Run

## Prerequisites
Before running BudgetBite, make sure you have:
- Python 3.8 or higher installed
- pip (Python package manager)
- Git (for cloning the repository)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/KevinAdkins/BudgetBite.git
cd BudgetBite
```

### 2. Backend Setup

#### Install Python Dependencies
Navigate to the backend directory and install required packages:
```bash
cd backend
pip install -r requirements.txt
```

#### Initialize the Database
The database will be automatically created when you first run the app. To manually seed the database with sample data, run:
```bash
python (or py) seed.py
```
Seed data is stored in [backend/data/meals_seed.csv](backend/data/meals_seed.csv) so teammates can update rows without hand-writing SQL inserts.
The CSV includes pricing fields (`estimated_price`, `currency`, `price_source`, `price_last_updated`) so you can share stable seeded prices without calling external APIs.
To export the latest DB meals back into CSV for teammates, run:
```bash
python (or py) backend/seed.py --export-csv
```

#### Start the Backend Server
```bash
python (or py) app.py
```

The backend API will start running at `http://localhost:5001`

You should see a message indicating the Flask server is running.

### Frontend Setup

````bash
cd frontend
```bash

### Configure Your Network IP

Find your local IP address:
```bash
ipconfig on Windows
Look for IPv4 Address for your IP
````

In `frontend/app/(tabs)/camera.tsx`, replace the backend URL with your IP:

```tsx
const res = await fetch("http://YOUR_LOCAL_IP:5001/api/analyze", {
```
Download the requirments.txt in the frontend folder
#### Start the Frontend

```bash
npx expo start --web
```

If your phone can't connect run:

```bash
npx expo start --web --host tunnel
```

### 3. Test the API
You can test if the backend is working by visiting these endpoints in your browser:
- `http://localhost:5001/` - API information
- `http://localhost:5001/api/meals` - View all meals (pls let me know if it works)

### 4. Gemini API Setup
Create a .env file
```bash
GEMINI_API_KEY=your-api-key
```

### 5. Kroger API Setup
In the same .env file from the Genimi Setup
```bash
KROGER_CLIENT_ID=app-name
KROGER_CLIENT_SECRET=your-api-key
KROGER_BASE_URL=https://api-ce.kroger.com
KROGER_SCOPE=product-scope
KROGER_ZIP_CODE=zip-code
```

## API Endpoints
The backend provides the following endpoints:

### Meals
- **GET** `/api/meals` - Get all meals
- **GET** `/api/meals/<name>` - Get specific meal by name
- **GET** `/api/meals/search?name=<name>` - Search for meal (checks database and external API)

(In-progress haven't tested yet skeleton code)
- **POST** `/api/meals` - Add new meal
- **PUT** `/api/meals/<name>` - Update meal
- **PATCH** `/api/meals/<name>/instructions` - Update instructions only
- **DELETE** `/api/meals/<name>` - Delete meal

### Analysis
- **POST** `/api/analyze` - Analyze fridge image

### Pricing
- **POST** `/api/pricing/ingredients` - Estimate ingredient pricing via blueprint route
- **POST** `/api/kroger/pricing/ingredients` - Estimate ingredient pricing via app route
- **GET** `/api/kroger/pricing/strategies` - List allowed Kroger pricing strategies

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can change it by modifying `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')  # Change to any available port
```

### Database Issues
Let me know if any arise but in the meantime. Delete the `backend/data/meals.db` file and restart the server. The database will be recreated automatically.

### Module Not Found Errors
Make sure you're in the `backend` directory and have activated your virtual environment (if using one). Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Gemini API Quota Exceeded
**Error**: `429 RESOURCE_EXHAUSTED - Quota exceeded`

The free tier of Gemini API has limits:
- **gemini-3-flash**: 20 requests per day
- **gemini-2.5-flash**: 1500 requests per day (higher limit!)

**Solutions:**

1. **Switch to gemini-2.5-flash** (recommended):
   ```bash
   # Edit src/ingredient_extractor.py and src/recipe_generator.py
   # Change model='gemini-3-flash-preview' to model='gemini-2.5-flash'
   ```

2. **Wait and retry** (free tier resets daily):
   - Wait 1 minute and run: `./demo.sh Nichi-Fridge.jpg`

3. **Run partial demo** (skip AI generation):
   ```bash
   # Steps 1-2 work without hitting limits
   python src/ingredient_extractor.py Nichi-Fridge.jpg ingredients.json
   python src/retrieval.py ingredients.json matched_recipes.json
   
   # View the matched recipes
   cat matched_recipes.json | python -m json.tool
   ```

4. **Use existing output files**:
   If Steps 1-2 completed, you already have:
   - `ingredients.json` - extracted ingredients
   - `matched_recipes.json` - recipes from database that match your ingredients
   
   View the top matches:
   ```bash
   python -c "import json; data=json.load(open('matched_recipes.json')); print('\n'.join([f'{i+1}. {r[\"name\"]} - {r[\"match_score\"][\"percentage\"]}% match' for i,r in enumerate(data[:5])]))"
   ```

## 🎬 Complete Workflow Demo

BudgetBite includes a complete end-to-end demo that showcases the full pipeline from fridge image to validated recipe.

### Demo Workflow

```
📸 Fridge Image → 🔍 Extract Ingredients → 🗄️ Match Recipes → 🤖 Generate Recipe → ✅ Validate
```

### Prerequisites for Demo

1. **Backend server must be running** (see Backend Setup above)
2. **Install additional dependencies**:
   ```bash
   pip install google-genai python-dotenv requests pydantic
   ```
3. **Create `.env` file** with your Gemini API key:
   ```bash
   echo "GEMINI_API_KEY=your_key_here" > .env
   ```

### Running the Complete Demo

Run the automated demo script:
```bash
chmod +x demo.sh
./demo.sh Nichi-Fridge.jpg
```

Replace `Nichi-Fridge.jpg` with the path to your fridge image.

### Demo Steps Explained

#### Step 1: Ingredient Extraction
Analyzes your fridge image and extracts all visible food items:
```bash
python src/ingredient_extractor.py <image> ingredients.json
```
**Output:** `ingredients.json` - Structured list of detected ingredients

#### Step 2: Recipe Retrieval
Queries the backend database and matches ingredients to available recipes:
```bash
python src/retrieval.py ingredients.json matched_recipes.json
```
**Output:** `matched_recipes.json` - Ranked list of matching recipes with scores

#### Step 3: Recipe Generation
Uses AI to generate a creative recipe based on your ingredients:
```bash
python src/recipe_generator.py matched_recipes.json generated_recipe.txt
```
**Output:** `generated_recipe.txt` - Complete recipe with instructions

#### Step 4: Recipe Validation
Validates that the generated recipe only uses detected ingredients:
```bash
python src/validator.py ingredients.json generated_recipe.txt
```
**Output:** Console report showing validation results

### Manual Testing

If you prefer to run steps individually:

```bash
# 1. Extract ingredients
python src/ingredient_extractor.py Nichi-Fridge.jpg ingredients.json

# 2. Match recipes from database
python src/retrieval.py ingredients.json matched_recipes.json

# 3. Generate creative recipe
python src/recipe_generator.py matched_recipes.json generated_recipe.txt

# 4. Validate recipe
python src/validator.py ingredients.json generated_recipe.txt
```

### View Results

```bash
# View extracted ingredients
cat ingredients.json | python -m json.tool

# View matched recipes
cat matched_recipes.json | python -m json.tool

# View generated recipe
cat generated_recipe.txt
```

### Demo Tips for Presentation

1. Start with backend server running in one terminal
2. Show the fridge image to your audience
3. Run `./demo.sh` with the image path
4. Watch as each step completes with colored output
5. Review the generated files and validation results
6. Show how recipes from database influenced the AI generation

### Testing Backend API Directly

```bash
# Get all meals
curl http://localhost:5001/api/meals

# Search for specific ingredient
curl "http://localhost:5001/api/meals/search?name=chicken"

# Get specific recipe
curl http://localhost:5001/api/meals/spaghetti
```

## 📝 Text Input Mode

In addition to analyzing fridge images, BudgetBite supports direct ingredient input via text. This allows users to manually enter ingredients they have on hand for recipe recommendations and budget analysis.

### Using the Text Input API

**Endpoint:** `POST /api/analyze-text`

**Request:**
```json
{
  "ingredients": ["chicken breast", "rice", "garlic", "onion"]
}
```

**Response:**
The API returns validated recipes, budget tier, and regeneration results following the same pipeline as the image analysis path (validation → pricing → budget classification → regeneration if needed).

### Text Input vs. Image Analysis

- **Image Analysis:** Extracts ingredients from photos, useful for showing what's in your fridge
- **Text Input:** Manual ingredient entry, useful for planning meals with specific items

Both paths flow through the same validation, pricing, and budget regeneration logic to ensure consistency.

### Demo Architecture

```
┌─────────────┐
│ Fridge      │
│ Image       │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│ Gemini AI   │─────▶│ ingredients  │
│ Extractor   │      │   .json      │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Backend API │
                     │ (localhost:  │
                     │   5001)      │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   matched    │
                     │  _recipes    │
                     └──────┬───────┘
                            │
                            ▼
┌─────────────┐      ┌──────────────┐
│ Gemini AI   │─────▶│  generated   │
│ Generator   │      │  _recipe.txt │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Validation  │
                     │   Report     │
                     └──────────────┘
```

# Latest Docs
[Our Documents & Slides](https://github.com/KevinAdkins/BudgetBite/tree/main/docs)
