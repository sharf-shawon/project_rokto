## 1. Implement Environment Fallback

- [x] 1.1 Update `config/settings/base.py` to import `os`
- [x] 1.2 Implement `DATABASE_URL` construction logic in `config/settings/base.py`
- [x] 1.3 Ensure the construction logic matches the Docker `entrypoint` script

## 2. Verification

- [x] 2.1 Verify settings syntax
- [x] 2.2 Run `just check` to ensure no regressions in local environment
- [x] 2.3 (Manual) Recommend user to test `python manage.py` in prod container terminal
