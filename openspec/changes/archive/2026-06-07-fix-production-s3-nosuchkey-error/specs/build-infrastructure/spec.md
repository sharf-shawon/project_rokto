## ADDED Requirements

### Requirement: Resilient S3 Compatibility

The production infrastructure SHALL support robust interaction with S3-compatible object storage providers (e.g., Cloudflare R2, MinIO, AWS).

#### Scenario: Successful static file collection

- **WHEN** the `collectstatic` command is executed with `collectfasta` enabled
- **THEN** the storage backend MUST successfully list and upload objects using path-style addressing and explicit endpoint resolution without `NoSuchKey` errors
