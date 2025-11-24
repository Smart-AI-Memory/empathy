# Project Memory with Imports Example
# Location: ./.claude/CLAUDE.md

This example shows how to use @import to include shared memory files.

## Import Shared Standards

Import organization-wide coding standards:
@../shared/python-standards.md

Import security policies:
@../shared/security-policy.md

Import API design guidelines:
@../shared/api-guidelines.md

## Project-Specific Overrides

While following the imported standards above, this project has specific requirements:

### Database
- PostgreSQL 15+
- Use asyncpg for connections
- Connection pooling: min=10, max=50
- Always use prepared statements

### API Design
- RESTful with OpenAPI 3.1 specs
- Versioning: /api/v1/, /api/v2/
- Authentication: JWT tokens (15-min expiry)
- Rate limiting: 100 req/min per user

### Deployment
- Container: Docker with multi-stage builds
- Orchestration: Kubernetes
- Monitoring: Prometheus + Grafana
- Logging: Structured JSON to stdout

## Testing for This Project
- Integration tests require Docker Compose
- Mock external services (Stripe, SendGrid)
- Load testing: 1000 concurrent users target
- Chaos engineering: weekly resilience tests

---
How @import works:
1. Relative paths from this file's directory
2. Maximum 5 levels of import depth
3. Circular imports are detected and prevented
4. Imported content is included inline

Example file structure:
```
/
├── .claude/
│   └── CLAUDE.md (this file)
└── shared/
    ├── python-standards.md
    ├── security-policy.md
    └── api-guidelines.md
```

Place this file at: ./.claude/CLAUDE.md
Generated for Empathy Framework v1.8.0
