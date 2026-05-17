## 1. Organizations App Fixes

- [x] 1.1 Add `__init__.py` to `project_rokto/organizations/tests/`.
- [x] 1.2 Fix long line in `project_rokto/organizations/api/views.py`.
- [x] 1.3 Fix boolean positional value in `project_rokto/organizations/services.py` (cache.set).
- [x] 1.4 Fix blind exception catching in `project_rokto/organizations/services.py`.
- [x] 1.5 Fix magic numbers and imports in `project_rokto/organizations/tests/test_integration.py`.
- [x] 1.6 Fix TRY300 and blind exception in `project_rokto/organizations/tasks.py`.

## 2. Global Fixes & Verification

- [x] 2.1 Fix magic numbers in `project_rokto/users/tests/test_guest_transition.py`.
- [x] 2.2 Run `just check` to verify all fixes.
- [x] 2.3 Archive the change once verified.
