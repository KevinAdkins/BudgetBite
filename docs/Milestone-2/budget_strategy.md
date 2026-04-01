# Budget Strategy

## Budget Tiers
- chosen budget tiers
- threshold values
## Pricing source: Kroger API
  - The Kroger API is called and passed the list generated from image extraction
  - It takes the average of the price points for items it can find
  - Retunts the price and what it was unable to find.
## What happens when pricing data is missing
  - The data is not included in the total. 
  - All the pricing data that is found it included
    
## Regeneration Strategy
  - If the pricing budget is not meet the recipe will be regenerated with additional context passed to better fit the budget the user wants
