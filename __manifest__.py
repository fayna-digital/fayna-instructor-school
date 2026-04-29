{
    "name": "Fayna Instructor School",
    "version": "17.0.1.3.0",
    "category": "Tools/Camp Management",
    "summary": "Instructor school — courses, enrollment, public website page",
    "description": """
Fayna Instructor School
=======================

Phase 8 of the Fayna Camp vertical stack (Strangler Fig decomposition
per CAMPSCOUT_MASTER_TZ.md §16).

Provides:
- fayna.instructor.course — course catalog with state machine (draft → open →
  in_progress → completed / cancelled)
- fayna.instructor.enrollment — per-participant enrollment with payment status
- Public website page /instructor-school listing open courses
- Portal enroll route /instructor-school/enroll/<id> (auth=user)
- Camp-manager full ACL; portal read-courses + create-own-enrollment
- Record rule: portal users see only their own enrollments
- i18n: uk_UA + pl_PL

Author: Fayna Digital — Volodymyr Shevchenko
License: LGPL-3
TZ: fayna-digital-docs/contributing/CAMPSCOUT_MASTER_TZ.md §16 Phase 8
    """,
    "author": "Fayna Digital — Volodymyr Shevchenko",
    "website": "https://fayna.agency",
    "license": "LGPL-3",
    "depends": ["base", "website", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "data/ir_config_parameter.xml",
        "views/instructor_course_views.xml",
        "views/instructor_enrollment_views.xml",
        "views/course_views.xml",
        "views/enrollment_views.xml",
        "views/menu.xml",
        "views/school_menu.xml",
        "views/website/instructor_school_page.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
