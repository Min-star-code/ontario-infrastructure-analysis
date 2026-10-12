-- Q1. Projects and reported budget by category.
-- budget is NULL when the source publishes no figure, so SUM skips those rows
-- and budget_coverage_pct shows how much of each category the total represents.
SELECT category,
       COUNT(*)                                         AS projects,
       COUNT(budget)                                    AS projects_with_budget,
       ROUND(100.0 * COUNT(budget) / COUNT(*), 1)       AS budget_coverage_pct,
       ROUND(SUM(budget) / 1e9, 2)                      AS reported_budget_billion
FROM projects
GROUP BY category
ORDER BY reported_budget_billion DESC;

-- Q2. Projects and reported budget by region.
SELECT region,
       COUNT(*)                                         AS projects,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM projects), 1) AS pct_of_projects,
       ROUND(SUM(budget) / 1e9, 2)                      AS reported_budget_billion,
       ROUND(100.0 * SUM(budget) / (SELECT SUM(budget) FROM projects), 1) AS pct_of_budget
FROM projects
GROUP BY region
ORDER BY projects DESC;

-- Q3. Project status by category.
SELECT category,
       SUM(status = 'Complete')            AS complete,
       SUM(status = 'Under construction')  AS under_construction,
       SUM(status = 'Planning')            AS planning,
       SUM(status = 'Not reported')        AS not_reported,
       ROUND(100.0 * SUM(status = 'Complete') / COUNT(*), 1) AS pct_complete
FROM projects
GROUP BY category
ORDER BY pct_complete DESC;

-- Q4. How concentrated is the reported budget? Share held by the 10 largest projects.
SELECT COUNT(*)                         AS top_projects,
       ROUND(SUM(budget) / 1e9, 2)      AS top_budget_billion,
       ROUND(100.0 * SUM(budget) / (SELECT SUM(budget) FROM projects), 1) AS pct_of_reported_budget
FROM (SELECT budget FROM projects WHERE budget IS NOT NULL ORDER BY budget DESC LIMIT 10);

-- Q5. Funding partners: how many levels of funding does each project list?
SELECT funding_partners,
       COUNT(*)                         AS projects,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM projects), 1) AS pct_of_projects,
       SUM(federal_funding)             AS with_federal,
       SUM(municipal_funding)           AS with_municipal
FROM projects
GROUP BY funding_partners
ORDER BY funding_partners;

-- Q6. Open projects (planning or under construction) by target completion year.
SELECT completion_year,
       COUNT(*)                         AS open_projects,
       ROUND(SUM(budget) / 1e9, 2)      AS reported_budget_billion
FROM projects
WHERE status IN ('Planning', 'Under construction') AND completion_year IS NOT NULL
GROUP BY completion_year
ORDER BY completion_year;
