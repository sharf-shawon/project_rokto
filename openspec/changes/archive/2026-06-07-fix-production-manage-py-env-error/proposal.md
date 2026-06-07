## Why

Administrative commands (e.g., `python manage.py createsuperuser`) currently fail when run inside the production container terminal with an `ImproperlyConfigured` error. This is because the `DATABASE_URL` environment variable is constructed dynamically in the Docker `entrypoint` script, which is not executed for interactive shell sessions or direct `docker exec` commands.

## What Changes

- **Enhance Database Configuration**: Update `config/settings/base.py` to automatically construct `DATABASE_URL` from individual `POSTGRES_*` environment variables if it is missing from the environment.
- **Maintain Consistency**: Ensure the fallback logic in Django settings matches the construction logic in the Docker `entrypoint` script.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `build-infrastructure`: Update production infrastructure settings to handle environment variable availability more robustly.

## Impact

- **Production Operations**: Enables the use of `manage.py` commands in interactive container shells without manual environment exporting.
- **Resilience**: Makes the application less dependent on the specific execution path (entrypoint vs. exec) for core configuration.
- **Files**: `config/settings/base.py`
