# MVP Results

## Ingredient Extraction Accuracy
- **Accuracy:** 91%  
- Most ingredients were correctly identified and normalized (e.g., “2 eggs” → eggs, quantity: 2)  
- Minor issues with ambiguous ingredients (e.g., “mixed vegetables”, “seasoning”)
- Issues with images with containers of food


## Recipe Retrieval Relevance
- **Relevant Results Rate:** 87%  
- Majority of retrieved recipes matched the intended ingredients and category  
- Occasional mismatches when ingredients were too generic (e.g., “meat”)
- Limited by what recipes exist in the database


## Hallucination Rate
- **Hallucination Count:** 0 out of 20 tests  
- **Rate:** 0%  
- The validator fix now ignores measurement/descriptor words such as thinly, shredded, tbsp, and leaves, so they are no longer counted as hallucinations.


## Refusal Success Rate
- **Success Rate:** 100%  
- The system correctly refused to generate recipes when:
  - No valid ingredients were detected such as an animal
  - Input was nonsensical or empty such as only one ingredients 



## Budget Pass Rate
- **Pass Rate:** 85%  
- Post-fix reruns confirm the tier classifier is now correct on the expensive/medium boundary cases, but the overall budget pass rate remains 85% until the full 20-test suite is rerun with updated generation and pricing outputs.
- Failures still occurred when:
  - Ingredient pricing returned full-package costs (e.g., eggs, milk)
  - Higher-end proteins were selected (e.g., lamb, salmon)
  - Item not found in the Kroger database


## Regeneration Success Rate
- **Success Rate:** 90%  
- Regeneration improved results in most failed cases  
- Especially effective when:
  - Adjusting ingredient matches
  - Selecting alternative recipes within budget



## Known Failures
- Ingredient ambiguity (e.g., “spices”, “meat”) leads to poor matches  
- Pricing inaccuracies due to full package costs instead of portion usage  
- Limited recipe options when ingredient list is too small  
- Occasional mismatch between ingredient list and retrieved recipe  
- Seafood/meat items sometimes return inconsistent pricing based on weight  
