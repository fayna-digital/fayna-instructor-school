# Odoo 17 Fayna Instructor School

![Odoo Version](https://img.shields.io/badge/Odoo-17.0%20Community-purple)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green.svg)
![Status](https://img.shields.io/badge/Status-Live-brightgreen)

**Opracowane przez [Fayna Digital](https://www.fayna.agency) dla CampScout i szerszego pionu Camp Fayna.**
**Autor: Volodymyr Shevchenko**

---

Publiczna strona docelowa + formularz zgłoszeniowy dla instruktorów obozowych
(wychowawców), z katalogiem kursów i zapisami uczestników.

Faza 8 planu głównego: `CAMPSCOUT_MASTER_TZ.md §16`.

---

## Możliwości

| Model | Opis |
|-------|------|
| `fayna.instructor.course` | Katalog kursów z maszyną stanów: `draft` → `open` → `in_progress` → `completed` / `cancelled` |
| `fayna.instructor.enrollment` | Zapis per-uczestnik ze statusem płatności |

- **Publiczna strona `/instructor-school`** — lista otwartych kursów
- **Trasa zapisu portalu `/instructor-school/enroll/<id>`** (`auth=user`)
- **Pełny ACL menedżera obozu**; portal: odczyt kursów + tworzenie własnego zapisu
- **Reguła rekordu:** użytkownicy portalu widzą tylko własne zapisy
- **i18n:** `uk_UA` + `pl_PL`

## Architektura

```
fayna_instructor_school/
├── __manifest__.py                  # 17.0.1.3.0, depends: base, website, mail
├── __init__.py
├── data/ir_config_parameter.xml     # feature flag
├── models/
│   ├── course.py                    # fayna.instructor.course (maszyna stanów)
│   └── enrollment.py                # fayna.instructor.enrollment (status płatności)
├── controllers/
│   └── website.py                   # /instructor-school + /instructor-school/enroll/<id>
├── security/
│   ├── ir.model.access.csv
│   └── ir_rules.xml                 # portal: tylko własne zapisy
├── views/
│   ├── instructor_course_views.xml
│   ├── instructor_enrollment_views.xml
│   ├── course_views.xml
│   ├── enrollment_views.xml
│   ├── menu.xml
│   ├── school_menu.xml
│   └── website/instructor_school_page.xml
├── tests/                           # test_instructor_school, test_course_enrollment, test_instructor, test_scaffold
├── docs/TZ.md                       # specyfikacja per-moduł
├── .github/workflows/ci.yml         # gate-2 CI
├── .pre-commit-config.yaml          # gate-1 pre-commit
├── pyproject.toml
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## Instalacja

```bash
cd /opt/campscout/custom-addons
sudo -u \#1000 git clone https://github.com/VladSh77/fayna-instructor-school.git fayna_instructor_school
docker exec campscout_web odoo -c /etc/odoo/odoo.conf -d campscout \
    -i fayna_instructor_school --stop-after-init --no-http
docker restart campscout_web
```

## Dokumentacja

- [docs/TZ.md](docs/TZ.md) — specyfikacja (6 obszarów spec-driven)
- [docs/PLAN.md](docs/PLAN.md) — dependency graph + fazy + checkpointy
- [CHANGELOG.md](CHANGELOG.md) — historia wersji

---

## Licencja

LGPL-3 — patrz [LICENSE](LICENSE).

---

*Opracowane przez [Fayna Digital](https://www.fayna.agency) · Volodymyr Shevchenko*
