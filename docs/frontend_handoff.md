## Frontend integration handoff (DhanSutra backend)

### Base URLs

- **Base URL (local dev)**: `http://localhost:8000`
- **OpenAPI / Swagger UI**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Demo credentials (seed data)

After running `make seed`:

- **Email**: `demo@finance.local`
- **Password**: `DemoPassword1!`

### Auth flow (step-by-step)

#### 1) Register (first-time user)
- **Endpoint**: `POST /api/v1/auth/register`
- **Body**: `{ email, password, full_name? }`
- **Returns**: user profile payload (no tokens)

#### 2) Login (get tokens)
- **Endpoint**: `POST /api/v1/auth/login`
- **Body**: `{ email, password }`
- **Returns**: `{ access_token, refresh_token, token_type }`

#### 3) Use access token on API calls
- Add header: `Authorization: Bearer <access_token>`
- Most non-auth endpoints require this header.

#### 4) Refresh access token (rotate refresh token)
- **Endpoint**: `POST /api/v1/auth/refresh`
- **Body**: `{ refresh_token }`
- **Returns**: a **new** `{ access_token, refresh_token }`
- **Important**: refresh is **rotating**. Replace the stored refresh token with the new one.

#### 5) Logout (revoke refresh token)
- **Endpoint**: `POST /api/v1/auth/logout`
- **Body**: `{ refresh_token }`
- **Returns**: `204 No Content`
- Logout is idempotent for already-revoked/unknown refresh tokens.

#### 6) Current user
- **Endpoint**: `GET /api/v1/auth/me` (or `GET /api/v1/users/me`)
- **Auth required**: Yes (access token)

---

### Pagination contract (used across list endpoints)

List endpoints return:

```json
{
  "items": [ /* array of DTOs */ ],
  "meta": { "limit": 20, "offset": 0, "total": 123 }
}
```

- **limit**: max items returned
- **offset**: starting index
- **total**: total matches for the filter (for infinite scroll / paging UI)

Endpoints using this contract:
- `GET /api/v1/accounts`
- `GET /api/v1/categories`
- `GET /api/v1/transactions`
- `GET /api/v1/budgets`
- `GET /api/v1/goals`

---

### Common status codes

- **200**: success (read/update)
- **201**: created
- **204**: success, no response body (delete/logout/change-password)
- **401**: unauthorized (missing/invalid token, bad credentials, revoked token)
- **403**: forbidden (business/security rule, e.g. archived account restrictions)
- **404**: not found (also used to avoid leaking existence across users)
- **409**: conflict (e.g., email already registered)
- **422**: validation failed (field validation / schema errors)
- **500**: internal server error

---

## Endpoints by screen

### Auth screen(s)

- **Register**
  - **Endpoint**: `POST /api/v1/auth/register`
  - **Auth**: No
  - **Response shape**: `{ id, email, full_name, onboarding_completed }`
  - **UI notes**: This does not return tokens; login after register.

- **Login**
  - **Endpoint**: `POST /api/v1/auth/login`
  - **Auth**: No
  - **Response shape**: `{ access_token, refresh_token, token_type }`

- **Refresh**
  - **Endpoint**: `POST /api/v1/auth/refresh`
  - **Auth**: No (uses refresh token in body)
  - **Response shape**: `{ access_token, refresh_token, token_type }`
  - **UI notes**: Replace stored refresh token (rotation).

- **Logout**
  - **Endpoint**: `POST /api/v1/auth/logout`
  - **Auth**: No (uses refresh token in body)
  - **Response**: `204`

- **Me (token check)**
  - **Endpoint**: `GET /api/v1/auth/me`
  - **Auth**: Yes
  - **Response shape**: `{ id, email, full_name, onboarding_completed }`

### Dashboard screen

- **Summary**
  - **Endpoint**: `GET /api/v1/dashboard/summary`
  - **Auth**: Yes
  - **Response shape**:
    - `total_balance`
    - `total_income_current_month`
    - `total_expense_current_month`
    - `total_savings`
    - `budget_usage_summary[]`
    - `recent_transactions[]`
    - `active_goals[]`
    - `top_spending_categories[]`
    - `account_overview[]`
  - **UI notes**: use `recent_transactions` for the “latest activity” list; use `top_spending_categories` for charts.

### Accounts screen

- **List**
  - **Endpoint**: `GET /api/v1/accounts`
  - **Auth**: Yes
  - **Query params**: `limit`, `offset`
  - **Response shape**: `Page[AccountResponse]`

- **Create**
  - **Endpoint**: `POST /api/v1/accounts`
  - **Auth**: Yes
  - **Response shape**: `AccountResponse`

- **Details**
  - **Endpoint**: `GET /api/v1/accounts/{account_id}`
  - **Auth**: Yes

- **Update**
  - **Endpoint**: `PATCH /api/v1/accounts/{account_id}`
  - **Auth**: Yes

- **Delete**
  - **Endpoint**: `DELETE /api/v1/accounts/{account_id}`
  - **Auth**: Yes
  - **Response**: `204`

### Categories screen

- **List**
  - **Endpoint**: `GET /api/v1/categories`
  - **Auth**: Yes
  - **Query params**: `type` (optional: `income|expense`), `limit`, `offset`
  - **Response shape**: `Page[CategoryResponse]`
  - **UI notes**: includes system defaults + user categories.

- **Create**
  - **Endpoint**: `POST /api/v1/categories`
  - **Auth**: Yes

- **Details**
  - **Endpoint**: `GET /api/v1/categories/{category_id}`
  - **Auth**: Yes

- **Update**
  - **Endpoint**: `PATCH /api/v1/categories/{category_id}`
  - **Auth**: Yes

- **Delete**
  - **Endpoint**: `DELETE /api/v1/categories/{category_id}`
  - **Auth**: Yes
  - **Response**: `204`

### Transactions screen

- **List (filters + search)**
  - **Endpoint**: `GET /api/v1/transactions`
  - **Auth**: Yes
  - **Query params**:
    - `q` (searches `note` and `merchant`)
    - `account_id`
    - `category_id`
    - `type` (`income|expense|transfer`)
    - `start`, `end` (ISO datetimes)
    - `sort` (`occurred_at_desc|occurred_at_asc`)
    - `limit`, `offset`
  - **Response shape**: `Page[TransactionListItem]`

- **Create**
  - **Endpoint**: `POST /api/v1/transactions`
  - **Auth**: Yes
  - **Response shape**: `TransactionResponse`

- **Details**
  - **Endpoint**: `GET /api/v1/transactions/{transaction_id}`
  - **Auth**: Yes

- **Update**
  - **Endpoint**: `PATCH /api/v1/transactions/{transaction_id}`
  - **Auth**: Yes

- **Delete**
  - **Endpoint**: `DELETE /api/v1/transactions/{transaction_id}`
  - **Auth**: Yes
  - **Response**: `204`

- **Overview summary**
  - **Endpoint**: `GET /api/v1/transactions/summary/overview`
  - **Auth**: Yes
  - **Query params**: `start`, `end` (optional)
  - **Response shape**: `{ total_income, total_expense, total_transfer_out, total_transfer_in, net_cashflow, start, end }`

### Budgets screen

- **List**
  - **Endpoint**: `GET /api/v1/budgets`
  - **Auth**: Yes
  - **Query params**: `limit`, `offset`
  - **Response shape**: `Page[BudgetResponse]` (includes calculated `spent/remaining/usage_pct/is_over_budget`)

- **Create**
  - **Endpoint**: `POST /api/v1/budgets`
  - **Auth**: Yes

- **Details**
  - **Endpoint**: `GET /api/v1/budgets/{budget_id}`
  - **Auth**: Yes

- **Update**
  - **Endpoint**: `PATCH /api/v1/budgets/{budget_id}`
  - **Auth**: Yes

- **Delete**
  - **Endpoint**: `DELETE /api/v1/budgets/{budget_id}`
  - **Auth**: Yes
  - **Response**: `204`

### Goals screen

- **List**
  - **Endpoint**: `GET /api/v1/goals`
  - **Auth**: Yes
  - **Query params**: `limit`, `offset`
  - **Response shape**: `Page[SavingsGoalResponse]` (includes `contributions[]`)

- **Create**
  - **Endpoint**: `POST /api/v1/goals`
  - **Auth**: Yes

- **Details**
  - **Endpoint**: `GET /api/v1/goals/{goal_id}`
  - **Auth**: Yes

- **Update**
  - **Endpoint**: `PATCH /api/v1/goals/{goal_id}`
  - **Auth**: Yes

- **Delete**
  - **Endpoint**: `DELETE /api/v1/goals/{goal_id}`
  - **Auth**: Yes
  - **Response**: `204`

- **Add contribution**
  - **Endpoint**: `POST /api/v1/goals/{goal_id}/contributions`
  - **Auth**: Yes
  - **Response shape**: `GoalContributionResponse`

### Analytics screen

- **Spending by category**
  - **Endpoint**: `GET /api/v1/analytics/spending-by-category`
  - **Auth**: Yes
  - **Query params**: `start`, `end` (optional)

- **Monthly trend**
  - **Endpoint**: `GET /api/v1/analytics/monthly-trend`
  - **Auth**: Yes
  - **Query params**: `months` (1..36)

- **Cashflow**
  - **Endpoint**: `GET /api/v1/analytics/cashflow`
  - **Auth**: Yes
  - **Query params**: `start`, `end` (optional)

- **Top categories**
  - **Endpoint**: `GET /api/v1/analytics/top-categories`
  - **Auth**: Yes
  - **Query params**: `start`, `end`, `limit` (1..20)

### Settings screen

- **Get my settings**
  - **Endpoint**: `GET /api/v1/settings/me`
  - **Auth**: Yes

- **Update my settings**
  - **Endpoint**: `PATCH /api/v1/settings/me`
  - **Auth**: Yes

---

## Important business rules the frontend must respect

- **Authorization required**: all endpoints except `POST /auth/*` require `Authorization: Bearer ...`.
- **Account archived rule**: archived accounts **cannot** accept new transactions unless `allow_transactions_when_archived=true`.
- **Transaction category constraints**:
  - `income` requires an **income** category
  - `expense` requires an **expense** category
  - `transfer` must not include `category_id`
- **Transfer constraints**:
  - `destination_account_id` is required
  - destination must differ from source
  - source and destination currency must match
- **Balances are server-controlled**: don’t “precompute” final balances client-side; treat server as source of truth.
- **Refresh token rotation**: after refresh, store the **new refresh token** only.

