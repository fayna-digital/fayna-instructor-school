{
    "name": "Fayna Instructor School",
    "version": "17.0.0.1.0",
    "category": "Tools/Camp Management",
    "summary": "Public landing page + application form for camp instructors (vozhaty)",
    "description": """
Fayna Instructor School
=======================

Phase 8 of the Fayna Camp vertical stack (Strangler Fig decomposition
per CAMPSCOUT_MASTER_TZ.md §16).

Dedicated /instructor-school page + application form + lead pipeline for new instructors.

Current status: scaffold — installable but inert. Feature flag
`fayna_instructor_school.active` defaults to `False`; implementation lands in incremental
milestones defined in docs/TZ.md.

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
        "data/ir_config_parameter.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
