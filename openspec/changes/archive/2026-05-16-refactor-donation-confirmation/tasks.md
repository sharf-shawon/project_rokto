## 1. Model Refactoring

- [x] 1.1 Implement logic in `BloodRequestDonor` model to update the donor's `last_donation_date` when `is_fully_confirmed` is true.
- [x] 1.2 Overload `BloodRequestDonor.save()` to trigger the confirmation update logic.
- [x] 1.3 Add a new test case in `project_rokto/blood_requests/tests/test_model_logic.py` to verify that saving a fully confirmed record updates the donor profile.

## 2. View Cleanup

- [x] 2.1 Refactor `BloodRequestViewSet.confirm_donation` in `project_rokto/blood_requests/views.py` to remove redundant donor profile update logic.
- [x] 2.2 Refactor `confirm_donation_view` in `project_rokto/blood_requests/views.py` to remove redundant donor profile update logic.
- [x] 2.3 Verify that the API confirmation endpoint correctly triggers the model-level update.
- [x] 2.4 Verify that the Web confirmation view correctly triggers the model-level update.

## 3. Verification & Cleanup

- [x] 3.1 Run all tests in `project_rokto/blood_requests/tests/` to ensure no regressions.
- [x] 3.2 Update `blood-request-lifecycle` main spec in `openspec/specs/` if any TBD sections can be improved beyond this change (optional but good practice).
- [x] 3.3 Run `just check` to verify linting and type safety.
