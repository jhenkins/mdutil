# Project Onboarding Guide

Welcome to the team! This guide covers everything you need to get started.

## Prerequisites

Before you begin, ensure you have the following installed:

1. Python 3.11+
2. Git
3. Node.js 18+
4. Docker Desktop

```bash
# Clone the repository
git clone https://github.com/example/project.git
cd project

# Install dependencies
pip install -r requirements.txt
npm install

# Run tests
pytest
npm test
```

## Architecture Overview

The project follows a microservices architecture:

```mermaid
graph LR
    A[Frontend] --> B[API Gateway]
    B --> C[User Service]
    B --> D[Order Service]
    B --> E[Payment Service]
    C --> F[(PostgreSQL)]
    D --> G[(MongoDB)]
    E --> H[(Redis)]
```

## Core Concepts

### Service Architecture

Microservice
:   An independently deployable unit that owns a specific business capability.

API Gateway
:   A single entry point that handles routing, authentication, and rate limiting.

Event Bus
:   Asynchronous messaging system for inter-service communication.

### Data Models

User entity:
- `id`: UUID
- `email`: string, unique
- `name`: string
- `role`: enum [admin, user, guest]
- `created_at`: datetime
- `updated_at`: datetime

## Development Setup

### Task Checklist

- [x] Fork the repository
- [x] Clone your fork locally
- [x] Create a feature branch
- [x] Install development dependencies
- [ ] Configure local database
- [ ] Run the test suite
- [ ] Make your changes
- [ ] Write tests for new features
- [ ] Update documentation
- [ ] Submit pull request

### Code Style

Follow these conventions:

```python
# GOOD
def calculate_total(items: list[Item]) -> float:
    """Calculate total price with tax."""
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + TAX_RATE)

# BAD - no type hints, no docstring
def calc(items):
    s = 0
    for i in items:
        s += i.price
    return s * 1.08
```

## Testing Strategy

### Unit Tests

```python
def test_calculate_total():
    items = [Item(price=10.0), Item(price=20.0)]
    total = calculate_total(items)
    assert total == 32.4  # 30 * 1.08
```

### Integration Tests

- Test API endpoints with mock database
- Test service-to-service communication
- Test event bus message handling

### Performance Tests

- Load test with 1000 concurrent users
- Measure p95 response time
- Monitor memory usage

## Math in Documentation

The compound interest formula:

$A = P(1 + \frac{r}{n})^{nt}$

Where:
- $A$ = final amount
- $P$ = principal investment
- $r$ = annual interest rate
- $n$ = number of times interest is compounded per year
- $t$ = number of years

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///local.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `SECRET_KEY` | `changeme` | JWT secret key |
| `DEBUG` | `false` | Enable debug mode |

### Config File Example

```ini
[database]
url = postgresql://user:pass@localhost:5432/mydb
pool_size = 10

[redis]
url = redis://localhost:6379
default_ttl = 3600

[auth]
secret_key = your-secret-key
token_expiry = 86400
```

## Deployment

### CI/CD Pipeline

```mermaid
graph TD
    A[Push to main] --> B[Run tests]
    B --> C{All pass?}
    C -->|Yes| D[Build Docker image]
    C -->|No| E[Notify team]
    D --> F[Push to registry]
    F --> G[Deploy to staging]
    G --> H{Smoke tests pass?}
    H -->|Yes| I[Deploy to production]
    H -->|No| J[Rollback]
```

### Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Changelog entry added
- [ ] Database migrations reviewed
- [ ] Rollback plan documented

## Troubleshooting

### Common Issues

1. **Database connection refused**
   - Check if PostgreSQL is running: `pg_isready`
   - Verify credentials in `.env`

2. **Port already in use**
   ```bash
   lsof -i :5432
   kill -9 <PID>
   ```

3. **Slow query performance**
   - Check indexes: `\di` in psql
   - Run `EXPLAIN ANALYZE` on slow queries

### Strikethrough for Deprecated Info

This section ~~was required~~ is now optional as of v3.0.

The old ~~monolithic~~ microservices architecture is still supported.

## Definitions

SLA
:   Service Level Agreement — commits to 99.9% uptime.

RTO
:   Recovery Time Objective — maximum acceptable downtime (15 minutes).

RPO
:   Recovery Point Objective — maximum acceptable data loss (5 minutes).

## Important Notes

See the [API documentation](https://docs.example.com/api "API Reference") for endpoint details.

For deployment procedures, see the [runbook](https://wiki.example.com/runbook "Deployment Runbook").

Here is a footnote reference[^1] and another[^2].

[^1]: This is the first footnote definition.
[^2]: This is the second footnote definition with **bold** and `code`.

## Subscripts and Superscripts

Chemical notation:
- Water: H~2~O
- Carbon dioxide: CO~2~
- Glucose: C~6~H~12~O~6~

Math notation:
- Pythagorean theorem: a^2^ + b^2^ = c^2^
- Quadratic: x = (-b ± √(b^2^ - 4ac)) / 2a

## Highlighted Warnings

==Security: Never commit API keys or secrets to version control!==

==Performance: Always use parameterized queries to prevent SQL injection!==

## Images

![Team Photo](assets/team.jpg)

![Architecture Diagram](docs/architecture.png =800x600)

## Nested List Example

Development Workflow
1. Create feature branch
    1. `git checkout -b feature/my-feature`
    2. Make changes
        1. Write code
        2. Write tests
        3. Run tests
    3. Push branch
        1. `git push origin feature/my-feature`
2. Create pull request
    1. Fill in PR template
    2. Request review
3. Address feedback
    1. Make requested changes
    2. Re-request review
4. Merge
    1. Squash and merge
    2. Delete branch

## Math Formulas

The standard deviation formula:

$\sigma = \sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i - \mu)^2}$

Big O notation examples:
- O(1) — constant time
- O(log n) — logarithmic time
- O(n) — linear time
- O(n log n) — linearithmic time
- O(n^2^) — quadratic time

## Links and References

- [Getting Started Guide](https://docs.example.com/getting-started "Begin here")
- [API Reference](https://api.example.com/docs "Complete API documentation")
- [Troubleshooting](https://docs.example.com/troubleshooting "Common issues")
- [Contributing](https://github.com/example/project/blob/main/CONTRIBUTING.md "How to contribute")

## Task Lists

### Pre-launch Checklist

- [x] Code review complete
- [x] Tests passing (100/100)
- [x] Documentation updated
- [ ] Staging deployment successful
- [ ] Performance testing passed
- [ ] Security audit complete
- [ ] Production deployment approved
- [ ] Monitoring configured
