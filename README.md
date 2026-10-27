# Motorcyle's part shop ERP prototype — Business Backend

FastAPI + SQLAlchemy backend for a vertical ERP serving a performance
motorcycle garage. One shared database (products, compatibility, stock,
customers, orders) underneath every module, so nothing drifts out of sync
between channels.

<img width="1611" height="535" alt="Screenshot 2026-10-27 120427" src="https://github.com/user-attachments/assets/f02defd7-6bcc-43d0-a114-791e7595b8a9" />

<img width="1827" height="894" alt="Screenshot 2026-10-27 120446" src="https://github.com/user-attachments/assets/60d6b427-b54f-489a-b942-b045e46b1589" />


## What's real vs. stubbed

This was built without network/API access, so it splits honestly:

| | Status |
|---|---|
| **Phase 1** — catalog, inventory, orders, customers, admin auth, catalog-grounded AI Q&A | **Fully working.** Runs end-to-end with `sqlite` and no external accounts. |
| **Phase 2** — LINE webhook, workshop job management | **Logic complete, integration stubbed.** The webhook parses LINE's event format and routes to the real Q&A engine; `line_service.py` needs a real LINE Official Account's channel secret/token to actually send messages (falls back to printing replies to the console until then). |
| **Phase 3** — settlement reconciliation, invoice OCR, analytics | **Invoice OCR is real** (Claude vision API — works once `ANTHROPIC_API_KEY` is set; accuracy depends on image quality and hasn't been validated against real supplier invoices yet, which is why the review step before posting still matters). **Settlement reconciliation logic is real but matches against a placeholder reference format** — actual Shopee/Lazada exports need seller-center access to see their real format.
| **ERP core** — general ledger, chart of accounts, procurement | **Fully working.** Real double-entry posting, a real trial balance, real purchase-order-to-inventory-to-ledger flow. This is what elevates the project from "business admin app" to actual ERP — see the section below. |

Every stub is marked with a docstring explaining exactly what's missing and
why — search for `STUB` or `Phase 2`/`Phase 3` comments.

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in ANTHROPIC_API_KEY etc. as you get them
python seed_data.py           # loads demo catalog (matches the pitch dashboard)
python create_admin.py owner yourpassword owner
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for interactive Swagger docs — every
endpoint below is callable from there directly.

To switch from the SQLite demo DB to Postgres, just change `DATABASE_URL`
in `.env` — the models don't change.

## Admin UI

`frontend/admin.html` is a plain HTML/JS admin console wired to the real
API above — not mock data. Run the backend, then just open the file in a
browser (or `cd frontend && python -m http.server 8080`):

- Dashboard — live KPIs from `/analytics/*`
- Catalog, Inventory, Orders (with a working "Verify" button that calls
  `/orders/{id}/verify-payment`), AI Q&A tester, Workshop job board,
  Finance (settlement import + invoice OCR), Analytics

It's a plain file, not a hosted page, because it needs to reach your
backend on `localhost` — a hosted page can't. The API base URL is
editable in the top bar if you run the backend somewhere other than
`http://localhost:8000`.

## ERP core — general ledger + procurement

This is the part that actually makes this an ERP rather than a business
admin app: every money-moving action posts a real, balanced double-entry
journal entry, not just a status update.

- **Chart of accounts** — `GET /ledger/accounts`
- **Trial balance** — `GET /ledger/trial-balance` (owner/admin only)
- **Journal entries** — `GET /ledger/entries` (owner/admin only)
- **Suppliers + purchase orders** — `POST /procurement/suppliers`, `POST /procurement/purchase-orders`, `POST /procurement/purchase-orders/{id}/receive` (receiving goods posts a real Inventory/Accounts Payable entry)

What posts automatically:
| Event | Journal entry |
|---|---|
| Order payment verified (LINE/manual) | Dr Cash, Cr Sales Revenue (+ Dr COGS, Cr Inventory if the product has a `cost_price`) |
| Order payment verified (Shopee/Lazada) | Dr Accounts Receivable, Cr Sales Revenue |
| Settlement import matches an order | Dr Cash (net), Dr Marketplace Fees Expense, Cr Accounts Receivable (gross) — clears the AR from above |
| Invoice marked posted (`POST /finance/invoices/{id}/post`) | Dr Operating Expense, Cr Accounts Payable |
| PO marked received | Dr Inventory, Cr Accounts Payable |

**Behavior change worth knowing:** `verify-payment`, `inventory/movements`,
`settlements/import`, `invoices/{id}/post`, and `purchase-orders/{id}/receive`
now require a logged-in admin user (`require_role` is actually enforced on
these, where before it existed but nothing used it). Log in via `POST
/auth/login` first, or `admin.html`'s login form — anonymous calls to these
specific endpoints will now 401.

An `AuditLog` table also records who did what on every one of those actions
(`actor`, `action`, `entity`, `entity_id`, `detail`, timestamp) — nothing in
the app code edits or deletes these rows.

**Known simplification, not a bug:** cash-vs-AR treatment is decided purely
by `order.channel` (LINE/manual = cash now, Shopee/Lazada = AR until
settled). Real accrual accounting would also handle partial settlements,
refunds, and multi-currency — none of which exist here.

## Foundation layer — scaffolded, needs confirmation before real use

Each of these has real data models and real endpoints — this is not a UI
mockup, the code runs — but each has a specific, named gap that needs
something from the real world (a document, a policy decision, or
professional review) before it should touch real data.

| Module | What's built | What's needed to make it complete |
|---|---|---|
| **Multi-warehouse** (`/warehouses`) | `Warehouse` model, stock-per-location, a working transfer endpoint. One "Main Warehouse" is seeded; everything else (orders, PO receiving, plain stock movements) still implicitly uses it. | Nothing blocking — just confirm whether the shop actually has >1 physical location before wiring warehouse choice into the rest of the flows. |
| **Customer invoicing / AR aging** (`/receivables`) | `CustomerInvoice` model, invoice issuance from an order, an aging report (current/1-30/31-60/61-90/90+ days overdue). | **VAT-registration status** of the shop (invoice numbering rules only matter if registered). **A real invoice sample** (even handwritten) or the shop's accountant's format spec — current numbering (`INV-<BE year>-<seq>`) and flat 7% VAT are both placeholders, not verified against Revenue Department sequential-numbering rules. |
| **Payroll** (`/payroll`) — **demo estimator only** | `Employee`/`Payslip` models, SSF deduction at a placeholder rate/cap, net pay calculation. | **Do not use for real payroll.** Withholding tax (PND.1) is left at 0 on purpose rather than faked — it's progressive brackets, not a flat rate. SSF rate/cap need verifying against current official numbers. Recommend routing real payroll through an existing Thai provider (FlowAccount, PayrollHero) instead of extending this, or having an accountant review before ever using it for a real paycheck. |
| **Bank reconciliation** (`/banking`) | `BankStatementLine` model, a naive amount-matching endpoint, same pattern as marketplace settlement matching. | **A sample export (CSV/Excel) from the shop's actual bank** — Kbank, SCB, Bangkok Bank etc. all format differently, and some only offer PDF, which is harder to parse. Nothing can be built against a real format without seeing one. |
| **Approval workflows** (`/approvals`) | `Approval` model, wired into purchase orders: a PO at/above ฿10,000 blocks `receive` until an owner approves it. | **The threshold (฿10,000) is a placeholder guess** — needs the owner to actually set a real number, and confirm whether owner-only approval is correct or if there should be a manager tier. |
| **Multi-tenancy** (`/shops`) | `Shop` model + `AdminUser.shop_id` — the seed of the pattern. | **Not a technical gap — a business decision.** Real multi-tenancy means repeating `shop_id` scoping across every table and every query, which is mechanical but substantial. Deliberately not done until it's confirmed this is becoming a sellable product, not a bespoke build for one shop. |

## Still not full ERP — what's genuinely still missing

All six items above now have a foundation. What's left, even after that:

- **None of the foundation modules are wired into the rest of the system end-to-end** — e.g. orders don't automatically issue a customer invoice, POs don't automatically check which warehouse to receive into, payroll doesn't pull hours from workshop jobs. Each works standalone via its own endpoints, not yet as part of the existing flows.
- **Budgeting / forecasting** beyond the simple reorder-threshold flag
- **Document generation** — no PDF for invoices, quotations, or packing slips yet, despite being a named Phase 2 goal
- **Full multi-tenancy** — the `Shop` table exists but nothing is actually scoped by it yet (see table above)

The pattern going forward for all of these: each needs a specific real
input named in the table above, not more guessing.

## Demo pages

`demo/` holds two standalone, no-backend-required HTML pages used for
presenting the Finance module to non-technical stakeholders — a sample-data
walkthrough of reconciliation and OCR, in English and Thai. Open them
directly in a browser; they're self-contained.

## Endpoint map by phase

**Phase 1**
- `POST /auth/login` — admin JWT login
- `GET/POST /catalog/products`, `GET /catalog/compatibility`
- `GET /inventory/stock`, `POST /inventory/movements`
- `GET/POST /customers/`, `GET /customers/{id}/history`
- `GET/POST /orders/`, `POST /orders/{id}/verify-payment`
- `POST /ai/qa` — catalog-grounded Q&A (try it with no `ANTHROPIC_API_KEY` set — it still answers from the catalog)

**Phase 2**
- `POST /messaging/line/webhook` — LINE event receiver
- `GET/POST /workshop/jobs`, `.../approve`, `.../assign`, `.../complete`

**Phase 3**
- `POST /finance/settlements/import`
- `POST /finance/invoices/ocr`
- `GET /analytics/low-stock-forecast`, `GET /analytics/sales-summary`

## Why one shared database

Every router reads/writes the same `Product`, `StockLevel`, `Customer`, and
`Order` tables. A LINE-driven sale (Phase 2) deducts the same stock row an
admin-verified order (Phase 1) would, and a settlement import (Phase 3)
reconciles against the same `Order.total_amount` the storefront created —
so there's no separate "channel database" to fall out of sync.

## Next real steps, in order

1. Get a LINE Official Account + webhook URL → drop credentials into `.env`, `line_service.py` goes live with zero code changes.
2. Add `ANTHROPIC_API_KEY` → AI Q&A moves from the deterministic fallback to actual conversational replies, still catalog-grounded.
3. Once you have Shopee/Lazada seller-center access, replace the placeholder matcher in `reconciliation_service.py` with each platform's actual settlement reference format.
4. Pick an OCR provider (Claude's vision API works well here) and fill in `ocr_service.py`.
