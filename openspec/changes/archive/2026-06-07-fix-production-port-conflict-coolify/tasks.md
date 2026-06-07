## 1. Adjust Production Compose Configuration

- [x] 1.1 Comment out `traefik` service in `docker-compose.production.yml`
- [x] 1.2 Remove `production_traefik` from volumes in `docker-compose.production.yml`

## 2. Verification

- [x] 2.1 Verify `docker-compose.production.yml` syntax
- [x] 2.2 Run `just check` to ensure workspace integrity
