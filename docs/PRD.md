# Product Requirements Document (PRD)

## Overview
**Budget Bite** uses the **Gemini API (Google)** for image-based ingredient extraction and a **SQLite database** (seeded by TheMealDB API) to provide **verified, grounded recipe recommendations** for budget-conscious users.

The system avoids custom computer vision models and instead relies on **Gemini’s multimodal capabilities** to extract ingredients directly from user-submitted images.

This document outlines:
1. Problem + target users  
2. Goals / success metrics  
3. MVP user stories  
4. MVP scope vs. non-goals  
5. Acceptance criteria  
6. Assumptions + constraints  

---

## Section 1: Problem + Target Users

### The Problem
Rising grocery costs and limited access to affordable, healthy food options lead many students to make poor dietary choices. A lack of quick, budget-friendly meal ideas contributes to long-term health risks such as type 2 diabetes and hypertension.

### Target Users
- **Primary:** College students (TAMUSA) with limited budgets and kitchen tools  
- **Secondary:** Busy parents needing quick, affordable, and verified meals  

---

## Section 2: Goals / Success Metrics

Success is defined by the system’s ability to **convert image or text input into grounded, verified recipes**.

| Metric | Target | Definition |
| :--- | :--- | :--- |
| **Grounding Accuracy** | 98% | % of recipes returned that exist in SQLite / TheMealDB |
| **Gemini Extraction Accuracy** | 90% | % of images where Gemini correctly identifies usable ingredients |
| **Local Cache Latency** | < 2 seconds | Time to retrieve recipes from SQLite |
| **API Fetch Latency** | < 6 seconds | Time to fetch and cache new recipes |

---

## Section 3: MVP User Stories

1. **Core User Story**  
   As a student, I want to take a picture of my ingredients or type what I have, so that I can quickly get a cheap and healthy meal idea.

2. **Low-Ingredient Scenario**  
   As a student with limited ingredients (e.g., milk, cheese, eggs), I want the app to suggest meals I can make and recommend affordable additions if needed.

3. **Family Use Case**  
   As a parent, I want affordable and nutritious meal suggestions, so that I can save time and feed my family well.

---

## Section 4: MVP Scope vs. Non-Goals

### Must-Have Features
- **Gemini API Image Processing**
  - Accept image input
  - Extract ingredient list using structured prompting
- **Ingredient Normalization Layer**
  - Clean and standardize Gemini output (e.g., “tomatoes” → “tomato”)
- **SQLite Database**
  - Store cached recipes from TheMealDB
- **Recipe Matching Engine**
  - Match extracted ingredients to grounded recipes
- **React Frontend**
  - Image upload + results display

### Nice-to-Have Features
- Nutritional overlays  
- Calorie estimates  

### Explicit Non-Goals
- Full budget tracking system  
- Strict calorie tracking  
- Custom-trained computer vision models  
- Demographic-specific tailoring  

---

## Section 5: Acceptance Criteria

- User can upload or take a photo of ingredients  
- System sends image to Gemini API for **ingredient extraction**  
- Gemini returns a **structured ingredient list (JSON)**  
- App normalizes ingredients and queries SQLite  
- System returns at least one grounded recipe within **10 seconds**  

### Edge Cases
- If no food is detected:
  - Return a clear error message  
- If ingredients are insufficient:
  - Suggest low-cost additional ingredients  

---

## Section 6: Assumptions + Constraints

### Technical Assumptions
- No CV segmentation model is used  
- Ingredient extraction is fully handled by Gemini using prompt engineering  

**Example Prompt:**
```json
{
  "instruction": "Extract all visible food ingredients from this image.",
  "format": {
    "ingredients": ["string"]
  }
}
