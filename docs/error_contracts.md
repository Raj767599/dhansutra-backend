## Error contracts (frontend-facing)

This backend uses a consistent top-level error envelope:

```json
{
  "error": {
    "code": "some_code",
    "message": "Human-readable message",
    "details": { "optional": "object" }
  }
}
```

Errors come from:
- request validation (FastAPI/Pydantic) → `422`
- auth failures → `401`
- permission/business rules → `403`/`422`
- not found / isolation-safe not found → `404`
- conflicts → `409`

---

### Validation errors (422)

Backend returns:
- `error.code`: `"validation_error"`
- `error.message`: `"Validation failed"`
- `error.details.errors`: the standard FastAPI validation list

Example:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "errors": [
        {
          "type": "string_too_short",
          "loc": ["body", "password"],
          "msg": "String should have at least 8 characters",
          "input": "short"
        }
      ]
    }
  }
}
```

---

### Auth errors (401)

Typical cases:
- missing `Authorization` header
- invalid/expired access token
- revoked access token (token version mismatch)
- invalid credentials on login
- invalid refresh token on refresh

Example: missing/invalid token

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Unauthorized"
  }
}
```

Example: bad credentials

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid credentials"
  }
}
```

---

### Not-found errors (404)

Used both for true not-found and for **user isolation** (to avoid leaking existence).

Example:

```json
{
  "error": {
    "code": "not_found",
    "message": "Account not found"
  }
}
```

---

### Business rule errors (examples)

#### Archived account cannot accept new transactions (403)

```json
{
  "error": {
    "code": "forbidden",
    "message": "Archived account cannot accept new transactions"
  }
}
```

#### Category required for income/expense (422)

```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "category_id": "Required for income/expense"
    }
  }
}
```

#### Category type mismatch (422)

```json
{
  "error": {
    "code": "validation_error",
    "message": "Category type mismatch",
    "details": {
      "category_id": "Must be expense"
    }
  }
}
```

#### Transfer requires destination account (422)

```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "destination_account_id": "Required for transfer"
    }
  }
}
```

#### Transfer currency mismatch (422)

```json
{
  "error": {
    "code": "validation_error",
    "message": "Transfer currency mismatch",
    "details": {
      "currency": "Accounts must match"
    }
  }
}
```

#### Insufficient funds (422)

```json
{
  "error": {
    "code": "validation_error",
    "message": "Insufficient funds",
    "details": {
      "account_id": "0b8a2c7a-2b79-4d4a-9c4a-0a2d2e8b9c0d"
    }
  }
}
```

---

### Conflict errors (409)

Example: email already registered

```json
{
  "error": {
    "code": "conflict",
    "message": "Email already registered"
  }
}
```

