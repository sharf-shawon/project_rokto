## 1. Model Consolidation & Migrations

- [x] 1.1 Move `NotificationLog` from `project_rokto/organizations/models.py` to `project_rokto/notifications/models.py`.
- [x] 1.2 Update imports and foreign keys (e.g., `donor`, `organization`) in the new model location.
- [x] 1.3 Add a `category` field to `NotificationLog` using the choices from `SMSLog.Category`.
- [x] 1.4 Create and run migrations to safely move the table and data.

## 2. Centralized Service Implementation

- [x] 2.1 Implement `UnifiedNotificationService` in `project_rokto/notifications/services.py`.
- [x] 2.2 Add `log_notification` and `log_failure` methods to the unified service.
- [x] 2.3 Refactor `UnifiedSMSService.send()` to create a high-level `NotificationLog` entry for every SMS attempt.
- [x] 2.4 Update `PhoneLoginView` and `PhoneManageView` to call the unified service for OTP dispatch.

## 3. Dispatcher & Backend Refactoring

- [x] 3.1 Refactor `project_rokto/organizations/services.py` `NotificationDispatcher` to route through the centralized gate.
- [x] 3.2 Update `EmailService` and `WebPushService` to utilize the unified logging logic.
- [x] 3.3 Ensure organizational quotas are correctly updated within the new unified flow.

## 4. Admin & Monitoring

- [x] 4.1 Consolidate `NotificationLogAdmin` into `project_rokto/notifications/admin.py`.
- [x] 4.2 Update the sidebar navigation in `OrganizationAdminSite` to point to the new model location.
- [x] 4.3 Verify that OTPs and other system messages now appear in the unified admin log.

## 5. Testing & Verification

- [x] 5.1 Write unit tests for `UnifiedNotificationService` ensuring dual-logging (NotificationLog + SMSLog).
- [x] 5.2 Add integration tests for the OTP flow to verify visibility in the main dashboard.
- [x] 5.3 Run `just check` to ensure no regressions and verify 95.00% coverage.
