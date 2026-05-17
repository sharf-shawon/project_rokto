## 1. Local Environment Setup

- [ ] 1.1 Verify current failure in celerybeat container logs
- [ ] 1.2 Identify the location of the /start-celerybeat script

## 2. Docker Compose Improvements

- [ ] 2.1 Add healthcheck to 'django' service in docker-compose.yml
- [ ] 2.2 Update 'celerybeat' service to depend on 'django' health status

## 3. Startup Script Modification

- [ ] 3.1 Update /start-celerybeat to wait for database availability
- [ ] 3.2 Add migration check or 'python manage.py migrate django_celery_beat' to the script

## 4. Verification

- [ ] 4.1 Restart containers with 'docker-compose up --build'
- [ ] 4.2 Confirm celerybeat starts successfully without ProgrammingError
