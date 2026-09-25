# Progress %

A personal progress dashboard with daily journaling, weekly comparisons, sleep and body measurements, and lifetime time projections.

## Android app
The installable Android preview is built and tested entirely on GitHub. Download the APK from [Android releases](https://github.com/Eagle00009/progress-percent/releases) after the **Build Android APK** workflow succeeds.

- Android 8.0+ (API 26), with an updated Android System WebView.
- Installs as **Progress %**, package `com.jeevesh.progress`.
- Dashboard and all app code are bundled in the APK. No website connection is required, and the manifest requests no Internet permission.
- Daily entries are stored atomically in a private app file. They remain after normal app restarts; uninstalling or clearing app data removes them.
- Android file picker handles JSON backup/export and restore. Use a website version 2 backup to transfer existing web entries. Automatic sync is not included.
- Native Android printing, system back handling and fixed bottom navigation.
- Sleep and activity values remain manual inputs; no wearable or sensor permissions are requested.

Open the downloaded `Progress-Percent-Android.apk` on your phone and follow Android's installation prompt. If Android asks, allow installation from the browser/file manager used to open this APK.

This is a **preview**, not a Google Play production release. Release-mode code is signed using a preview/debug key retained in the GitHub Actions cache. If that cache expires, a future preview may have a different signature; export your data before reinstalling. A dedicated private production signing key is needed before store distribution.

### Android source and checks
`android/prepare.py` holds the Gradle, manifest, Java activity, resources and instrumentation-test templates. It packages the existing dashboard with Android storage and backup integrations into a generated project in the GitHub runner's temporary directory. This avoids duplicating the web UI source.

`.github/workflows/android.yml` builds the APK, checks its signature and manifest, runs Android 15 emulator tests, and publishes the APK plus SHA-256 checksum only after successful checks. Tests cover offline initialization, percentage calculations, time/sleep validation, grams/mm precision, persistence after activity recreation, reports, profile persistence and demo isolation. Physical-phone and real document-provider backup/restore testing remain manual checks.

Build stack: Java 17, Gradle 8.13, Android Gradle Plugin 8.11.1, compile/target SDK 36, AndroidX WebKit 1.14.0. The local-asset origin follows [Android's WebViewAssetLoader guidance](https://developer.android.com/develop/ui/views/layout/webapps/load-local-content).

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
