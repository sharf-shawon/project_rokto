## Why

The logic for updating a donor's `last_donation_date` upon successful donation confirmation is currently duplicated across API viewsets and standard Django views. This redundancy increases technical debt and creates a risk of data inconsistency if business rules change. Centralizing this logic into the model layer ensures that the domain rule—updating a donor's status after a confirmed donation—is always applied correctly, regardless of the entry point.

## What Changes

- **Model-Level Centralization**: Move the `last_donation_date` update logic from view functions into the `BloodRequestDonor` model (likely within the `save` method or a specialized domain method).
- **View Refactoring**: Clean up `BloodRequestViewSet.confirm_donation` and `confirm_donation_view` to remove duplicated business logic, leaving them responsible only for request handling and response formatting.
- **Robustness**: Ensure that the update logic handles edge cases, such as multiple confirmations or out-of-order updates, consistently.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `blood-request-lifecycle`: Fleshing out the requirements for donation confirmation and ensuring the model-level enforcement is documented.

## Impact

- **Models**: `project_rokto/blood_requests/models.py` (updated logic in `BloodRequestDonor`).
- **Views**: `project_rokto/blood_requests/views.py` (logic removal/simplification).
- **Tests**: `project_rokto/blood_requests/tests/` (verifying refactored logic via existing and new tests).
