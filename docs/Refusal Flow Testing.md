# Sprint 2 P2: Refusal Flow Testing Documentation

## Overview
This document demonstrates the BudgetBite pipeline's input validation and refusal behavior. The system correctly rejects invalid requests with appropriate HTTP 400 status codes and error messages.

## Test Results

### Test Environment
- **Date:** April 14, 2026
- **Tester:** Eric Gerner
- **Validation Function:** `validate_pipeline_input()` from `backend/routes/pipeline_routes.py`

### Test Cases

#### 1. Empty Request Body
**Input:**
```json
{}
```
**Expected:** Rejection with "Request body cannot be empty"
**Result:** ✅ PASS
**Error Message:** "Request body cannot be empty"

#### 2. Missing Ingredients Field
**Input:**
```json
{
  "budget": 10.0
}
```
**Expected:** Rejection with "ingredients field is required"
**Result:** ✅ PASS
**Error Message:** "ingredients field is required and must not be empty"

#### 3. Empty Ingredients List
**Input:**
```json
{
  "ingredients": []
}
```
**Expected:** Rejection with "ingredients list cannot be empty"
**Result:** ✅ PASS
**Error Message:** "ingredients field is required and must not be empty"

#### 4. Non-List Ingredients
**Input:**
```json
{
  "ingredients": "chicken, tomato"
}
```
**Expected:** Rejection with "ingredients must be a list"
**Result:** ✅ PASS
**Error Message:** "ingredients must be a list"

#### 5. Invalid Ingredients (Empty Strings Only)
**Input:**
```json
{
  "ingredients": ["", "  ", ""]
}
```
**Expected:** Rejection with "no valid ingredients"
**Result:** ✅ PASS
**Error Message:** "No valid ingredients provided after sanitization"

#### 6. Invalid Budget Type
**Input:**
```json
{
  "ingredients": ["chicken"],
  "budget": "ten dollars"
}
```
**Expected:** Rejection with "budget must be a valid number"
**Result:** ✅ PASS
**Error Message:** "budget must be a valid number"

#### 7. Negative Budget
**Input:**
```json
{
  "ingredients": ["chicken"],
  "budget": -5.0
}
```
**Expected:** Rejection with "budget must be non-negative"
**Result:** ✅ PASS
**Error Message:** "budget must be non-negative"

## API Response Format

All rejection responses follow this format:
```json
{
  "success": false,
  "error": "specific error message",
  "pipeline_status": "input_rejected",
  "timestamp": "2026-04-14T..."
}
```

## Test Script

The validation was tested using `test_refusal_flow.py` which directly tests the `validate_pipeline_input()` function.

**Command:**
```bash
python test_refusal_flow.py
```

**Output:**
```
🧪 Testing Pipeline Input Validation (Refusal Flow)
============================================================
1. Empty request body ✅ PASS
2. Missing ingredients field ✅ PASS
3. Empty ingredients list ✅ PASS
4. Ingredients not a list ✅ PASS
5. Ingredients with only empty strings ✅ PASS
6. Invalid budget type ✅ PASS
7. Negative budget ✅ PASS
============================================================
Results: 7/7 tests passed
🎉 All refusal flow tests passed!
```

## Conclusion

The BudgetBite pipeline correctly implements input validation and refusal behavior. All invalid inputs are properly rejected with clear, specific error messages. The system prevents incoherent or malicious requests from proceeding through the pipeline.

**Status:** ✅ COMPLETE - Refusal flow testing and documentation completed.