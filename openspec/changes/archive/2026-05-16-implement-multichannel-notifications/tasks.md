## 1. Infrastructure & Core Models

- [ ] 1.1 Install dependencies: `django-mimsms`, `pywebpush`, `celery`, `redis`.
- [ ] 1.2 Configure Celery in `config/celery.py` and `config/settings/base.py`.
- [ ] 1.3 Implement `NotificationPreference` model in `project_rokto/users/models.py`.
- [ ] 1.4 Implement `WebPushSubscription` model in `project_rokto/users/models.py`.
- [ ] 1.5 Create and run migrations for new models.

## 2. Notification Engine (The Dispatcher)

- [ ] 2.1 Create `NotificationDispatcher` service in `project_rokto/organizations/services.py`.
- [ ] 2.2 Implement `EmailService` using standard Django Mail.
- [ ] 2.3 Implement `SMSService` using `django-mimsms`.
- [ ] 2.4 Implement `WebPushService` using `pywebpush` and VAPID.
- [ ] 2.5 Create base notification templates in `project_rokto/templates/notifications/`.

## 3. Integration & Automation

- [ ] 3.1 Integrate dispatcher into `BloodRequestViewSet.perform_create` to alert donors.
- [ ] 3.2 Update `send_donor_invite` task to use the new dispatcher.
- [ ] 3.3 Implement Web Push registration API endpoint.
- [ ] 3.4 Add Service Worker for Web Push handling in `static/js/sw.js`.

## 4. Preferences & Validation

- [ ] 4.1 Create a UI/API for users to manage `NotificationPreference`.
- [ ] 4.2 Add validation tests for preference-aware routing.
- [ ] 4.3 Add validation tests for quota enforcement within the dispatcher.
- [ ] 4.4 Run `just check` to ensure total coverage remains >= 95.00%.
