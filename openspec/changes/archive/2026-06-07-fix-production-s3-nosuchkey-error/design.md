## Context

The production Django environment uses `django-storages` with the `s3boto3` backend and `collectfasta` for optimized static file collection. The current configuration relies on default `boto3` behavior for endpoint resolution and addressing style. Some S3-compatible providers (like Cloudflare R2) return a `NoSuchKey` error during `ListObjects` if the request is interpreted as virtual-host style or if the prefix resolution is inconsistent.

## Goals / Non-Goals

**Goals:**

- Fix the `NoSuchKey` error during `collectstatic`.
- Ensure S3 configuration is resilient to various providers (AWS, R2, MinIO).
- Explicitly define addressing style and endpoint URL in storage settings.

**Non-Goals:**

- Changing the local storage backend (whitenoise/local files).
- Modifying IAM permissions (assuming they are already correct).

## Decisions

### 1. Set `AWS_S3_ADDRESSING_STYLE = "path"`

- **Rationale**: Path-style addressing (`endpoint.com/bucket`) is generally more reliable across different S3-compatible providers compared to virtual-host style (`bucket.endpoint.com`). It avoids DNS resolution issues for bucket subdomains.
- **Alternatives**: Keeping "auto" or "virtual". _Rejected_ as it is the likely cause of the current failure.

### 2. Explicitly pass `endpoint_url` in `STORAGES` options

- **Rationale**: While `AWS_S3_ENDPOINT_URL` is a global setting, explicitly passing it to the storage options ensures that the backend uses the correct URL for all operations, including the listing operations triggered by `collectfasta`.

### 3. Ensure `AWS_S3_REGION_NAME` is set

- **Rationale**: Some SDK operations require a region even for custom endpoints. Setting this to a standard value (or "auto" for R2) prevents potential `botocore` resolution errors.

## Risks / Trade-offs

- **[Risk]** Some legacy providers might only support virtual-host style. → **Mitigation**: Most modern S3 providers (including AWS) support path-style, and it is the standard for compatibility.
