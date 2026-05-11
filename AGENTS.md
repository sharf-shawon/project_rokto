# AGENTS.md - Repository Canonical Instructions

This is the single source of truth for all agents (AI and human) working on Project Rokto. All provider-specific instruction files must defer to this document.

## Vision: Sovereign Blood Donation Network for Bangladesh

Project Rokto is a **Decentralized, Resilient, Privacy-First, and Automated** blood donation network. It is designed to be the digital backbone of blood donation in Bangladesh, ensuring that life-saving infrastructure is open-source, community-owned, and free from centralized bottlenecks.

## Architecture

- **Foundation:** Built on [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django).
- **Admin Interface:** Uses [django-unfold](https://github.com/unfoldadmin/django-unfold) for a modern, responsive administrative experience.
- **Stack:** Django 6.0 (Python 3.14), Django REST Framework, PostGIS (PostgreSQL + Spatial), Redis.
- **Frontend:** Webpack, Sass, Bootstrap 5.
- **Package Managers:** `uv` (Python), `npm` (JS).
- **Task Runner:** `just`.
- **Environment:** Docker-based development and production.

### Core Modules

- `config/`: Core Django settings, URL routing (`urls.py`), and WSGI/ASGI configuration.
- `project_rokto/users/`: Custom user model, phone-based authentication, NID verification logic, and health profile management.
- `project_rokto/locations/`: Geographical database for Bangladesh (Postcodes, Upazilas, Districts) with geocoded PostGIS coordinates.
- `project_rokto/blood_requests/`: Core logic for blood requests, donor matching, and dual-party confirmation.
- `project_rokto/templates/`: Django templates using Bootstrap 5 and Sass.
- `project_rokto/static/`: Static assets (JS, CSS/Sass, images).
- `compose/`: Docker configuration for local and production environments.

## Domain-Specific Patterns (MANDATORY)

- **Dual-Party Confirmation:** A donation is only marked as successful when **both the Seeker and the Donor** confirm it (YES/YES).
- **Multi-Layered Geocoding:**
  1. **GeoNames:** Primary local lookup for high-speed, offline-capable resolution.
  2. **ArcGIS:** Secondary fallback for precision.
     _Note: Nominatim is deprecated and should not be used._
- **Privacy-First Contact Exchange:**
  - Contact details are never public.
  - Exchange is only triggered after mutual acceptance.
  - Every reveal is logged and audited.
  - Search results are obfuscated to prevent mass scraping.
- **Authentication:** Users can login/signup via phone number and OTP. New users are created with their phone number as their username.
- **Geospatial Search:** Donor searching is "local-first" and distance-aware using GeoDjango `Distance` queries.

## Documentation Mandate

Agents MUST:

1. **Always document/update code flow:** When changing logic, ensure the READMEs, docstrings, and diagrams are updated.
2. **Sync docs:** Ensure that changes in one part of the documentation are reflected everywhere else (e.g., if a CLI command changes, update it in `AGENTS.md` and `README.md`).

## Development Lifecycle (MANDATORY)

All changes MUST follow this full development cycle:

1. **TRIAGE:**
   - Restate the task to ensure understanding.
   - Define scope and identify risks/assumptions.
   - List impacted files, documentation, and tests.
2. **CLARIFY:** Ask questions for any ambiguity or risk. No coding until critical clarity is reached.
3. **PLAN:**
   - List files to be changed.
   - Define tests to add/update (ensuring 95%+ coverage).
   - Sync documentation requirements.
   - Define validation steps.
4. **CODE:**
   - Match existing patterns and architecture.
   - Implement minimal, focused changes.
   - Ensure type annotations are used.
5. **TEST SYNC:**
   - Add new tests for all behavior changes and edge cases.
   - Update any stale tests.
   - **Verification:** Run `just test-coverage` and ensure total coverage remains >= 95%.
6. **DOCS SYNC:** Update all impacted docs, examples, changelogs, and comments to reflect the latest updates.
7. **VALIDATE:** Run the full quality suite: `just check` (lint → format → type → test → coverage).
8. **REVIEW:** Perform a self-review as a senior engineer. Verify synchronization and Definition of Done (DoD).
9. **COMMIT:**
   - Use brief, clean, and descriptive **Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`, `test:`).
   - Summarize the changes, tests, and documentation updated.

## Quick Start & Resources

### Learning Resources

- [Django Documentation](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostGIS Best Practices](https://postgis.net/workshops/postgis-intro/)

### Basic Setup

```bash
# Start local development with Docker
just up

# Run migrations
just migrate

# Import geographical data
just manage import_locations
```

### Essential Commands

```bash
# RUN THIS BEFORE EVERY PUSH (lint, type-check, test, coverage)
just check

# Run tests with coverage report
just test-coverage

# Lint & Format (pre-commit)
just lint

# Access Django shell
just shell

# Create superuser
just manage createsuperuser
```

## Quality Expectations

- **Code/Test/Docs Sync:** Every code change MUST include corresponding tests and documentation updates.
- **Testing:**
  - **95%+ total code coverage** (mandatory).
  - 95% lines/90% branches on business logic.
  - New features must have unit and/or integration tests covering edge cases.
- **Types:** All new Python code should be type-annotated. `mypy` must pass.
- **Linting:** `ruff`, `prettier`, and `djlint` must pass via pre-commit hooks.
- **Conventional Commits:** Use clear, concise commit messages following the Conventional Commits specification.
