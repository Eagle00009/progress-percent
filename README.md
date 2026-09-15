# Progress %

A browser-based dashboard for tracking goals through small, measurable actions.

## Features

- Track goals across sleep, learning, fitness, emotions, work, money, relationships, habits, and custom activities.
- Log progress with quick-add buttons or an amount and optional note.
- View daily, weekly, monthly, and yearly progress.
- Add reflections, switch themes, and export a JSON backup.

## Run locally

Download `index.html` and open it in a modern browser. No installation or build step is required. HTML, CSS, and JavaScript are included in the same file.

## Data and current limitations

The first visit includes sample activity. Goals, logs, notes, and preferences are saved in that browser's local storage; there is no account or device sync. Clearing browser storage removes that data. Use **Export** to download a backup; importing backups is not currently implemented.

Week, month, and year views use rolling 7-, 30-, and 365-day targets. The historical trend and day-over-day score need a calculation correction before being used for reliable comparisons.

## Project files

- `index.html` — complete application
- `README.md` — project guide

Created by [Jeevesh Singh](https://github.com/Eagle00009).
