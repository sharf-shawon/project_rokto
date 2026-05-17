## 1. Organizations & Donors Cleanup

- [x] 1.1 Add `__init__.py` to `project_rokto/donors/tests/`.
- [x] 1.2 Replace magic numbers and fix positional boolean in `project_rokto/donors/tests/test_admin.py`.
- [x] 1.3 Replace magic numbers in `project_rokto/organizations/tests/test_admin.py`.
- [x] 1.4 Move `DonorImportService` import to top in `project_rokto/organizations/tests/test_api.py`.
- [x] 1.5 Replace magic number `302` in `project_rokto/organizations/tests/test_middleware.py`.
- [x] 1.6 Move `patch` import to top in `project_rokto/organizations/tests/test_tasks.py`.

## 2. Users Cleanup & Verification

- [x] 2.1 Remove unused `saved_user` assignment in `project_rokto/users/tests/test_forms_coverage.py`.
- [x] 2.2 Fix magic number `302` in `project_rokto/users/tests/test_guest_transition.py`.
- [x] 2.3 Run `just check` to ensure all quality gates pass.
- [x] 2.4 Archive the change.
