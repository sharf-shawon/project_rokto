## 1. Production Settings Update

- [x] 1.1 Set `AWS_S3_ADDRESSING_STYLE = "path"` in `config/settings/production.py`
- [x] 1.2 Explicitly add `"endpoint_url": AWS_S3_ENDPOINT_URL` to `STORAGES["default"]["OPTIONS"]`
- [x] 1.3 Explicitly add `"endpoint_url": AWS_S3_ENDPOINT_URL` to `STORAGES["staticfiles"]["OPTIONS"]`
- [x] 1.4 Explicitly add `"addressing_style": "path"` to `STORAGES["default"]["OPTIONS"]`
- [x] 1.5 Explicitly add `"addressing_style": "path"` to `STORAGES["staticfiles"]["OPTIONS"]`
- [x] 1.6 Ensure `AWS_S3_REGION_NAME` defaults to `"auto"` if not provided in environment

## 2. Verification

- [x] 2.1 Verify settings syntax and env resolution
- [x] 2.2 Run `just check` to ensure total project health
