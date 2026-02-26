# Milestone 1 Deliverables  
## Team: BudgetBite  
### Focus: Ingredient-Aware, Knowledge-Grounded Recipe Assistant  

---

## Context

The team demoed a CNN-based vision model for ingredient detection during the Spike.  
However:

- The CNN model is currently too inaccurate without substantial labeled training data  
- There is no knowledge base for recipes  
- There is no grounding layer for generated outputs  
- No evaluation framework exists for accuracy or reliability  

You have been directed to pivot toward:

- Using an LLM-assisted ingredient understanding approach  
- Grounding outputs in a structured recipe knowledge base  
- Ensuring generated recipes are verifiable and consistent with known ingredients  

Milestone 1 must demonstrate a reliable, grounded, and measurable system.

---

# Milestone 1 Objective

By Milestone 1, your team must demonstrate:

- A working ingredient understanding pipeline (vision optional, LLM acceptable)  
- A structured recipe knowledge base  
- Retrieval-based recipe generation  
- Explicit grounding to known ingredients and recipe data  
- Measurable evaluation of correctness  
- Clean GitHub structure and engineering artifacts  

---

# 1. Final PRD-Lite (Updated)

Your PRD must clearly define the product as:

> A grounded recipe recommendation system based on detected or provided ingredients.

## The PRD must include:

### A. Clear Product Definition
- User uploads image OR inputs ingredient list  
- System identifies ingredients  
- System retrieves compatible recipes  
- System generates grounded output  

### B. Grounding Requirement (Non-Negotiable)

- Recipes must be generated from a structured recipe database  
- Ingredients in output must exist in detected/provided list  
- No invented ingredients  
- If insufficient ingredients are available, system must refuse or request clarification  

### C. MVP Scope (April 5 Demo)

Must include:

- Ingredient input (image or text)  
- Ingredient normalization step  
- Recipe retrieval  
- Grounded generation  
- Refusal when insufficient data  

### D. Acceptance Criteria (Testable)

Examples:

- ≥ 80% ingredient detection accuracy (if vision used)  
- ≥ 85% recipe retrieval relevance  
- 0 invented ingredients in generated recipes  
- Refusal triggered when ingredient list incomplete  

---

# 2. Ingredient Understanding Layer

You must implement at least one reliable approach:

- LLM-based ingredient extraction from image captions or text  
- Pretrained food recognition API (if used, must evaluate accuracy)  
- Structured mapping to canonical ingredient list  

If CNN is retained:

- Must provide measurable evaluation  
- Must document dataset size and validation accuracy  

If performance remains low, pivot to LLM-based approach.

---

# 3. Structured Recipe Knowledge Base (Required)

You must implement:

- A structured recipe database (JSON, SQL, etc.)  
- Fields including:
  - Recipe name  
  - Ingredient list  
  - Steps  
  - Optional nutrition/cost info  

Create:

/docs/data_sources.md

Document:

- Source of recipes  
- Number of recipes indexed  
- Preprocessing steps  

Hard-coded recipes in prompts are not acceptable.

---

# 4. Grounded Generation Layer

The system must:

- Retrieve top-k recipes based on ingredient overlap  
- Pass only retrieved recipes into LLM context  
- Prevent inclusion of ingredients not in user list  

If the model proposes extra ingredients:

- Either block  
- Or clearly label as "optional" with justification  

---

# 5. Evaluation Starter Kit (Minimum 20 Test Cases)

Create:

/docs/evaluation_test_cases.md

Include:

- 20 ingredient input scenarios  
- Expected recipe(s)  
- Retrieved recipe(s)  
- Generated output  
- Verification result  

Required metrics:

- Ingredient extraction accuracy  
- Retrieval accuracy  
- Hallucination rate (invented ingredients)  
- Refusal accuracy  

---

# 6. Spike Recovery / Pivot Document

Create:

/docs/spike_results.md

Must include:

- CNN performance metrics  
- Identified limitations  
- Rationale for pivot  
- Updated architecture plan  
- Risk mitigation plan  

---

# 7. Architecture Diagram (1 page)

Create:

/docs/architecture.png

It must clearly show:

Image/Text Input  
→ Ingredient Extraction  
→ Ingredient Normalization  
→ Recipe Retrieval  
→ LLM Generation  
→ Validation Layer  
→ Output  

Clearly label deterministic components vs LLM components.

---

# 8. Required Technical Walkthrough Video (No UI Required)

Submit a short technical walkthrough video (5–8 minutes) showing:

- Ingredient extraction logic  
- Recipe database structure  
- Retrieval process  
- Context passed into LLM  
- Validation preventing invented ingredients  

UI is not required. Engineering transparency is required.

---

# 9. GitHub Repository Requirements

Your repository must include:

- /docs/PRD.md  
- /docs/data_sources.md  
- /docs/spike_results.md  
- /docs/evaluation_test_cases.md  
- /docs/architecture.png  
- /src/ingredient_extractor.py  
- /src/retrieval.py  
- /src/generator.py  
- /src/validator.py  

Additionally:

- Updated README with setup and run instructions  
- requirements.txt  
- .env.example  
- At least one meaningful commit per team member  
- Sprint 1 issue board with assigned owners  

---

# Required Live Demo for Milestone 1

You must demonstrate:

1. Ingredient input  
2. Detected/normalized ingredient list  
3. Retrieved recipes  
4. Generated recipe grounded to retrieved data  
5. Validation step preventing hallucinated ingredients  
6. A refusal case when insufficient ingredients  

If recipes are generated without grounding to a structured database, Milestone 1 is incomplete.

---

# Milestone 1 Standard

Your project must evolve from:

“We trained a CNN to guess ingredients.”

To:

“We engineered a grounded, ingredient-aware recipe system with structured retrieval and hallucination control.”

This is the expected senior-level standard.
