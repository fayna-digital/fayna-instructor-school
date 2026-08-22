# PLAN — fayna_instructor_school (план реалізації)

> Друга черга після [docs/TZ.md](TZ.md). Dependency graph + фази + checkpoints (skill `planning-and-task-breakdown`).
> Що ВЖЕ зроблено — у CHANGELOG.md (моделі course/enrollment, state-machine, ACL, публічна сторінка+форма — реалізовано).
> ⚠️ **DEPRECATED (2026-06-07):** модуль заморожений; пріоритет — міграція у `fayna_camp_portal`, не розвиток тут.

---

## Overview

Базовий функціонал (каталог курсів, запис учасників, state-machine, публічна сторінка + форма заявки, ACL, i18n) — **реалізований**. Модуль інертний за feature flag (`fayna_instructor_school.active` = `False`) і заморожений після архітектурного pivot. Цей план фіксує залишковий борг і шлях міграції.

---

## Dependency graph

```
[Feature flag / scaffold] ✅ ── фундамент
        │
        ├── [instructor.course модель + state-machine] ✅
        │           │
        │           └── [instructor.enrollment + capacity/unique guard] ✅ ── залежить від course
        │                       │
        │                       └── [ACL + record rule portal] ✅ ── залежить від моделей
        │
        └── [Публічна сторінка /instructor-school + форма /apply] ✅ ── залежить від course/enrollment
                    │
                    └── [Self-enroll /enroll auth=user] ✅

[Міграція у fayna_camp_portal] ── залежить від УСЬОГО вище ── фінальна фаза (відкрита)
```

---

## Task List

### Phase 0: Scaffold ✅ (2026-04-24)

- [x] Empty-but-installable модуль, feature flag `False`, CI зелений, базові тести.

### Phase 1: Моделі + state-machine ✅ (2026-04-28..29)

- [x] `instructor.course` — каталог, типи, дати, ціна, computed counts, state-machine
- [x] `instructor.enrollment` — запис, payment_status, capacity guard, unique `(course_id, partner_id)`, cascade
- [x] ACL (manager/user/portal) + record rule (portal бачить лише свої)
- [x] Тести `test_course_enrollment.py` (state-machine + edge cases)

### Checkpoint: Phase 1
Моделі повні, тести зелені, coverage ≥70%, ACL коректний.

### Phase 2: Публічний фронт ✅

- [x] Сторінка `/instructor-school` — список опублікованих курсів
- [x] Форма заявки `/apply/<id>` (public) — find-or-create partner + enrollment, guard на дублікат/місткість
- [x] Self-enroll `/enroll/<id>` (auth=user)
- [x] Тести роутів `test_instructor_school.py`

### Checkpoint: Phase 2
Публічний потік працює: відвідувач бачить курси → подає заявку → enrollment створено без дублів/overbooking.

### Phase 3: Міграція у fayna_camp_portal (ВІДКРИТО — пріоритет)

- [ ] **Task: Інвентаризація функціоналу для переносу**
  - Acceptance: список моделей/роутів/views, що йдуть у `fayna_camp_portal`, vs архівуються
  - Verify: узгоджено з master TZ + pivot-нотаткою
  - Files: документ міграції, `docs/TZ.md` Open Questions
- [ ] **Task: Перенос моделей/роутів у fayna_camp_portal**
  - Acceptance: функціонал доступний у єдиному модулі CampScout, дані не дублюються
  - Verify: тести в цільовому репо зелені; цей модуль uninstall без втрати даних
- [ ] **Task: Архівація fayna_instructor_school**
  - Acceptance: README/CLAUDE/TZ позначені DEPRECATED (✅), модуль не деплоїться

### Checkpoint: Phase 3
Функціонал у `fayna_camp_portal`, цей модуль — read-only reference.

---

## Боротьба з технічним боргом (REPO_STANDARD консолідація 2026-06-08)

- [x] CLAUDE.md створено (#4ZONES банер + призначення + команди + межі)
- [x] docs/TZ.md переписано у 6 областей spec-driven
- [x] docs/PLAN.md створено (цей файл)
- [x] CHANGELOG.md — додано запис 17.0.1.3.0 (синхронізація з manifest)
- [x] .gitignore — додано ігнор секретів (.env, *.key, *.pem, credentials)
- [ ] Manifest `version` vs CHANGELOG — тримати в синхроні при кожному bump

---

## Зв'язки
[docs/TZ.md](TZ.md) · [[REPO_STANDARD]] · [[CAMPSCOUT_MASTER_TZ]] §16
