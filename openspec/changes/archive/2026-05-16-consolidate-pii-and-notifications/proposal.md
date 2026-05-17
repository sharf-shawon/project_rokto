## Why

Currently, Project Rokto lacks a centralized mechanism for Organizations to manage their own donor databases, including inviting unverified donors to the platform. Additionally, PII (phone numbers) is redundant across models, and there is no budgeting or rate-limiting system to prevent notification misuse or cost overruns at the organization or project level.

## What Changes

- **Organization-Scale Donor Management**:
  - Change `Donor.organization` (FK) to `Donor.organizations` (M2M) to allow donors to belong to multiple networks.
  - Implement Bulk CSV Import for Organization Admins.
  - Implement an automated Invite/Sign-up flow that links "Guest" donors to new User accounts upon verification.
- **Notification Budgeting & Rate Limiting**:
  - Implement a centralized Quota Engine to track and limit SMS, Email, and WebPush notifications.
  - Add per-organization and project-wide daily/weekly/monthly budgets.
  - Add sophisticated misuse protection (e.g., cooling-off periods for user notifications).
- **PII Consolidation**:
  - **BREAKING**: Refactor `Donor` and `User` models to consolidate identity and contact information, ensuring a single source of truth for PII.

## Capabilities

### New Capabilities

- `notification-budgeting`: Centralized system for tracking and limiting notification costs and volume.
- `organization-donor-management`: Tools for organizations to import, invite, and track their donor networks.

### Modified Capabilities

- `donor-privacy-security`: Updated to include rules for PII consolidation and secure invite-link handling.

## Impact

- **Models**: `User`, `Donor`, `Organization`, and new `NotificationQuota` models.
- **Services**: New Notification & Quota services.
- **API**: New endpoints for CSV upload and quota management.
- **Auth**: Modified signup flow to handle auto-linking of guest donors.
