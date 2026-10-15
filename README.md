# Progress %

An Android tracker with daily personal-best comparisons, Google Fit imports, income and wealth planning, and lifetime projections.

## Android app — 1.4.1 preview

Download the APK from the [latest tested Android release](https://github.com/Eagle00009/progress-percent/releases/tag/android-preview-19). These features apply to Android; the website section below describes the older separate web version.

**If Android says “package conflicts with an existing package”: use [Progress-Percent-New.apk](https://github.com/Eagle00009/progress-percent/releases/download/android-preview-19/Progress-Percent-New.apk).** It installs as **Progress % New**, package com.jeevesh.progress.migration, beside the old Progress % app. Keep the old app installed. Export its JSON backup from Profile, then open Progress % New → Profile → Restore backup. Confirm your entries before removing anything. Reconnect Health Connect and enable auto sync in the new app; phone permissions do not transfer through a data backup. The normal APK remains for installations already using the current signing key.

**Back up before updating.** The signing-key cache from previews 6–8 expired before build 9. Builds 9 onward use a new signing certificate. Android cannot install them over an app signed with the old key. Export your JSON backup from the installed app first, keep it safe, then reinstall only if Android requires it, and restore the backup. Uninstalling without a backup removes your data. The current signing key now has an AES-256 encrypted repository backup, protected by the GitHub Actions SIGNING_BACKUP_PASSWORD secret. Builds restore that backup and refuse to generate replacement keys. Keep both the encrypted file and the secret. Updates use the same certificate as build 11.

### Added in 1.4

- **Backup reminders:** the dashboard shows the last successful export and reminds you after seven days. The timestamp is recorded only after the file provider finishes saving. Exported files remain under your control.
- **Fair daily comparisons:** choose Workday or Rest day in Journal. New days default from the weekday, then you can override them. Best-day comparisons require the same day type and matching scoring rules. Today remains labelled “Today so far” until finished. Legacy day types use the weekday default.
- **Scoring modes:** Profile → Goal scoring supports Reach target, Stay below target limit, and Stay within range. Reach uses actual/target capped at 100%; limit gives 100% at/below the target and target/actual above it; range gives 100% inside the entered bounds and proportionally less outside. Missing values stay missing. Rules are saved with each date; changes apply to new dates, including newly imported days. Existing entries retain their rules. Range bounds use the displayed raw units, including seconds for time.
- **One-minute check-in:** Show missing fields, Show all fields, and Copy yesterday’s routine. Copy fills only blank work, friends, learning, personal-care and miscellaneous fields, checks the 24-hour budget and leaves the result as a draft for review. Synced measurements are filled by the existing import flow.
- **Per-measurement sync status:** Updated, Waiting for shared data, Permission needed or Read failed, with the available read timestamp. Waiting does not mean a zero reading. Legacy imports without status metadata can only show their saved availability.
- **Actual net worth:** Income & wealth → Actual net worth records monthly cash, investments and debts in paise. Net worth is cash + investments − debts, with a history table and percentage of your goal. These actual balances are separate from the future projection.
- **Required-investment calculator:** Income & wealth → What needs to change? calculates total monthly investment needed under the saved return/contribution-growth assumptions. Adjust the age when contributions stop and inflation; optionally use the latest actual balances as today's starting point or treat the target as today's purchasing power. Results include projected purchasing power and affordability after expenses and cash savings. Debt interest and repayments are not modelled. An old actual snapshot should be updated before using it as today's balance.
- **Daily calendar:** Overview → Daily calendar. Tap a date for its best-day comparison; unfinished and missing entries are marked. Future days are disabled.
- **Custom dashboard:** Overview → Customize dashboard. Reorder or hide scores, goals, finance, sync, imported health and backup cards. Navigation stays accessible. Preferences survive app restarts and backups.

- Android 8+ for manual tracking; Google Fit import requires supported Health Connect (normally Android 9+). Automatic import additionally requires background-read support and permission.
- Offline bundled app and private phone storage. No health or financial data is sent to GitHub or a server. No direct Noise-app connection: Google Fit must share data with Health Connect.
- **Daily comparison against your best previous completed day**, replacing the weekly Android dashboard. The selected day's recorded goal IDs are compared with completed previous days containing all those goals. Scores average goal percentages capped at 100%; missing data is not zero. Ties select the most recent day. Differences are percentage points. Income is separate from the activity score.
- Tap goal/score cards and imported health readings for sources, values and calculations. Legacy entries without recorded provenance are labelled honestly. Imported readings remain distinct from manual overrides.
- **Automatic sync around 5 PM and 11:55 PM**, in phone local time. Enable once on the dashboard and grant background/data permissions. Android can delay runs during idle or battery restrictions; force-stopping the app prevents jobs until reopened. Each run checks today and yesterday for late-arriving data. Snapshots are stored privately, then merged automatically when you open the dashboard. Manual overrides, including explicitly cleared fields, are protected. Last successful check and problems are shown.
- Single-day and up-to-31-day historical imports remain in Journal. Older data requires past-data permission where supported. Only data actually shared by Google Fit can be read. Repeated imports do not duplicate dates. New historical records remain unfinished until reviewed.
- Steps, distance, sleep/stages, heart rate, resting heart rate, calories, workouts, weight, height and oxygen saturation are supported where shared. Do not add active and total calories together. Workouts are not automatically added to the daily time budget. These are measurements, not diagnoses.
- **Working years are independent of lifespan.** Default: work starts at age 18 and lasts 50 years; both are editable under Income & wealth. Time outside the working period becomes unallocated. Lifetime projections use the saved lifespan and recent finished logs.
- **Monthly income**: actual take-home income and a target, stored to the paisa. Shows target percentage and change from the immediately previous month. Missing or zero prior income does not produce a misleading percentage.
- **Wealth goal**: target amount in crore and target age, current savings/investments, monthly income/expenses/contributions, and separate income/contribution growth assumptions. Shows projected total, percentage, surplus/shortfall and a higher-investment scenario. Against ₹50 crore, ₹30 crore means 60% and ₹20 crore behind; ₹79 crore means 158% and ₹29 crore ahead. These are test examples, not predictions about your finances.
- Projection uses month-end contributions, the monthly equivalent of annual investment return, annual contribution increases and 0% cash interest. Contributions stop after your working period; balances continue growing. Growth/return assumptions default to 0%. Results are nominal rupees; inflation, taxes and fees are not separately modelled. Use a net return assumption. Plans exceeding income after expenses are flagged. Results are estimates, not guarantees or investment recommendations.
- Colored cards, larger touch targets, navigation icons, quick time buttons, optional exact seconds, entry sections and light/dark appearance. Family time remains removed; older family entries migrate into miscellaneous time.
- JSON backup/restore includes finance and source information. Native printing and back navigation remain supported.

Source templates are in android/prepare.py. GitHub Actions builds and tests the APK in an Android emulator, covering journal validation, persistence, imports, manual protection, daily comparison, income, wealth arithmetic and schedule boundaries. Passing emulator checks do not verify your phone's background timing or whether Google Fit shares every Noise-watch measurement.

## Website version

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
