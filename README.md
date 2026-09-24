# Progress %

A personal progress dashboard with daily journaling, weekly comparisons, sleep and body measurements, and lifetime time projections.

## Start
Open the GitHub Pages app once deployment succeeds. Select **Explore demo** for illustrative data, or **Profile & goals** to enter your age and personal targets, then **Log your day**.

## Features
- Monday-based weekly dashboard and eight-week history, with previous/next week navigation.
- Comparable week-over-week changes calculated on matching weekdays and recorded goal IDs.
- Daily time budget: sleep, work, walking, family, friends, learning, personal care and miscellaneous activities.
- Total sleep plus deep, light and REM stages; unspecified sleep remains unclassified.
- Steps, walking distance, weight, height, wellbeing and health/reflection notes.
- Custom measurable goals, editable daily records, JSON backup/restore and printable dashboard.
- Whole-life and remaining-life time estimates from the last 28 calendar days of finished time logs.
- Responsive layout, light/dark appearance and an isolated, temporary demo.

## Percentages and units
A goal score is actual / recorded target × 100, capped at 100% for scoring. A daily score averages available goals equally; a period averages logged daily scores equally. Missing values are excluded, not treated as zero. Logging coverage is shown separately.

The headline week-over-week change uses only matching weekdays and goal IDs present in both weeks. Goal rows show available period averages and may have different coverage. Targets are snapshotted when a date is first saved. Changing targets affects new dates only. Custom goals also apply to new dates.

70% to 72% is **+2 percentage points**, equivalent to **+2.86% relative change**. A value of 7.2 out of 10 is 72%; 72 out of 10 is not a valid 0–10 rating.

Time is stored as whole seconds, weight as grams, height as millimetres, distance as metres, steps as whole counts. Inputs use HH:MM:SS, kg to three decimals and cm to one decimal. Precision does not imply measurement accuracy. Body percentages use the first recorded measurement as reference; wellbeing is a personal 0–10 rating converted to percent. These are not medical health scores.

## Lifetime assumptions
Only entries explicitly marked as finished time logs are included. Time categories cannot exceed 86,400 seconds/day. Sleep stages cannot exceed sleep and are never added again to the daily budget. Unallocated time is retained.

The average routine of finished days in the last 28 calendar days is applied to an editable lifespan (default 70). The conversion uses 365.2425 days/year. Eight hours every day is 33.33% of life, or 23.33 years / approximately 8,522.33 days across 70 years. Remaining-life estimates require current age. Whole-life figures are scenarios, not historical records or lifespan predictions. Age is manually maintained; no automatic wearable integration or medical diagnosis is provided.

## Data
This GitHub-hosted version retains browser-only storage. No account, backend, telemetry, or cross-device sync is included. Entries are not uploaded to GitHub. Clearing browser data can remove entries; export regular backups. Restore validates the backup and requests confirmation before replacing matching dates/profile/goals.

The original app is preserved as [legacy.html](legacy.html), including its original storage key. Its records remain separate and are not silently imported because the old app contains sample data and different goal semantics. Old data is accessible only from its original browser/origin. The new app uses `progressPercentLifeV2` and starts empty.

## Source and hosting
- `index.html`: dependency-free application.
- `legacy.html`: unchanged original tracker.
- `README.md`: usage and calculation rules.

GitHub Pages serves the repository root from `main`. No installation or build is needed. All source changes were authored through GitHub; no local project files were created.

## Validation
JavaScript syntax checked. Calculation assertions cover normalization, percentage-point changes, missing/zero values, seconds precision, week/year boundaries, excluded unfinished days, non-overlapping weekly ranges, 70-year projections, totals summing to 100%, and invalid inputs.
