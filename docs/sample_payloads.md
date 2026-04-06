## Sample payloads (requests + responses)

Notes:
- All authenticated calls include `Authorization: Bearer <access_token>`.
- List endpoints return the standard pagination envelope:
  - `{ "items": [...], "meta": { "limit": n, "offset": n, "total": n } }`

---

### Login

**POST** ` /api/v1/auth/login `

Request:

```json
{
  "email": "demo@finance.local",
  "password": "DemoPassword1!"
}
```

Response `200`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "3c1c8b79-0bb6-4a6e-b2f2-... .6b4f5a4d-...",
  "token_type": "bearer"
}
```

---

### Me (current user)

**GET** ` /api/v1/auth/me `

Response `200`:

```json
{
  "id": "a6e5c2e0-2f0e-4d90-a1f3-2e0c2d6c8c1b",
  "email": "demo@finance.local",
  "full_name": "Demo User",
  "onboarding_completed": true
}
```

---

### Accounts list

**GET** ` /api/v1/accounts?limit=20&offset=0 `

Response `200`:

```json
{
  "items": [
    {
      "id": "0b8a2c7a-2b79-4d4a-9c4a-0a2d2e8b9c0d",
      "name": "Main Checking",
      "type": "bank",
      "currency": "USD",
      "balance": "5345.80",
      "archived": false,
      "allow_transactions_when_archived": false
    }
  ],
  "meta": { "limit": 20, "offset": 0, "total": 2 }
}
```

---

### Categories list (expense)

**GET** ` /api/v1/categories?type=expense&limit=50&offset=0 `

Response `200`:

```json
{
  "items": [
    {
      "id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22",
      "name": "Groceries",
      "type": "expense",
      "icon": "cart",
      "color": "#f97316",
      "is_system": true
    }
  ],
  "meta": { "limit": 50, "offset": 0, "total": 7 }
}
```

---

### Create transaction (expense)

**POST** ` /api/v1/transactions `

Request:

```json
{
  "type": "expense",
  "amount": "54.20",
  "occurred_at": "2026-04-06T12:00:00Z",
  "account_id": "0b8a2c7a-2b79-4d4a-9c4a-0a2d2e8b9c0d",
  "category_id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22",
  "note": "Weekly groceries",
  "merchant": "Whole Foods",
  "recurring_template": null
}
```

Response `201`:

```json
{
  "id": "7d07f3b5-7dc6-4b24-8b46-3b7c8c2d9f72",
  "type": "expense",
  "amount": "54.20",
  "currency": "USD",
  "occurred_at": "2026-04-06T12:00:00+00:00",
  "note": "Weekly groceries",
  "merchant": "Whole Foods",
  "account_id": "0b8a2c7a-2b79-4d4a-9c4a-0a2d2e8b9c0d",
  "destination_account_id": null,
  "category_id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22"
}
```

---

### Transactions list with pagination meta + search

**GET** ` /api/v1/transactions?q=groceries&limit=20&offset=0&sort=occurred_at_desc `

Response `200`:

```json
{
  "items": [
    {
      "id": "7d07f3b5-7dc6-4b24-8b46-3b7c8c2d9f72",
      "type": "expense",
      "amount": "54.20",
      "currency": "USD",
      "occurred_at": "2026-04-06T12:00:00+00:00",
      "note": "Weekly groceries",
      "merchant": "Whole Foods",
      "account_id": "0b8a2c7a-2b79-4d4a-9c4a-0a2d2e8b9c0d",
      "destination_account_id": null,
      "category_id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22"
    }
  ],
  "meta": { "limit": 20, "offset": 0, "total": 1 }
}
```

---

### Budgets list

**GET** ` /api/v1/budgets?limit=20&offset=0 `

Response `200`:

```json
{
  "items": [
    {
      "id": "2ad1a8b5-3e0f-4bd1-a4d0-0f3c3f1f0e11",
      "year": 2026,
      "month": 4,
      "amount": "300.00",
      "currency": "USD",
      "category_id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22",
      "spent": "54.20",
      "remaining": "245.80",
      "usage_pct": "18.07",
      "is_over_budget": false
    }
  ],
  "meta": { "limit": 20, "offset": 0, "total": 2 }
}
```

---

### Goal details with contributions

**GET** ` /api/v1/goals/{goal_id} `

Response `200`:

```json
{
  "id": "8c1a0e2b-8d2b-4c9c-9b5f-7f9a2f2b3c4d",
  "name": "Emergency Fund",
  "target_amount": "2000.00",
  "current_amount": "250.00",
  "currency": "USD",
  "deadline": "2026-08-04T07:00:00+00:00",
  "completed": false,
  "progress_pct": "12.50",
  "contributions": [
    {
      "id": "c1f02d3a-4f5b-4a9c-8b1d-2f3a4b5c6d7e",
      "amount": "150.00",
      "contributed_at": "2026-04-01T12:00:00+00:00",
      "note": "Extra savings"
    }
  ]
}
```

---

### Dashboard summary

**GET** ` /api/v1/dashboard/summary `

Response `200` (shape excerpt):

```json
{
  "total_balance": "5495.80",
  "total_income_current_month": "3000.00",
  "total_expense_current_month": "72.95",
  "total_savings": "0.00",
  "budget_usage_summary": [
    {
      "budget_id": "2ad1a8b5-3e0f-4bd1-a4d0-0f3c3f1f0e11",
      "year": 2026,
      "month": 4,
      "amount": "300.00",
      "spent": "54.20",
      "remaining": "245.80",
      "usage_pct": "18.07",
      "is_over_budget": false,
      "category_id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22"
    }
  ],
  "recent_transactions": [],
  "active_goals": [],
  "top_spending_categories": [],
  "account_overview": []
}
```

---

### Analytics: spending-by-category

**GET** ` /api/v1/analytics/spending-by-category?start=2026-04-01T00:00:00Z&end=2026-05-01T00:00:00Z `

Response `200`:

```json
{
  "start": "2026-04-01T00:00:00+00:00",
  "end": "2026-05-01T00:00:00+00:00",
  "items": [
    { "category_id": "1c3f0d9d-5b65-4df0-9f1c-2c7e1f4d9a22", "category_name": "Groceries", "total": "54.20" }
  ]
}
```

---

### Settings update

**PATCH** ` /api/v1/settings/me `

Request:

```json
{
  "preferred_currency": "EUR",
  "theme_preference": "dark"
}
```

Response `200`:

```json
{
  "preferred_currency": "EUR",
  "locale": "en-US",
  "timezone": "UTC",
  "notifications_enabled": true,
  "budget_alerts_enabled": true,
  "theme_preference": "dark"
}
```

