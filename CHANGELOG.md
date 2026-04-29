# Changelog

All notable changes to `fayna_instructor_school` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: Odoo `17.0.MAJOR.MINOR.PATCH`.

---

## [17.0.1.2.0] — 2026-04-29

### Added
- `instructor.enrollment.payment_status` field: `unpaid` / `paid` selection with tracking — enables kitchen/admin to filter paid participants for certificate issuance
- `instructor.enrollment.action_confirm()` / `action_complete()` / `action_cancel()` state transitions with `UserError` guards
- `_check_course_not_cancelled` `@api.constrains` — blocks enrollment creation in cancelled courses
- `create()` capacity guard: raises `UserError` when `available_spots < 0` after insert
- `_sql_constraints`: unique `(course_id, partner_id)` on `instructor.enrollment` — prevents double enrollment
- `instructor.course.action_cancel()`: cascades cancellation to all non-completed enrollments
- `instructor.course.action_complete()`: auto-completes all confirmed enrollments

### Fixed
- `_compute_enrollment_count` now uses `len()` instead of a domain search — consistent with `enrollment_ids` One2many already loaded in memory

### Security
- `security/ir_rules.xml`: portal users see only their own enrollments (was unrestricted read for portal group)

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
