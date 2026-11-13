# Deployment notes

We deploy on Tuesdays. The build runs the full test suite first. A failed test
stops the release. The on-call engineer checks the dashboard after deploy. If
errors rise, revert the release. Then write a short note in the incident log.
