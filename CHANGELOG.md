# Changelog

All notable changes to `fayna_instructor_school` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: Odoo `17.0.MAJOR.MINOR.PATCH`.

---

## [17.0.1.1.0] — 2026-04-28

### Added

- `instructor.course` model — Szkoła Instruktorów course catalog with state machine (draft → active → archived), course_type selection (wychowawca/kierownik/first_aid/specialty), max_participants, website_published flag, smart enrollment count button.
- `instructor.enrollment` model — per-participant enrollment (enrolled/completed/dropped), certificate_number, completion_date, constraint blocking enrollment in archived courses.
- Views: tree + form + search for both models; statusbar in form headers.
- Menu: top-level "Instructor School" with Courses / Enrollments sub-items.
- ACL: manager (full CRUD) + user (read/write/create) for both models.
- Tests: 10 tests in `test_course_enrollment.py` covering all 5 required cases + edge cases.
- i18n: uk_UA.po + pl_PL.po updated with all new user-facing strings.

---

## [17.0.0.1.0] — 2026-04-24

### Added
- Initial scaffold (empty-but-installable).
- Feature flag `fayna_instructor_school.active` (default `False`) per master TZ §2 Strangler Fig.
- Canonical tooling (pre-commit, pyproject, GitHub Actions CI).
- Placeholder tests (install + flag + deps sanity).
- `docs/TZ.md` per-module TZ aligned with CAMPSCOUT_MASTER_TZ.md §16 Phase 8.

### Notes
- Module is **inert** until Phase 8 implementation lands.
