## Context

Project Rokto's notification logging is currently fragmented. Technical SMS details are logged in the `notifications` app (`SMSLog`), while high-level organizational notifications are logged in the `organizations` app (`NotificationLog`). System-critical messages like login OTPs only appear in the technical log and are missing from the main admin monitoring dashboard. Furthermore, the dispatch logic is spread across multiple services, making it hard to enforce a "central gate" for all communication.

## Goals / Non-Goals

**Goals:**

- Unify all notification logging (SMS, Email, WebPush) into a single, project-wide audit trail.
- Ensure every outbound message, including OTPs, is visible in the main admin dashboard.
- Create a `UnifiedNotificationService` as the single entry point for dispatch.
- Maintain technical technical logs (`SMSLog`) for provider-specific debugging while providing a high-level `NotificationLog`.

**Non-Goals:**

- Re-implementing SMS provider backends (we will reuse `MiMSMSBackend`).
- Changing the donor preference logic (opt-in/opt-out).
- Modifying the URL shortener or rate limiter core logic (only their integration).

## Decisions

### 1. Consolidate `NotificationLog` in `notifications` app

We will move the `NotificationLog` model from `organizations` to `notifications`.

- **Rationale**: Communication logging is a foundational concern, not just an organizational one. Moving it to the `notifications` app allows it to handle system-wide logs (like OTPs).
- **Migration**: A Django migration will handle the table move and update foreign key relationships (e.g., `related_organization`, `donor`).

### 2. Implementation of `UnifiedNotificationService`

A new service class that orchestrates dispatch and dual-logging.

- **Workflow**:
  1.  Receive payload (user, channel, message, category, etc.).
  2.  Create a "PENDING" `NotificationLog` entry.
  3.  Hand off to channel-specific logic (e.g., `UnifiedSMSService`).
  4.  Update `NotificationLog` with final status (SENT/FAILED) and failure reason.
- **Rationale**: Guarantees that even if a provider call crashes, we have a record of the _attempt_.

### 3. "The Dual-Log Pattern"

For SMS, we will log to both `NotificationLog` (dashboard-level) and `SMSLog` (technical-level).

- **NotificationLog**: Focuses on _What_ was sent, _Who_ to, and the _High-level status_.
- **SMSLog**: Focuses on _Provider Raw Response_, _Message Length_, and _Technical Failure Reason_.
- **Implementation**: `UnifiedSMSService.send()` will return the `SMSLog` ID so it can be linked/referenced in the `NotificationLog` metadata if needed.

### 4. Refactoring `NotificationDispatcher`

Update the dispatcher to call `UnifiedNotificationService` instead of individual services.

- **Rationale**: Ensures that even multi-channel routes (SMS + Push) are centrally logged under the same event context.

## Risks / Trade-offs

- **[Risk]** Migration Complexity: Moving a model between apps in a live DB can be tricky. → **Mitigation**: Use `db_table` preservation during the move to avoid table recreation if possible, or a standard "move" migration sequence.
- **[Risk]** Log Bloat: Logging every OTP might create millions of rows. → **Mitigation**: Add a data retention policy/task to purge old `OTP` category logs after 30 days, while keeping `EMERGENCY` logs longer.

## Open Questions

- Should `NotificationLog` have a generic `JSONField` for channel-specific metadata? (Decided: Yes, to store things like `email_subject` or `push_id` without bloating the schema).
