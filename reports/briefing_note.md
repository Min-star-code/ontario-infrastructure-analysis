# Briefing Note: Where Ontario's published infrastructure budget is concentrated

**Prepared by:** Mincheng Li | **Data as of:** 12 June 2026

## Issue

The province publishes a list of key infrastructure projects under Ontario Builds. This note summarizes what the list shows about where projects and reported budgets are concentrated, and how far the published data can support comparisons.

## Background

The public file lists 5,935 projects across seven categories, with status, target completion date, location, funding partners, and an estimated total budget. The file was cleaned without dropping any rows, and every figure below was checked against an independent SQL total.

## Key findings

1. **Budget reporting is incomplete.** 3,930 projects publish a budget, totalling $163.8 billion. The other 2,005 (34%) record a budget of zero, meaning no figure is published.
2. **Transit dominates the reported budget.** Transit is 10% of projects but 72% of the reported budget ($117.8 billion). Health care follows at $24.0 billion.
3. **A few projects account for most of the total.** The ten largest projects hold 71.5% of the reported budget. The Ontario Line ($29.5 billion) and GO Expansion ($27.5 billion) together hold 35%.
4. **Most of the reported budget is in the Central region.** Central has 30% of projects and 88% of the reported budget, because the largest transit and hospital projects are there.
5. **Some published dates are out of date.** 93 projects still marked Planning or Under construction have a target completion year before 2026.

## Considerations

- Totals are lower bounds. Budget coverage ranges from 98% of child care projects to 20% of recreation projects, so category comparisons are uneven.
- Budgets are life-of-project estimates, not spending to date.
- Region figures are not adjusted for population, so they do not show investment per resident.

## Suggested next steps

- Add population by region to compare reported investment per resident.
- Follow up on the 93 open projects with past target dates to confirm whether the status or the date is stale.
