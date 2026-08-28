# TZ — fayna_instructor_school

> Канонічна специфікація модуля за [[REPO_STANDARD]].
> Версія модуля: **17.0.1.3.0** | License: LGPL-3 | depends: `base`, `website`, `mail`.
> Структура: 6 областей spec-driven + Success Criteria + Open Questions.
> ⚠️ **DEPRECATED (2026-06-07):** функціонал переноситься у `fayna_camp_portal`. Код — reference.

---

## 1. Objective

**Що:** Odoo 17 Community модуль школи інструкторів (вожатих) для CampScout — каталог курсів зі state-machine, запис учасників, публічна сторінка з формою подачі заявки.

**Для кого:** CampScout / Fayna Camp — рекрутація та навчання кадри таборів (kurs wychowawcy, kurs kierownika, first aid, specialty).

**Можливості (реалізовано в коді):**
- `instructor.course` — каталог курсів зі state-machine (`draft → open → in_progress → completed / cancelled`), типи курсу, дати, локація, ціна (Monetary), `max_participants`, computed-лічильники (`enrollment_count`, `enrolled_count`, `available_spots`)
- `instructor.enrollment` — запис учасника (`pending → confirmed → completed / cancelled`), `payment_status` (unpaid/paid), `certificate_number`, capacity guard + unique `(course_id, partner_id)`
- Публічна сторінка `/instructor-school` — список опублікованих open/in_progress курсів
- Форма заявки `/instructor-school/apply/<id>` (`auth="public"`) — find-or-create partner + enrollment, guard на дублікат/місткість
- Self-enroll `/instructor-school/enroll/<id>` (`auth="user"`) для залогінених
- ACL: manager (full CRUD) + internal user + portal; record rule — portal бачить лише свої enrollment
- i18n: uk_UA + pl_PL

**Контекст:** Phase 8 master TZ `CAMPSCOUT_MASTER_TZ.md §16` (Strangler Fig). Модуль інертний за feature flag `fayna_instructor_school.active` (default `False`).

**Технології:** [[library/tools/python]] · Odoo 17 Community · [[library/tools/docker]] · QWeb/website · pytest · ruff.

---

## 2. Commands

```bash
# Тести (pytest)
cd fayna_instructor_school
python -m pytest tests/ -v

# Coverage (ціль ≥70%)
python -m pytest tests/ --cov=. --cov-report=term-missing

# Lint + format (pre-commit: ruff + ruff-format + OCA + bandit + gitleaks)
pre-commit run --all-files
ruff check .
ruff format --check .

# Деплой #4ZONES (Mac → GitHub → staging → prod) — модуль DEPRECATED, для reference
git push origin main
ssh prod 'cd /opt/campscout/custom-addons/fayna_instructor_school && git pull && sudo chmod -R o+rX .'
ssh prod 'docker exec campscout_web odoo -u fayna_instructor_school --stop-after-init -d campscout && docker restart campscout_web'
```

---

## 3. Project Structure

```
fayna_instructor_school/
  __manifest__.py        # v17.0.1.3.0, depends: base, website, mail
  models/
    course.py            # instructor.course — каталог + state-machine + computed counts
    enrollment.py        # instructor.enrollment — запис + payment_status + capacity guard
  controllers/
    website.py           # /instructor-school, /apply/<id> (public), /enroll/<id> (user)
  views/
    instructor_course_views.xml / course_views.xml          # tree/form/search course
    instructor_enrollment_views.xml / enrollment_views.xml  # tree/form/search enrollment
    menu.xml / school_menu.xml                               # меню
    website/instructor_school_page.xml                       # QWeb сторінка + форма заявки
  data/ir_config_parameter.xml   # feature flag fayna_instructor_school.active (False)
  security/
    ir.model.access.csv  # manager / user / portal ACL
    ir_rules.xml         # portal бачить лише свої enrollment
  tests/                 # test_scaffold, test_course_enrollment, test_instructor_school
  i18n/                  # uk_UA.po, pl_PL.po
  docs/                  # TZ.md (цей), PLAN.md
```

---

## 4. Code Style

```python
# State-machine action — guard на дозволений стан, помилка через _()
def action_open_enrollment(self):
    for course in self:
        if course.state != "draft":
            raise UserError(_("Only draft courses can be opened for enrollment."))
        course.state = "open"

# Capacity guard у create — @api.model_create_multi
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    for record in records:
        course = record.course_id
        if course.max_participants and course.available_spots < 0:
            raise UserError(_("Course '%s' is fully booked.") % course.name)
    return records
```

- **Odoo 17 ідіоми:** `@api.depends` для computed, `@api.constrains` для валідації, `@api.model_create_multi` для `create`
- **State-machine:** кожен перехід — лише з дозволеного стану, інакше `UserError`; cascade у `course.action_cancel/complete`
- **i18n:** усі user-facing рядки через `_()`; синхронізувати `uk_UA.po` + `pl_PL.po`
- **Публічні роути:** `.sudo()` для запису від анонімного відвідувача + guard на дублікат/`available_spots`
- **Чистота** (golden rules): без закоментованого коду, дебаг-принтів, сміття
- **ruff:** line-length 100, double quotes, select `E,F,W,I,N,UP,B,S,C4,SIM` (див. `pyproject.toml`)
- **Semantic Versioning** у `__manifest__.py`: одна сесія = один bump

---

## 5. Testing

- **Фреймворк:** pytest (`minversion 8.0`), тести в `tests/`
- **Локація і покриття:**
  - `test_scaffold.py` — install + feature flag + deps sanity
  - `test_course_enrollment.py` — state-machine (course + enrollment), capacity guard, unique `(course_id, partner_id)`, cascade cancel/complete
  - `test_instructor_school.py` — моделі + публічні роути (`/apply`, `/enroll`)
- **Coverage:** ціль ≥70% критичних шляхів (`fail_under = 70` у `pyproject.toml`)
- **Regression:** кожен bug-fix → тест, що відтворює баг
- **Gate:** pre-commit (ruff/format/bandit/gitleaks) зелений перед кожним комітом

---

## 6. Boundaries

**Always:**
- Деплой лише #4ZONES: Mac → GitHub → staging → prod ([[meta/golden-rules-developer]] #3)
- `chmod -R o+rX` після git pull на сервері ()
- ≥1 тест на кожен fix; CHANGELOG-запис; Semantic Version bump; синхронізація i18n
- Feature flag за замовчуванням `False` (Strangler Fig — модуль інертний)

**Ask first:**
- Реактивація DEPRECATED-модуля (за замовчуванням функціонал у `fayna_camp_portal`)
- Зміна `depends` у `__manifest__.py`
- Зміна моделі/полів, що тягне міграцію даних
- Зняття/зміна feature flag (`fayna_instructor_school.active`)

**Never:**
- Редагувати файли напряму на сервері (nano/vim/scp/docker exec edit) — #4ZONES
- Секрети (.env, токени, ключі) у код / UI / лог / git
- Дублювати функціонал, що мігрує у `fayna_camp_portal` (узгодити архітектуру)
- Запис від анонімного роуту без `.sudo()` + guard на дублікат/місткість

---

## Success Criteria

- [x] Курс проходить state-machine `draft → open → in_progress → completed`, cancel каскадить на enrollments
- [x] Запис учасника: capacity guard + unique `(course_id, partner_id)` блокують overbooking/дублі
- [x] Публічна заявка `/apply/<id>` створює partner + enrollment, не дублює
- [x] Portal user бачить лише свої enrollment (record rule)
- [x] Тести зелені, coverage ≥70%, pre-commit зелений
- [ ] Міграція функціоналу у `fayna_camp_portal` завершена (далі модуль архівується)

---

## Open Questions

- Точна межа міграції у `fayna_camp_portal`: що переносити, що архівувати (див. ).
- Чи лишати публічну форму заявки тут, чи повністю в єдиному CampScout-модулі.

---

## Зв'язки

- Стандарт: [[REPO_STANDARD]] · Master: [[CAMPSCOUT_MASTER_TZ]] §16 Phase 8
- План реалізації: **docs/PLAN.md** · Історія: **CHANGELOG.md**
- Інструменти: [[library/tools/python]] · [[library/tools/docker]] · [[library/tools/git]]
- Memory:
- Repo: `VladSh77/fayna-instructor-school`
