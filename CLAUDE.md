# Fayna Instructor School — CLAUDE.md

> 🚫 **#4ZONES — НІКОЛИ не працювати напряму на сервері.**
> Єдиний шлях: **локально → GitHub (push) → staging → prod (pull)**. Жодних правок файлів на сервері (nano/vim/scp/docker exec з редагуванням), жодних тимчасових скриптів на проді — спершу локально, коміт, push, тоді pull на сервер. Зміни «на сервері» зникають при наступному `git pull`/rebuild. Git — єдине джерело правди. ([[meta/golden-rules-developer]] #3)

> ⚠️ **DEPRECATED (pivot 2026-06-07).** Модуль заморожений і не деплоїться. Весь функціонал переноситься у `fayna_camp_portal` ([VladSh77/fayna-campscout](https://github.com/VladSh77/fayna-campscout)) — єдиний модуль CampScout. Код тут зберігається як reference до завершення міграції.

> Як працювати з репо. **Що** будуємо — у [docs/TZ.md](docs/TZ.md) (специфікація за REPO_STANDARD). План реалізації — у [docs/PLAN.md](docs/PLAN.md).

## Призначення

Odoo 17 Community модуль для школи інструкторів (вожатих) CampScout: каталог курсів зі state-machine, запис учасників, публічна сторінка `/instructor-school` із формою подачі заявки. Phase 8 вертикального стеку Fayna Camp (Strangler Fig decomposition, `CAMPSCOUT_MASTER_TZ.md §16`).

**Версія:** `17.0.1.3.0` | Модуль: `fayna_instructor_school` | License: LGPL-3 | depends: `base`, `website`, `mail`

## Структура модуля

```
fayna_instructor_school/
  models/
    course.py        # instructor.course — каталог + state-machine (draft→open→in_progress→completed/cancelled)
    enrollment.py    # instructor.enrollment — запис учасника + payment_status + capacity guard
  controllers/
    website.py       # публічні роути /instructor-school, /apply/<id>, /enroll/<id>
  views/             # tree/form/search для course + enrollment, меню
    website/instructor_school_page.xml  # QWeb публічна сторінка + форма заявки
  data/ir_config_parameter.xml          # feature flag fayna_instructor_school.active (default False)
  security/          # ir.model.access.csv + ir_rules.xml (portal бачить лише свої записи)
  tests/             # pytest: scaffold + course/enrollment + instructor school
  i18n/              # uk_UA.po + pl_PL.po
  docs/              # TZ.md, PLAN.md
```

## Команди

```bash
# Тести (pytest, поза Odoo-середовищем — сумісність/sanity)
python -m pytest tests/ -v

# Lint + format (pre-commit: ruff + ruff-format + OCA + bandit + gitleaks)
pre-commit run --all-files
ruff check .
ruff format --check .

# Coverage (ціль ≥70%)
python -m pytest tests/ --cov=. --cov-report=term-missing
```

## Deploy — #4ZONES (Mac → GitHub → staging → prod)

> Модуль DEPRECATED — не деплоїться. Команди нижче — еталонний шлях, якщо реактивація знадобиться.

```bash
git push origin main
ssh prod 'cd /opt/campscout/custom-addons/fayna_instructor_school && git pull && sudo chmod -R o+rX .'
# Python-only fix → достатньо рестарту:
ssh prod 'docker restart campscout_web'
# Зміна моделей/views → update модуля:
ssh prod 'docker exec campscout_web odoo -u fayna_instructor_school --stop-after-init -d campscout && docker restart campscout_web'
```

Модуль встановлюється **inert** (feature flag `fayna_instructor_school.active` = `False`). Жодної зміни поведінки до явного flip.

## Coding conventions

- Odoo 17 ідіоми: `@api.depends` для computed, `@api.constrains` для валідації, `@api.model_create_multi` для `create`
- State-machine actions (`action_open_enrollment`, `action_confirm`...) — кожен крок guard через `UserError`, переходи лише з дозволеного стану
- Помилки користувачу — через `_()` (translate); рядки UI → в `i18n/uk_UA.po` + `pl_PL.po`
- Публічні роути: `auth="public"` для перегляду/заявки, `auth="user"` для enroll; завжди `.sudo()` для запису від анонімного відвідувача + guard на дублікати/місткість
- Секрети — ніколи в код/UI/лог (див. `.gitignore`); портал бачить лише свої enrollment (`ir_rules.xml`)
- Semantic Versioning у `__manifest__.py`: одна сесія = один bump = реліз

## Тестування

```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=. --cov-report=term-missing   # ціль ≥70%
```

Тести в `tests/`: `test_scaffold.py` (install/flag/deps), `test_course_enrollment.py` (state-machine + capacity + unique constraint), `test_instructor_school.py` (моделі + роути). Кожен bug-fix → regression тест.

## Документація репо

- **docs/TZ.md** — специфікація (6 областей spec-driven: Objective / Commands / Project Structure / Code Style / Testing / Boundaries)
- **docs/PLAN.md** — dependency graph + фази + checkpoints
- **CHANGELOG.md** — історія версій (Keep a Changelog)
- **README.md** — короткий опис + встановлення + посилання

## Зв'язки

Стандарт: [[REPO_STANDARD]] · Master: [[CAMPSCOUT_MASTER_TZ]] §16 Phase 8 · Інструменти: [[library/tools/python]] · [[library/tools/docker]] · [[library/tools/git]] · Golden rules: [[meta/golden-rules-developer]] · Memory: [[claude-memory/project_campscout_arch_pivot_2026-06-07]]
