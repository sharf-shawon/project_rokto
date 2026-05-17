## 1. Admin Site Configuration

- [ ] 1.1 Implement `NotificationLogAdmin` with filters for channel, status, and organization.
- [ ] 1.2 Implement `NotificationQuotaAdmin` with clear usage visibility.
- [ ] 1.3 Register `NotificationLog` and `NotificationQuota` in the Global Admin (`admin_site`).

## 2. Organization Admin Integration

- [ ] 2.1 Register `NotificationLog` in `org_admin_site` with read-only permissions and queryset filtering by user orgs.
- [ ] 2.2 Register `NotificationQuota` in `org_admin_site` with read-only permissions and queryset filtering by user orgs.
- [ ] 2.3 Update `OrganizationAdminSite.get_sidebar_navigation` to include a "Communications" section for Logs and Quotas.

## 3. Verification

- [ ] 3.1 Verify that Org Admins cannot edit or delete logs/quotas via the interface.
- [ ] 3.2 Verify that superusers can still manage all quotas.
- [ ] 3.3 Run `just check` to ensure code quality and coverage.
