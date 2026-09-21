We are continuing development of the FinPilot personal finance application.

STAGE 1 has already been completed.

Now implement ONLY STAGE 2: DATABASE + AUTHENTICATION.

Do not implement transactions, document processing, RAG, LLM, agents, budgets, goals, subscriptions, or purchase analysis yet.

==================================================
PROJECT CONTEXT
==================================================

FinPilot is a personal finance decision-support application.

Future capabilities include:

- transaction ingestion
- transaction categorization
- recurring payment detection
- unusual spending detection
- monthly financial summaries
- budgets
- financial goals
- upcoming obligations
- natural-language financial questions
- RAG over financial documents
- local LLM
- API LLM fallback
- financial scenario analysis

Important architecture principle:

LLM handles language understanding, extraction, routing and explanation.

Deterministic backend code handles:
- financial calculations
- aggregation
- forecasting
- financial rules
- scenario analysis

The application must be multi-user and securely isolate each user's data.

==================================================
STAGE 1
==================================================

Stage 1 already contains:

backend/
    app/
        main.py
        api/
            v1/
                health.py
        core/
            config.py
            logging.py
            exceptions.py
        schemas/
            common.py

    tests/

    requirements.txt
    Dockerfile
    .env.example

root:
    docker-compose.yml
    README.md

Existing endpoint:

GET /api/v1/health

Do not break Stage 1.

==================================================
TECHNOLOGY
==================================================

Use:

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- pydantic-settings
- python-jose OR PyJWT for JWT
- passlib/bcrypt OR pwdlib for password hashing
- pytest
- httpx

Prefer modern maintained libraries.

Use SQLAlchemy 2.x typed models.

Use UUID primary keys.

Use PostgreSQL.

==================================================
DATABASE ARCHITECTURE
==================================================

Create:

backend/app/
    models/
    repositories/
    services/
    api/v1/
    schemas/

Suggested structure:

app/
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── refresh_token.py
│
├── repositories/
│   ├── __init__.py
│   └── user_repository.py
│
├── services/
│   ├── __init__.py
│   └── auth_service.py
│
├── api/
│   └── v1/
│       ├── health.py
│       └── auth.py
│
├── schemas/
│   ├── common.py
│   └── auth.py
│
└── core/
    ├── config.py
    ├── database.py
    ├── security.py
    ├── logging.py
    └── exceptions.py

==================================================
DATABASE CONFIGURATION
==================================================

Create database.py.

Use SQLAlchemy async support if practical.

Use:

AsyncEngine
async_sessionmaker
AsyncSession

DATABASE_URL must come from environment variables.

Do not hardcode credentials.

Provide a reusable database dependency:

get_db()

Routes and services must use the dependency.

==================================================
ALEMBIC
==================================================

Configure Alembic.

Create the initial migration.

The migration must create:

users
refresh_tokens

Do not manually create tables during application startup.

Do NOT use:

Base.metadata.create_all()

Alembic must be the source of schema migrations.

==================================================
USER MODEL
==================================================

Create User model:

id:
    UUID primary key

email:
    string
    unique
    indexed
    not null

password_hash:
    string
    not null

name:
    string
    not null

is_active:
    boolean
    default true

created_at:
    timestamp with timezone

updated_at:
    timestamp with timezone

Use UTC timestamps.

Email should be normalized to lowercase before storing.

==================================================
REFRESH TOKEN MODEL
==================================================

Create RefreshToken model:

id:
    UUID primary key

user_id:
    foreign key users.id
    indexed
    not null

token_hash:
    string
    not null

expires_at:
    timestamp with timezone
    not null

revoked:
    boolean
    default false

created_at:
    timestamp with timezone

Add relationship from RefreshToken to User.

==================================================
PASSWORD SECURITY
==================================================

Never store plaintext passwords.

Use a secure password hashing algorithm supported by the selected library.

Create functions:

hash_password(password)

verify_password(password, password_hash)

Do not log passwords.

Do not return password_hash in API responses.

==================================================
JWT
==================================================

Implement:

access token
refresh token

JWT payload should contain:

sub = user UUID
type = access OR refresh
exp = expiration time
iat = issued-at time

Use SECRET_KEY from environment configuration.

Do not hardcode SECRET_KEY.

Configure expiration values through environment variables.

For example:

ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS

Use UTC.

==================================================
AUTH SCHEMAS
==================================================

Create Pydantic schemas:

UserRegister:
    email
    password
    name

UserResponse:
    id
    email
    name
    is_active
    created_at

TokenResponse:
    access_token
    refresh_token
    token_type

LoginRequest:
    email
    password

RefreshRequest:
    refresh_token

Never expose password_hash.

==================================================
AUTH SERVICE
==================================================

Create auth_service.py.

Responsibilities:

register_user()
authenticate_user()
create_access_token()
create_refresh_token()
refresh_access_token()
revoke_refresh_token()

Keep business logic out of route handlers.

Routes should call the service.

==================================================
USER REPOSITORY
==================================================

Create user_repository.py.

Implement functions such as:

get_by_id()
get_by_email()
create()

Do not put business logic in repository.

Repository handles database access.

==================================================
AUTH API
==================================================

Create:

POST /api/v1/auth/register

Request:

{
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "name": "Test User"
}

Response:

{
    "id": "...",
    "email": "user@example.com",
    "name": "Test User",
    "is_active": true,
    "created_at": "..."
}

Do not automatically expose sensitive information.

--------------------------------------------

POST /api/v1/auth/login

Request:

{
    "email": "user@example.com",
    "password": "StrongPassword123!"
}

Response:

{
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer"
}

--------------------------------------------

POST /api/v1/auth/refresh

Request:

{
    "refresh_token": "..."
}

Return a new access token.

Validate:

- signature
- token type
- expiration
- refresh token exists
- refresh token is not revoked
- user exists
- user is active

--------------------------------------------

POST /api/v1/auth/logout

Request:

{
    "refresh_token": "..."
}

Revoke the refresh token.

Return:

{
    "message": "Successfully logged out"
}

--------------------------------------------

GET /api/v1/auth/me

Require:

Authorization: Bearer <access_token>

Return:

{
    "id": "...",
    "email": "...",
    "name": "...",
    "is_active": true,
    "created_at": "..."
}

==================================================
AUTHENTICATION DEPENDENCY
==================================================

Create:

get_current_user()

It must:

1. Read Authorization header.
2. Extract Bearer token.
3. Decode JWT.
4. Validate token type.
5. Extract user ID from "sub".
6. Load user from database.
7. Verify user is active.
8. Return User object.

Protected endpoints should use:

current_user: User = Depends(get_current_user)

Never accept user_id from the frontend to determine ownership.

==================================================
ERROR HANDLING
==================================================

Use appropriate HTTP status codes.

Registration with existing email:

409 Conflict

Invalid login:

401 Unauthorized

Missing/invalid access token:

401 Unauthorized

Expired token:

401 Unauthorized

Inactive user:

403 Forbidden

Invalid request:

422 Unprocessable Entity

Do not reveal whether an email exists during authentication failures in a way that creates unnecessary account enumeration risk.

Do not expose stack traces to clients in production mode.

==================================================
SECURITY REQUIREMENTS
==================================================

Implement:

- password hashing
- JWT validation
- token expiration
- refresh-token revocation
- environment-based secrets
- input validation
- normalized email
- database constraints
- no plaintext passwords
- no sensitive logging
- user authentication dependency

Do not put JWT secret in source code.

==================================================
TESTING
==================================================

Create tests for:

1. Health endpoint still works.

2. Register user successfully.

3. Duplicate email rejected.

4. Password is stored as a hash.

5. Login succeeds.

6. Login fails with incorrect password.

7. /auth/me works with valid access token.

8. /auth/me fails without token.

9. /auth/me fails with invalid token.

10. Refresh token creates a new access token.

11. Logout revokes refresh token.

12. Revoked refresh token cannot be reused.

13. Expired token is rejected.

Use a test database or isolated test database strategy.

Do not run destructive tests against the development database.

==================================================
DOCKER
==================================================

Update docker-compose.yml if required.

Backend and PostgreSQL must work together.

Do not expose PostgreSQL publicly unless required for local development.

Use environment variables.

Add PostgreSQL healthcheck.

==================================================
ENVIRONMENT
==================================================

Update .env.example with:

APP_NAME=FinPilot
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+asyncpg://...

SECRET_KEY=replace_this_in_real_environment

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

Never commit the real .env file.

==================================================
DATABASE DESIGN FOR FUTURE STAGES
==================================================

Do NOT create future tables yet.

However, design User relationships so future tables can reference:

users.id

Future tables will include:

accounts
transactions
documents
conversations
messages
budgets
goals
recurring_payments
audit_logs

Every user-owned resource will eventually contain:

user_id

This is critical for tenant/data isolation.

==================================================
CODE QUALITY
==================================================

Follow these principles:

- modular monolith
- separation of routes/services/repositories/models
- type hints
- async database access
- dependency injection
- Pydantic validation
- no business logic inside route handlers
- no database queries inside schemas
- no hardcoded secrets
- no unnecessary abstraction
- no microservices

Do not implement any Stage 3+ functionality.

==================================================
FINAL VERIFICATION
==================================================

After implementation:

1. Show complete directory tree.

2. Explain each new file.

3. Show Alembic migration.

4. Show how to start PostgreSQL.

5. Show how to run migrations.

6. Show how to start FastAPI.

7. Demonstrate:

POST /api/v1/auth/register

POST /api/v1/auth/login

GET /api/v1/auth/me

POST /api/v1/auth/refresh

POST /api/v1/auth/logout

8. Run all tests.

9. Confirm Stage 1 health endpoint still works.

10. Report any issues.


***very important thing to do hardCode anything***
Do not move to Stage 3.