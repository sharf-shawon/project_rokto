## Context

The system recently gained `NotificationLog` and `NotificationQuota` models to handle multi-channel alerts and budgeting. However, these models were not registered in any Django Admin interface.

## Goals / Non-Goals

**Goals:**

- Expose `NotificationLog` and `NotificationQuota` to superusers with full control.
- Expose `NotificationLog` and `NotificationQuota` to Org Admins with read-only access to their specific organization's data.
- Ensure the Org Admin sidebar includes intuitive navigation for these logs.

**Non-Goals:**

- Modifying the underlying data models.
- Changing the dispatch or quota calculation logic.

## Decisions

### 1. Dual Admin Registration

- **Decision**: Create base Admin classes and subclass them for `admin_site` (Global) and `org_admin_site` (Organization).
- **Rationale**: Allows for clean separation of permissions and querysets while sharing display logic.

### 2. Permissions for Org Admins

- **Decision**: Override `has_add_permission`, `has_change_permission`, and `has_delete_permission` to return `False` for Org Admins.
- **Rationale**: Communication logs and quotas are "records of truth" that should not be tampered with by organization-level users.

### 3. Queryset Filtering

- **Decision**: Override `get_queryset` in `org_admin_site` classes to filter by the current user's organization memberships.
- **Rationale**: Core requirement of the project's data sovereignty model.

### 4. Sidebar Organization

- **Decision**: Create a new navigation group "Communications" in the `OrganizationAdminSite`.
- **Rationale**: Differentiates purely administrative/billing data (Quotas/Logs) from domain data (Donors/Organizations).

## Risks / Trade-offs

- **[Risk] Log Volatility** → Querying millions of logs could be slow.
  - **Mitigation**: Use `list_select_related` for `donor` and `organization` fields and ensure we use `SimpleRouter` behavior or restricted search fields.
