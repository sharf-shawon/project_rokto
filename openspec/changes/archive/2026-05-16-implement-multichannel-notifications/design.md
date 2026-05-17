## Context

Project Rokto relies on timely notifications to connect seekers with donors. The current implementation uses placeholders. We need a unified system that handles multiple channels (SMS, Email, Push) asynchronously while respecting user preferences and organization budgets.

## Goals / Non-Goals

**Goals:**

- Centralize all notification logic into a single `NotificationDispatcher`.
- Support SMS (via `django-mimsms`), Email (SMTP), and Web Push (VAPID).
- Enforce organization quotas and user "cooling-off" periods.
- Allow users to manage their notification preferences per channel and type.

**Non-Goals:**

- Implementing a mobile app (Web Push is the target for now).
- Handling in-app chat (only one-way notifications).

## Decisions

### 1. Asynchronous Task Queue (Celery + Redis)

- **Decision**: All notification dispatches will be offloaded to Celery.
- **Rationale**: Email/SMS gateways can be slow or unreliable. Async handling ensures the main request-response cycle remains fast and allows for retries.

### 2. The Multi-Channel Dispatcher

- **Decision**: Create a `NotificationDispatcher` service that takes a `recipient`, a `template_name`, and `context`.
- **Rationale**: Simplifies the call site. The dispatcher handles preference checks, quota checks, and routing to the correct sub-services (EmailService, SMSService, etc.).

### 3. Localization & BDIX Resilience (Web Push)

- **Decision**: Use `pywebpush` for standard browser Push API.
- **Rationale**: Avoids dependence on Firebase or other US-based SaaS that might be throttled or blocked during local network instability, aligning with the "Local Resilience" vision.

### 4. Integration with `django-mimsms`

- **Decision**: Use the specified package for SMS.
- **Rationale**: Specifically designed for Bangladeshi SMS gateways, ensuring high deliverability.

## Risks / Trade-offs

- **[Risk] Cost of SMS** → SMS is expensive compared to Email.
  - **Mitigation**: Enforce strict quotas and prioritize Web Push for non-critical alerts.
- **[Risk] Delivery Failure** → Network issues with local gateways.
  - **Mitigation**: Implement exponential backoff retries in Celery.
