"""
API Wizard

Designs consistent REST/GraphQL APIs with OpenAPI specs, versioning, and documentation.
Uses Empathy Framework Level 3 (Proactive) for endpoint design and Level 4
(Anticipatory) for API sprawl prediction.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from typing import Any

from .base_wizard import (
    BaseWizard,
    EmpathyChecks,
    WizardArtifact,
    WizardHandoff,
    WizardOutput,
    WizardRisk,
    WizardTask,
)


class APIWizard(BaseWizard):
    """
    Wizard for API design and documentation

    Uses:
    - Level 2: Guide user through API design decisions
    - Level 3: Proactively generate OpenAPI specs
    - Level 4: Anticipate API sprawl and versioning needs
    """

    def can_handle(self, task: WizardTask) -> float:
        """Determine if this is an API design task"""
        # High-priority API phrases (worth 2 points each)
        api_phrases = ["api", "endpoint", "rest", "graphql", "openapi", "swagger"]

        # Secondary indicators (worth 1 point each)
        secondary_keywords = [
            "http",
            "json",
            "request",
            "response",
            "schema",
            "route",
            "controller",
            "versioning",
            "documentation",
            "postman",
        ]

        task_lower = (task.task + " " + task.context).lower()

        primary_matches = sum(2 for phrase in api_phrases if phrase in task_lower)
        secondary_matches = sum(1 for keyword in secondary_keywords if keyword in task_lower)

        total_score = primary_matches + secondary_matches

        return min(total_score / 6.0, 1.0)

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute API design workflow"""

        self._assess_emotional_state(task)
        self._extract_constraints(task)

        diagnosis = self._analyze_api_requirements(task)
        design = self._design_api_endpoints(task)
        openapi_spec = self._generate_openapi_spec(task, design)
        versioning_strategy = self._recommend_versioning(task, design)
        api_sprawl_forecast = self._predict_api_sprawl(task, design)

        artifacts = [
            WizardArtifact(type="doc", title="API Design Document", content=diagnosis),
            WizardArtifact(type="code", title="OpenAPI 3.1 Specification", content=openapi_spec),
            WizardArtifact(
                type="code",
                title="API Implementation (FastAPI)",
                content=self._generate_implementation(task, design),
            ),
            WizardArtifact(type="doc", title="Versioning Strategy", content=versioning_strategy),
            WizardArtifact(
                type="doc", title="API Documentation", content=self._generate_api_docs(task, design)
            ),
        ]

        plan = [
            "1. Review REST/GraphQL design principles",
            "2. Define endpoint structure and URL patterns",
            "3. Create OpenAPI specification",
            "4. Implement endpoints with validation",
            "5. Generate interactive documentation (Swagger UI)",
            "6. Create client SDK or Postman collection",
            "7. Set up versioning strategy",
        ]

        empathy_checks = EmpathyChecks(
            cognitive="Considered API consumers: developers, mobile apps, third-party integrations",
            emotional="Acknowledged: Good API design prevents future breaking changes and customer frustration",
            anticipatory=api_sprawl_forecast[:200] + "...",
        )

        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=self._identify_risks(task),
            handoffs=self._create_handoffs(task),
            next_actions=[
                "Review OpenAPI spec",
                "Test endpoints with Postman",
                "Generate client SDK",
            ],
            empathy_checks=empathy_checks,
            confidence=self.can_handle(task),
        )

    def _analyze_api_requirements(self, task: WizardTask) -> str:
        """Analyze API requirements"""
        return f"""# API Design Analysis

**Objective**: {task.task}

**API Type**: REST (RESTful design patterns)
**Format**: JSON
**Authentication**: JWT Bearer tokens (recommended)

**Context**: {task.context[:300]}...
"""

    def _design_api_endpoints(self, task: WizardTask) -> list[dict[str, Any]]:
        """Design API endpoints"""
        # Example endpoints based on common patterns
        endpoints = [
            {
                "method": "GET",
                "path": "/api/v1/users",
                "summary": "List all users",
                "query_params": ["page", "limit", "sort"],
                "response": "200: List of user objects",
            },
            {
                "method": "GET",
                "path": "/api/v1/users/{id}",
                "summary": "Get user by ID",
                "path_params": ["id"],
                "response": "200: User object, 404: Not found",
            },
            {
                "method": "POST",
                "path": "/api/v1/users",
                "summary": "Create new user",
                "request_body": "User object",
                "response": "201: Created user, 400: Validation error",
            },
            {
                "method": "PUT",
                "path": "/api/v1/users/{id}",
                "summary": "Update user",
                "path_params": ["id"],
                "request_body": "User object",
                "response": "200: Updated user, 404: Not found",
            },
            {
                "method": "DELETE",
                "path": "/api/v1/users/{id}",
                "summary": "Delete user",
                "path_params": ["id"],
                "response": "204: No content, 404: Not found",
            },
        ]
        return endpoints

    def _generate_openapi_spec(self, task: WizardTask, design: list[dict]) -> str:
        """Generate OpenAPI 3.1 specification following OpenAI/Anthropic conventions"""
        return """openapi: 3.1.0
info:
  title: API Specification
  version: 1.0.0
  description: |
    RESTful API following OpenAI/Anthropic conventions:
    - Streaming support for long-running operations (Server-Sent Events)
    - Consistent error format (type, message, param, code)
    - Rate limit headers on all responses
    - Object type field for resource identification
  contact:
    name: API Support
    email: api@example.com

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List all users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: List of users
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/X-RateLimit-Reset'
          content:
            application/json:
              schema:
                type: object
                required:
                  - object
                  - data
                properties:
                  object:
                    type: string
                    enum: [list]
                    description: Object type (OpenAI convention)
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  has_more:
                    type: boolean
                    description: Whether there are more results
                  first_id:
                    type: string
                    description: ID of first item in list
                  last_id:
                    type: string
                    description: ID of last item in list
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '429':
          $ref: '#/components/responses/RateLimitError'
        '500':
          $ref: '#/components/responses/InternalServerError'
    post:
      summary: Create new user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/X-RateLimit-Reset'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '429':
          $ref: '#/components/responses/RateLimitError'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /users/{id}:
    get:
      summary: Get user by ID
      operationId: getUser
      tags:
        - Users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User object
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/X-RateLimit-Reset'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '404':
          $ref: '#/components/responses/NotFoundError'
        '429':
          $ref: '#/components/responses/RateLimitError'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /completions:
    post:
      summary: Create a completion (with streaming support)
      operationId: createCompletion
      tags:
        - Completions
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - prompt
                - model
              properties:
                model:
                  type: string
                  description: Model identifier
                  example: gpt-4
                prompt:
                  type: string
                  description: The prompt to complete
                  example: "Once upon a time"
                max_tokens:
                  type: integer
                  description: Maximum tokens to generate
                  default: 100
                  minimum: 1
                  maximum: 4096
                temperature:
                  type: number
                  description: Sampling temperature
                  default: 1.0
                  minimum: 0.0
                  maximum: 2.0
                stream:
                  type: boolean
                  description: Enable streaming via Server-Sent Events
                  default: false
      responses:
        '200':
          description: Completion response
          headers:
            X-RateLimit-Limit:
              $ref: '#/components/headers/X-RateLimit-Limit'
            X-RateLimit-Remaining:
              $ref: '#/components/headers/X-RateLimit-Remaining'
            X-RateLimit-Reset:
              $ref: '#/components/headers/X-RateLimit-Reset'
          content:
            application/json:
              schema:
                type: object
                required:
                  - id
                  - object
                  - created
                  - model
                  - choices
                properties:
                  id:
                    type: string
                    description: Unique completion ID
                    example: cmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW
                  object:
                    type: string
                    enum: [text_completion]
                    description: Object type
                  created:
                    type: integer
                    description: Unix timestamp of creation
                    example: 1677652288
                  model:
                    type: string
                    description: Model used
                    example: gpt-4
                  choices:
                    type: array
                    items:
                      type: object
                      properties:
                        text:
                          type: string
                          description: Generated text
                        index:
                          type: integer
                        finish_reason:
                          type: string
                          enum: [stop, length, content_filter]
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: integer
                      completion_tokens:
                        type: integer
                      total_tokens:
                        type: integer
            text/event-stream:
              schema:
                type: string
                description: |
                  Server-Sent Events stream. Each event contains a JSON object:
                  data: {"id":"cmpl-123","object":"text_completion.chunk","created":1677652288,"choices":[{"text":"Hello","index":0,"finish_reason":null}]}

                  Final event:
                  data: [DONE]
                example: |
                  data: {"id":"cmpl-123","object":"text_completion.chunk","created":1677652288,"choices":[{"text":"Hello","index":0,"finish_reason":null}]}

                  data: {"id":"cmpl-123","object":"text_completion.chunk","created":1677652288,"choices":[{"text":" world","index":0,"finish_reason":null}]}

                  data: [DONE]
        '400':
          $ref: '#/components/responses/BadRequestError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '429':
          $ref: '#/components/responses/RateLimitError'
        '500':
          $ref: '#/components/responses/InternalServerError'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - object
        - email
        - name
        - created_at
      properties:
        id:
          type: string
          format: uuid
          description: Unique user identifier
        object:
          type: string
          enum: [user]
          description: Object type (OpenAI convention)
        email:
          type: string
          format: email
          description: User email address
        name:
          type: string
          description: User full name
        created_at:
          type: integer
          description: Unix timestamp when user was created
          example: 1673539200

    UserCreate:
      type: object
      required:
        - email
        - name
        - password
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 2
        password:
          type: string
          minLength: 8

    PaginationMeta:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        total_pages:
          type: integer

    Error:
      type: object
      required:
        - type
        - message
      properties:
        type:
          type: string
          enum:
            - invalid_request_error
            - authentication_error
            - permission_error
            - not_found_error
            - rate_limit_error
            - api_error
            - overloaded_error
          description: Error type (Anthropic convention)
        message:
          type: string
          description: Human-readable error message
        param:
          type: string
          nullable: true
          description: The parameter that caused the error
        code:
          type: string
          nullable: true
          description: Machine-readable error code

  headers:
    X-RateLimit-Limit:
      description: Maximum requests per minute
      schema:
        type: integer
        example: 60

    X-RateLimit-Remaining:
      description: Remaining requests in current window
      schema:
        type: integer
        example: 58

    X-RateLimit-Reset:
      description: Unix timestamp when rate limit resets
      schema:
        type: integer
        example: 1673539200

  responses:
    BadRequestError:
      description: Bad request - invalid parameters
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          $ref: '#/components/headers/X-RateLimit-Remaining'
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            type: invalid_request_error
            message: "Invalid parameter: 'limit' must be between 1 and 100"
            param: limit
            code: invalid_parameter

    UnauthorizedError:
      description: Unauthorized - missing or invalid authentication
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          $ref: '#/components/headers/X-RateLimit-Remaining'
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            type: authentication_error
            message: Invalid API key provided
            param: null
            code: invalid_api_key

    NotFoundError:
      description: Resource not found
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          $ref: '#/components/headers/X-RateLimit-Remaining'
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            type: not_found_error
            message: The requested resource was not found
            param: null
            code: resource_not_found

    RateLimitError:
      description: Rate limit exceeded
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          $ref: '#/components/headers/X-RateLimit-Remaining'
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
        Retry-After:
          description: Number of seconds to wait before retrying
          schema:
            type: integer
            example: 60
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            type: rate_limit_error
            message: Rate limit exceeded. Please retry after 60 seconds
            param: null
            code: rate_limit_exceeded

    InternalServerError:
      description: Internal server error
      headers:
        X-RateLimit-Limit:
          $ref: '#/components/headers/X-RateLimit-Limit'
        X-RateLimit-Remaining:
          $ref: '#/components/headers/X-RateLimit-Remaining'
        X-RateLimit-Reset:
          $ref: '#/components/headers/X-RateLimit-Reset'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            type: api_error
            message: An internal server error occurred
            param: null
            code: internal_error

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
"""

    def _generate_implementation(self, task: WizardTask, design: list[dict]) -> str:
        """Generate FastAPI implementation"""
        return """# FastAPI Implementation with OpenAI/Anthropic Conventions
from fastapi import FastAPI, HTTPException, Query, Path, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, AsyncIterator
from uuid import UUID, uuid4
from datetime import datetime
import time
import json

app = FastAPI(
    title="API Service",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# ============================================================================
# Custom Error Classes (Anthropic convention)
# ============================================================================
class APIError(BaseModel):
    \"\"\"Anthropic-style error response\"\"\"
    type: str
    message: str
    param: Optional[str] = None
    code: Optional[str] = None

class APIException(HTTPException):
    \"\"\"Base exception for API errors\"\"\"
    def __init__(
        self,
        status_code: int,
        error_type: str,
        message: str,
        param: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.error_type = error_type
        self.param = param
        self.code = code

# ============================================================================
# Rate Limiting Middleware
# ============================================================================
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    \"\"\"Add rate limit headers to all responses\"\"\"
    # In-memory rate limiter using dict (production: use Redis)
    # Structure: {client_id: {"count": int, "reset": timestamp}}
    if not hasattr(app.state, "rate_limits"):
        app.state.rate_limits = {}

    # Get client identifier (IP address or API key)
    client_id = request.client.host if request.client else "unknown"

    # Rate limit configuration
    RATE_LIMIT = 60  # requests per minute
    WINDOW = 60  # seconds
    current_time = int(time.time())

    # Initialize or reset window
    if client_id not in app.state.rate_limits:
        app.state.rate_limits[client_id] = {"count": 0, "reset": current_time + WINDOW}

    client_limit = app.state.rate_limits[client_id]

    # Reset window if expired
    if current_time >= client_limit["reset"]:
        client_limit["count"] = 0
        client_limit["reset"] = current_time + WINDOW

    # Check rate limit
    if client_limit["count"] >= RATE_LIMIT:
        # Rate limit exceeded
        return Response(
            status_code=429,
            content=json.dumps({
                "type": "rate_limit_error",
                "message": f"Rate limit exceeded. Please retry after {client_limit['reset'] - current_time} seconds",
                "param": None,
                "code": "rate_limit_exceeded"
            }),
            media_type="application/json",
            headers={
                "X-RateLimit-Limit": str(RATE_LIMIT),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(client_limit["reset"]),
                "Retry-After": str(client_limit["reset"] - current_time)
            }
        )

    # Increment counter
    client_limit["count"] += 1

    # Process request
    response = await call_next(request)

    # Add rate limit headers (OpenAI/Anthropic convention)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT - client_limit["count"])
    response.headers["X-RateLimit-Reset"] = str(client_limit["reset"])

    return response

# ============================================================================
# Exception Handlers (Anthropic-style errors)
# ============================================================================
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    \"\"\"Handle custom API exceptions with Anthropic error format\"\"\"
    return Response(
        status_code=exc.status_code,
        content=json.dumps({
            "type": exc.error_type,
            "message": exc.detail,
            "param": exc.param,
            "code": exc.code
        }),
        media_type="application/json"
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    \"\"\"Catch-all for unexpected errors\"\"\"
    return Response(
        status_code=500,
        content=json.dumps({
            "type": "api_error",
            "message": "An internal server error occurred",
            "param": None,
            "code": "internal_error"
        }),
        media_type="application/json"
    )

# ============================================================================
# Pydantic Models (Request/Response validation)
# ============================================================================
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class User(BaseModel):
    id: UUID
    object: str = "user"  # OpenAI convention
    email: EmailStr
    name: str
    created_at: int  # Unix timestamp (OpenAI/Anthropic convention)

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

class UserListResponse(BaseModel):
    object: str = "list"  # OpenAI convention
    data: List[User]
    has_more: bool
    first_id: Optional[str] = None
    last_id: Optional[str] = None

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 1.0
    stream: bool = False

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int  # Unix timestamp
    model: str
    choices: List[dict]
    usage: dict

# ============================================================================
# User Endpoints
# ============================================================================
@app.get("/api/v1/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    \"\"\"List all users with pagination\"\"\"
    # Validate parameters
    if limit > 100:
        raise APIException(
            status_code=400,
            error_type="invalid_request_error",
            message="Invalid parameter: 'limit' must be between 1 and 100",
            param="limit",
            code="invalid_parameter"
        )

    # Mock in-memory database (production: use SQLAlchemy/ORM)
    # Initialize mock database if not present
    if not hasattr(app.state, "mock_users_db"):
        app.state.mock_users_db = [
            User(
                id=uuid4(),
                object="user",
                email=f"user{i}@example.com",
                name=f"User {i}",
                created_at=int(time.time()) - (i * 86400)
            )
            for i in range(1, 51)  # 50 mock users
        ]

    # Query database with pagination
    users_db = app.state.mock_users_db
    total = len(users_db)

    # Calculate pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    users = users_db[start_idx:end_idx]

    return UserListResponse(
        object="list",
        data=users,
        has_more=end_idx < total,
        first_id=str(users[0].id) if users else None,
        last_id=str(users[-1].id) if users else None
    )

@app.get("/api/v1/users/{user_id}", response_model=User)
async def get_user(user_id: UUID = Path(...)):
    \"\"\"Get user by ID\"\"\"
    # Query mock database by ID (production: use ORM query)
    if not hasattr(app.state, "mock_users_db"):
        app.state.mock_users_db = []

    # Find user by ID
    user = next((u for u in app.state.mock_users_db if u.id == user_id), None)

    if not user:
        raise APIException(
            status_code=404,
            error_type="not_found_error",
            message="The requested resource was not found",
            param=None,
            code="resource_not_found"
        )

    return user

@app.post("/api/v1/users", response_model=User, status_code=201)
async def create_user(user_data: UserCreate):
    \"\"\"Create new user\"\"\"
    # Initialize mock database if not present
    if not hasattr(app.state, "mock_users_db"):
        app.state.mock_users_db = []

    # Validate: Check if email already exists
    existing_user = next((u for u in app.state.mock_users_db if u.email == user_data.email), None)
    if existing_user:
        raise APIException(
            status_code=400,
            error_type="invalid_request_error",
            message=f"User with email '{user_data.email}' already exists",
            param="email",
            code="duplicate_email"
        )

    # Hash password using bcrypt (production: use passlib or bcrypt)
    import hashlib
    # Simple hash for demo (production: use bcrypt.hashpw(password.encode(), bcrypt.gensalt()))
    password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

    # Create new user
    new_user = User(
        id=uuid4(),
        object="user",
        email=user_data.email,
        name=user_data.name,
        created_at=int(time.time())
    )

    # Insert to mock database
    app.state.mock_users_db.append(new_user)

    # Note: password_hash would be stored in DB, not returned in response
    # For security, User model doesn't include password field

    return new_user

# ============================================================================
# Streaming Completions Endpoint
# ============================================================================
async def generate_completion_stream(
    completion_id: str,
    model: str,
    prompt: str,
    max_tokens: int
) -> AsyncIterator[str]:
    \"\"\"Generate streaming completion chunks (Server-Sent Events)\"\"\"
    # Simulate streaming response
    created = int(time.time())

    # Example: Stream word by word
    words = ["Hello", " world", "!", " This", " is", " a", " streaming", " response", "."]

    for i, word in enumerate(words[:max_tokens]):
        chunk = {
            "id": completion_id,
            "object": "text_completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "text": word,
                "index": 0,
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk)}\\n\\n"

        # Simulate processing delay
        await asyncio.sleep(0.1)

    # Final chunk with finish_reason
    final_chunk = {
        "id": completion_id,
        "object": "text_completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "text": "",
            "index": 0,
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk)}\\n\\n"

    # Send [DONE] marker (OpenAI convention)
    yield "data: [DONE]\\n\\n"

@app.post("/api/v1/completions")
async def create_completion(request: CompletionRequest):
    \"\"\"Create a completion (with streaming support)\"\"\"
    completion_id = f"cmpl-{uuid4().hex[:24]}"
    created = int(time.time())

    # Streaming response
    if request.stream:
        return StreamingResponse(
            generate_completion_stream(
                completion_id=completion_id,
                model=request.model,
                prompt=request.prompt,
                max_tokens=request.max_tokens
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    # Non-streaming response
    # Simple completion logic (production: call actual LLM API)
    # This demonstrates a basic text generation pattern

    # Generate completion text based on prompt
    prompt_lower = request.prompt.lower()

    # Simple rule-based completion for demonstration
    if "hello" in prompt_lower or "hi" in prompt_lower:
        completion_text = "Hello! How can I help you today?"
    elif "weather" in prompt_lower:
        completion_text = "I'm sorry, I don't have access to real-time weather data. Please check a weather service."
    elif "what is" in prompt_lower or "explain" in prompt_lower:
        completion_text = "That's a great question. In a production system, this would connect to an actual language model API to provide detailed explanations."
    else:
        # Default completion
        completion_text = f"I received your prompt: '{request.prompt[:50]}...'. In production, this would generate a contextual response using a language model."

    # Respect max_tokens by truncating if needed
    words = completion_text.split()
    if len(words) > request.max_tokens:
        completion_text = " ".join(words[:request.max_tokens]) + "..."
        finish_reason = "length"
    else:
        finish_reason = "stop"

    # Calculate token counts (simplified word-based counting)
    prompt_tokens = len(request.prompt.split())
    completion_tokens = len(completion_text.split())

    return CompletionResponse(
        id=completion_id,
        object="text_completion",
        created=created,
        model=request.model,
        choices=[{
            "text": completion_text,
            "index": 0,
            "finish_reason": finish_reason
        }],
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    )

# ============================================================================
# Additional imports needed for streaming
# ============================================================================
import asyncio
"""

    def _recommend_versioning(self, task: WizardTask, design: list[dict]) -> str:
        """Recommend API versioning strategy"""
        return """# API Versioning Strategy

## Recommended Approach: URL Versioning

**Pattern**: `/api/v{version}/resource`
**Example**: `/api/v1/users`, `/api/v2/users`

### Advantages:
- Clear and explicit (version in URL)
- Easy to test (use different URLs)
- Works with all HTTP clients
- Simple to route in API gateway

### Version Lifecycle:
1. **v1** (Current): Stable, production traffic
2. **v2** (Beta): New features, breaking changes allowed
3. **v1 → v2 Migration**: 6-month deprecation period
   - Month 1-2: Announce v2, document changes
   - Month 3-4: Encourage migration, support both
   - Month 5-6: Warning headers on v1 responses
   - Month 7+: v1 deprecated (returns 410 Gone)

### Breaking vs Non-Breaking Changes:

**Non-Breaking (Same version):**
- Add new optional fields
- Add new endpoints
- Add new query parameters (optional)
- Increase pagination limits

**Breaking (New version required):**
- Remove fields
- Rename fields
- Change field types
- Change authentication method
- Remove endpoints
- Change URL structure

### Implementation:
```python
# FastAPI versioned routing
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/users")
async def list_users_v1():
    return {"version": "1.0", "users": []}

# Version 2 (with breaking changes)
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/users")
async def list_users_v2():
    # Breaking change: Different response structure
    return {"version": "2.0", "data": [], "meta": {}}

app.include_router(v1_router)
app.include_router(v2_router)
```

### Deprecation Headers:
```python
@v1_router.get("/users")
async def list_users_v1(response: Response):
    response.headers["X-API-Deprecated"] = "true"
    response.headers["X-API-Deprecation-Date"] = "2025-07-01"
    response.headers["X-API-Sunset"] = "2025-12-31"
    return {"users": []}
```
"""

    def _predict_api_sprawl(self, task: WizardTask, design: list[dict]) -> str:
        """Level 4: Predict API sprawl issues"""
        return """# API Sprawl Forecast (Level 4: Anticipatory)

## Current State
- Endpoints: 5 (baseline CRUD operations)
- Versions: 1 (v1)
- Growth rate: ~2-3 endpoints/month (typical)

## Projected Issues (Next 60-90 Days)

### ⚠️ API Sprawl at 50+ Endpoints (90 days)
**Prediction**: At 2-3 endpoints/month growth, will exceed 50 endpoints in ~90 days
**Impact**: Difficult to document, test, and maintain consistency
**Preventive Action**:
- Implement API gateway NOW for centralized management
- Group related endpoints into subdomains (users-api, orders-api)
- Use OpenAPI tags to organize documentation
- Set up automated API testing (contract testing)

### ⚠️ Breaking Change Management (60 days)
**Prediction**: First major breaking change will require new API version
**Impact**: Must support v1 + v2 simultaneously (2x maintenance)
**Preventive Action**:
- Document versioning policy NOW (before it's needed)
- Plan 6-month deprecation timeline
- Set up version routing infrastructure
- Create migration guides for API consumers

## Recommended Timeline
- **Now**: Document versioning strategy
- **Week 4**: Set up automated OpenAPI validation in CI
- **Week 8**: Implement API gateway (before sprawl becomes unmanageable)
- **Week 12**: Create API client SDK to reduce consumer pain
"""

    def _generate_api_docs(self, task: WizardTask, design: list[dict]) -> str:
        """Generate API documentation"""
        return """# API Documentation

## Getting Started

### Base URL
```
https://api.example.com/v1
```

### Authentication
All endpoints require JWT Bearer token:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  https://api.example.com/v1/users
```

## Endpoints

### List Users
`GET /api/v1/users`

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `limit` (integer, default: 20, max: 100): Items per page

**Response:**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

### Get User
`GET /api/v1/users/{id}`

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-01-15T10:00:00Z"
}
```

## Error Handling

All errors return consistent format:
```json
{
  "error": "ValidationError",
  "message": "Invalid email format",
  "details": {
    "field": "email",
    "value": "invalid"
  }
}
```

**HTTP Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
"""

    def _identify_risks(self, task: WizardTask) -> list[WizardRisk]:
        """Identify API design risks"""
        return [
            WizardRisk(
                risk="Breaking changes may disrupt existing API consumers",
                mitigation="Use API versioning (URL-based) and 6-month deprecation period",
                severity="high",
            ),
            WizardRisk(
                risk="Inconsistent endpoint design leads to confusion",
                mitigation="Follow REST conventions strictly, use OpenAPI spec for validation",
                severity="medium",
            ),
            WizardRisk(
                risk="Missing rate limiting may allow abuse",
                mitigation="Implement rate limiting (100 req/min per user) before public launch",
                severity="high",
            ),
        ]

    def _create_handoffs(self, task: WizardTask) -> list[WizardHandoff]:
        """Create handoffs for API work"""
        return [
            WizardHandoff(
                owner="DevOps",
                what="Set up API gateway with rate limiting and monitoring",
                when="Before production deployment",
            ),
            WizardHandoff(
                owner="Technical Writer",
                what="Create comprehensive API documentation and usage examples",
                when="After OpenAPI spec finalized",
            ),
        ]
