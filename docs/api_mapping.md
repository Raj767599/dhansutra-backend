## API mapping to likely mobile screens

Assumptions inferred from design:
- DhanSutra is a mobile-first personal finance app for Indian users; primary flows are accounts, transactions, budgets, goals, dashboard, analytics, and settings.

- **Onboarding / Register** -> `POST /api/v1/auth/register`
- **Login screen** -> `POST /api/v1/auth/login`
- **App token refresh** -> `POST /api/v1/auth/refresh`
- **Logout** -> `POST /api/v1/auth/logout`
- **Profile header (current user)** -> `GET /api/v1/auth/me` or `GET /api/v1/users/me`
- **Edit profile screen** -> `PATCH /api/v1/users/me`
- **Change password screen** -> `POST /api/v1/users/change-password`

- **Accounts list screen** -> `GET /api/v1/accounts`
- **Add account screen** -> `POST /api/v1/accounts`
- **Account details screen** -> `GET /api/v1/accounts/{account_id}`
- **Edit account screen** -> `PATCH /api/v1/accounts/{account_id}`
- **Delete account** -> `DELETE /api/v1/accounts/{account_id}`

- **Categories selector sheet** -> `GET /api/v1/categories?type=expense|income`
- **Manage categories screen** -> `POST/GET/PATCH/DELETE /api/v1/categories...`

- **Transactions list screen** -> `GET /api/v1/transactions` (pagination + filters + search)
- **Transaction detail screen** -> `GET /api/v1/transactions/{transaction_id}`
- **Add transaction screen** -> `POST /api/v1/transactions`
- **Edit transaction screen** -> `PATCH /api/v1/transactions/{transaction_id}`
- **Delete transaction action** -> `DELETE /api/v1/transactions/{transaction_id}`
- **Transactions overview card** -> `GET /api/v1/transactions/summary/overview`

- **Budgets list screen** -> `GET /api/v1/budgets`
- **Create budget flow** -> `POST /api/v1/budgets`
- **Budget details** -> `GET /api/v1/budgets/{budget_id}`
- **Edit budget** -> `PATCH /api/v1/budgets/{budget_id}`
- **Delete budget** -> `DELETE /api/v1/budgets/{budget_id}`

- **Goals list screen** -> `GET /api/v1/goals`
- **Goal details** -> `GET /api/v1/goals/{goal_id}`
- **Create goal** -> `POST /api/v1/goals`
- **Edit goal** -> `PATCH /api/v1/goals/{goal_id}`
- **Delete goal** -> `DELETE /api/v1/goals/{goal_id}`
- **Add contribution** -> `POST /api/v1/goals/{goal_id}/contributions`

- **Home dashboard screen** -> `GET /api/v1/dashboard/summary`

- **Analytics charts**:
  - Spending by category -> `GET /api/v1/analytics/spending-by-category`
  - Monthly trend -> `GET /api/v1/analytics/monthly-trend`
  - Cashflow -> `GET /api/v1/analytics/cashflow`
  - Top categories -> `GET /api/v1/analytics/top-categories`

- **Settings screen** -> `GET /api/v1/settings/me`
- **Edit settings** -> `PATCH /api/v1/settings/me`

## Assumptions inferred from design

- **Categories**: app ships with system default categories; users can add custom categories.
- **Transfers**: transfers require same-currency source/destination (mobile apps typically avoid FX in v1).
- **Budgets**: budgets are monthly; optional category-specific budgets apply to expense categories only.
- **Goals**: goal progress is based on contributions; the app can show a contributions list.
- **Notifications**: stored in DB for display later; no background scheduler in this local-first starter.
- **Soft delete**: entities use `deleted_at` to support undo/audit later and to avoid hard deletes in v1.

