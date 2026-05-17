## 1. Data Model Refactoring (Multi-Org & PII Consolidation)

- [x] 1.1 Convert `Donor.organization` (FK) to `Donor.organizations` (ManyToManyField).
- [x] 1.2 Implement "Guest Data" field isolation logic (possibly a separate `OrganizationDonorData` through model to store Org-specific names/notes).
- [x] 1.3 Add `invite_token` and `invite_status` fields to the `Donor` model.
- [x] 1.4 Create `NotificationQuota` and `NotificationLog` models.

## 2. Notification Quota Engine

- [x] 2.1 Implement a `QuotaService` that checks both Global and Organization-level limits before dispatching notifications.
- [x] 2.2 Integrate Redis for real-time rate limiting of individual phone numbers (cooling-off period).
- [x] 2.3 Implement daily/monthly budget reset logic (management command or Celery task).

## 3. Bulk Import & Invite Flow

- [x] 3.1 Create a `DonorImportService` that parses CSVs and handles the M2M merge logic.
- [x] 3.2 Implement an API endpoint for CSV upload for Organization Admins.
- [x] 3.3 Create a task to dispatch invite notifications (SMS/Email) using the `QuotaService`.

## 4. Identity Linking (Signup Flow)

- [x] 4.1 Refactor `SignupInfoView` to check for existing `Donor` records by phone number.
- [x] 4.2 Implement the "Handover" logic that links the new `User` to the existing `Donor` identity.
- [x] 4.3 Add verification tests for the guest-to-verified transition.

## 5. Verification & Finalization

- [x] 5.1 Run `just check` to ensure type safety and linting.
- [x] 5.2 Add integration tests covering bulk upload -> invite -> signup -> quota enforcement.
