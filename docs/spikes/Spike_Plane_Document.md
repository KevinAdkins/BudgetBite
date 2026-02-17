# Spike Plan

1. **Riskiest assumption** (1 sentence)
	The Computer Vision model (Model A) can accurately identify raw ingredients from a single, low-quality mobile photo well enough for the LLM (Model B) to generate a viable, safe recipe.

2. **Spike goal** (what "success" means)
	- Validate that the Flask backend can pass an image to the CV model and receive a clean text list of ingredients.

	- Confirm the LLM can transform that specific list into a recipe that respects "Budget-Friendly" constraints.

	- Ensure the SQLite caching layer correctly stores and retrieves previously generated recipes to save on API costs.

3. **Inputs -> Outputs** (what data goes in, what comes out)
	- User Photo $\rightarrow$ Ingredient List (via CV Model)

	- Ingredient List + Budget Constraint $\rightarrow$ Formatted Recipe (via LLM)

	- Recipe Metadata $\rightarrow$ SQLite Database (Persistent Storage)

4. **Demo plan (2-3 min)** (what you will show live)
	- **Live Capture:** Upload a photo of 3-4 random fridge items.

	- **Backend Trace:** Show the terminal logs of the CV model identifying the items and passing them to the LLM.

	- **The Result:** Display the generated "Budget Bite" recipe and verify the data now exists in the SQLite DB without the raw image.

5. **Owner(s) + tasks** (who is responsible for what)
	- **Jorge Munoz:** Team Leader & AI Developer
	- **Kevin Adkins:** Frontend Developer
	- **Alvaro Gonzalez:** Database Developer
	- **David Abundis:** Wireframe Developer
	- **Eric Gerner:** Backend Developer

6. **Exit criteria** (clear pass/fail checks)
	- **PASS** The system correctly identifies at least 75% of items in a test photo and generates a recipe in under 10 seconds.

	- **PASS** The raw image is successfully deleted from the server after processing (Privacy Goal).

	- **FAIL** The CV model consistently confuses common items (e.g., calling an orange a tomato) or the LLM "hallucinates" ingredients not in the photo.

7. **If it fails...** (Plan B / fallback approach)
	- Plan B (Manual Input): If CV is too inaccurate, pivot the UI to a "Smart Search" where users quickly tap/tag ingredients instead of relying solely on a photo.
