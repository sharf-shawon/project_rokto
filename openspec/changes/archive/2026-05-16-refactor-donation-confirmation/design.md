## Context

Currently, the business logic for updating a donor's `last_donation_date` is duplicated across two view entry points: `BloodRequestViewSet.confirm_donation` (REST API) and `confirm_donation_view` (standard Django view used for external links). This logic is triggered when both the seeker and the donor have confirmed the donation as "YES".

## Goals / Non-Goals

**Goals:**

- Centralize the "Full Confirmation" logic into the `BloodRequestDonor` model.
- Reduce code duplication in the `blood_requests/views.py`.
- Ensure that any future confirmation methods automatically inherit this logic.

**Non-Goals:**

- Modifying the UI/UX of the confirmation process.
- Changing the criteria for what constitutes a "fully confirmed" donation.
- Refactoring the search or notification systems.

## Decisions

### 1. Centralize logic in `BloodRequestDonor.save()`

- **Decision**: Overload the `save` method of `BloodRequestDonor` to check `is_fully_confirmed` and update the associated `Donor` profile.
- **Rationale**: The model layer is the source of truth for domain logic. Placing it in `save()` ensures the rule is enforced regardless of whether the change comes from an API, a view, or the Django admin.
- **Alternative**: Using a `post_save` signal. While decoupled, signals can be harder to debug and trace. Explicitly defining this in `save()` makes the behavior more transparent to future developers.

### 2. Idempotent Profile Updates

- **Decision**: Only update `donor_profile.last_donation_date` if the `blood_request.donation_date` is strictly newer (or the existing date is `None`).
- **Rationale**: Prevents accidental regressions if an older donation is confirmed after a newer one.

## Risks / Trade-offs

- **[Risk]** Redundant database writes if `save()` is called frequently without changes to confirmation status.
  - **Mitigation**: Add a check to see if the confirmation fields have actually changed before triggering the profile update (using a pattern like `__init__` state tracking or checking if the profile already matches).
- **[Risk]** Side effects in tests.
  - **Mitigation**: Ensure that factories and test setups are aware that saving a `BloodRequestDonor` might mutate a `Donor` profile.
