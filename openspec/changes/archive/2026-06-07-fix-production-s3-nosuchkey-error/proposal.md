## Why

The production deployment is failing during the `collectstatic` phase with a `botocore.errorfactory.NoSuchKey` error. This typically occurs when using S3-compatible providers (like Cloudflare R2 or MinIO) where the default virtual-host style addressing or endpoint resolution causes malformed requests during bucket listing operations.

## What Changes

- **S3 Configuration Update**: Switch from virtual-host style to path-style addressing for S3 operations in production.
- **Explicit Endpoint Resolution**: Ensure the `AWS_S3_ENDPOINT_URL` is explicitly passed to the storage options to prevent SDK-level malformations.
- **Improved Region Handling**: Set a default region for custom endpoints to ensure SDK stability.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `build-infrastructure`: Update production infrastructure requirements to ensure robust S3 compatibility across providers.

## Impact

- **Production Deployment**: Resolves the `NoSuchKey` error, allowing `collectstatic` to complete and the stack to start successfully.
- **Storage Stability**: Enhances compatibility with various S3-compatible object storage providers.
- **Files**: `config/settings/production.py`
