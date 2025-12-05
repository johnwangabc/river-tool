# Repository Guidelines

## Project Structure & Module Organization
- Entry point `App.js` wires the bottom-tab navigator for Activity, RiverPatrol, Comprehensive, and Settings flows.
- Feature screens live in `src/screens/*Screen.js`; keep per-screen logic self-contained and lean on shared helpers.
- Reusable UI parts belong in `src/components/`; utilities (API calls, formatting, data transforms) go in `src/utils/`.
- Static assets (fonts, icons) sit in `assets/`. Project-wide config lives in `app.json`, `eas.json`, `metro.config.js`, and `babel.config.js`.

## Build, Test, and Development Commands
- Install dependencies with `npm install`.
- Launch Expo dev server: `npm start` (or `npm run start`); scan the QR to load on device/emulator.
- Platform targets: `npm run android`, `npm run ios`, `npm run web`. Prefer device/emulator testing for native features.
- If bundler cache causes odd errors, restart Expo and clear caches (`npm start -- --clear`).

## Coding Style & Naming Conventions
- Use functional React components, hooks, and React Navigation patterns already present.
- Two-space indentation, single quotes, and trailing semicolons to match existing files.
- Components and screen files in PascalCase (e.g., `UserList.js`); helper functions in camelCase.
- Keep API endpoints, token handling, and formatting helpers in `src/utils/` instead of in screen components.
- Prefer `react-native-paper` components for consistent styling and theming.

## Testing Guidelines
- No automated test suite is configured; run the app via `npm start` and exercise critical paths:
  - Activity stats date entry, fetch, and Excel export
  - River patrol/assessment queries by user IDs and date range
  - Comprehensive stats export
  - Settings: token save/load and org ID persistence
- When fixing bugs, outline manual steps taken (device, platform, data ranges) in your PR.

## Commit & Pull Request Guidelines
- Write imperative, focused commit messages (e.g., `Add river patrol export validation`).
- Small, scoped PRs are preferred. Include:
  - Summary of changes and rationale
  - Test plan (commands run, manual steps taken)
  - Screenshots or screen recordings for UI changes
  - Linked issue IDs when applicable
- Avoid committing tokens, sample exports, or device-specific artifacts.

## Security & Configuration Tips
- Never hard-code or commit the Authorization token; keep secrets only in local settings storage.
- Remove personal data from sample exports before sharing.
- Keep dependencies current with Expo/React Native release notes; verify native builds after upgrades.
