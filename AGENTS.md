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

Project Rokto uses a **Spec-Driven Development** lifecycle powered by OpenSpec (`/opsx:*`). All changes MUST follow these phases:

1. **EXPLORE (`/opsx:explore`)**:
   - Research the codebase and understand integration points.
   - Clarify requirements and identify risks/assumptions.
   - Surface hidden complexity and map dependencies.
2. **PROPOSE (`/opsx:propose`)**:
   - Create a formal change proposal (`proposal.md`).
   - Define technical requirements in specs (`specs/`).
   - Document the implementation approach (`design.md`).
   - Break down work into trackable tasks (`tasks.md`).
3. **APPLY (`/opsx:apply`)**:
   - Implement tasks sequentially.
   - Match existing patterns and architecture.
   - Ensure type annotations are used for all new Python code.
4. **VERIFY (`just check`)**:
   - Add new tests for all behavior changes and edge cases.
   - **Verification:** Run `just test-coverage` and ensure total coverage remains >= 95%.
   - Ensure `mypy` and linting (`ruff`, `prettier`, `djlint`) pass.
5. **ARCHIVE (`/opsx:archive`)**:
   - Finalize the change and merge specs into the main specification database.
   - Perform a final self-review.

## AI Workflow Commands

- `/opsx:explore <topic>`: Enter thinking mode to analyze problems or code.
- `/opsx:propose <name>`: Create all artifacts for a new change in one step.
- `/opsx:apply <name>`: Implement tasks from an active change.
- `/opsx:archive <name>`: Complete a change and update foundational specs.

## Quick Start & Resources

### Environment Setup

```bash
# Sync dependencies
uv sync --locked

# Start local development with Docker
just up

# Run migrations and import data
just migrate
just manage import_locations
```

### Essential Commands

```bash
# RUN THIS BEFORE CONCLUDING ANY TASK (lint, type, test, coverage)
just check

# Run tests with coverage
just test-coverage

# Lint & Format manually
just lint

# Access Django shell
just shell
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
