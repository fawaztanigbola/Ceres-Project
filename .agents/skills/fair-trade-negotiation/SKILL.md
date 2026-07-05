---
name: fair-trade-negotiation
description: >
  Enforces fair trade pricing rules when evaluating buyer bids against
  the current market price. Applies the 15% floor rule to protect farmers
  from below-market offers and rejects all bids that fall beneath the
  acceptable floor price.
---

# Skill: Fair Trade Negotiation

When evaluating buyer bids against the current market price, you MUST strictly enforce the 15% rule.

## Rule: The 15% Floor Price

Calculate the acceptable floor using the following formula:

```
floor_price = market_price * 0.85
```

## Decision Logic

- **If ANY buyer bid is at or above `floor_price`:** Proceed with the transaction using only the qualifying bids.
- **If ALL buyer bids are below `floor_price`:** You MUST reject all offers and output exactly:

  > "No fair trade bids available."

  Do not execute the transaction. Do not book freight. Do not proceed to the Security Agent review step.

## Example

| Input | Value |
|---|---|
| `market_price` | $5/kg |
| `floor_price` | $5 × 0.85 = **$4.25/kg** |
| Bid A | $4.00/kg → ❌ Below floor |
| Bid B | $3.80/kg → ❌ Below floor |
| Bid C | $3.50/kg → ❌ Below floor |

**Result:** All bids are below `$4.25/kg`. Output `"No fair trade bids available."` and halt.

## Integration Notes

- This rule is applied by the **Logistics_Agent** after calling `get_market_price` and `get_vetted_buyers`.
- The floor check MUST happen before calling `book_freight`.
- The **Security_Agent**'s `Rule 2` (price > 0) is a complementary guard, not a replacement for this rule.
