# AGENTS.md

## Commands

```bash
# Run server
python manage.py runserver

# Run migrations
python manage.py migrate
python manage.py makemigrations

# Run tests
pytest

# Run single test file
pytest tests/test_user.py

# Run single test
pytest tests/test_user.py::test_create_user
```

## Prerequisites

- PostgreSQL must be running locally with database `smart_ticket`
- .env file contains secrets (do not commit)

## Architecture

- Django REST API with SimpleJWT auth
- Standard Django User model (no custom user model)
- Apps: `project`, `users`, `ticket`, `ticket_history`
- CORS enabled for `localhost:4200`
- Groq API integration for AI features

## Testing

- Uses `factory-boy` for test fixtures
- Custom faker provider in `tests/custom_faker_providers.py`
- Faker factories in `tests/factories.py`
- Fixtures defined in `conftest.py`
- pytest configured via `pytest.ini`

## Key Patterns

- JWT authentication required for most endpoints
- Project membership used for authorization
- Paginated list views with `page_size` query param
- Soft delete pattern in some models