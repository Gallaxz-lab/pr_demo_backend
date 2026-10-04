from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import Base, engine, SessionLocal
from app.routers import catalog, inventory, customers, orders, ai_qa, auth, messaging, workshop, finance, analytics, ledger, procurement
from app.services.ledger_service import seed_chart_of_accounts

Base.metadata.create_all(bind=engine)

_db = SessionLocal()
seed_chart_of_accounts(_db)
_db.close()

app = FastAPI(
    title="PR.Racing Shop — Business Backend",
    description="Vertical ERP for a performance motorcycle garage. One shared catalog/inventory/order database across all modules.",
    version="0.2.0",
)

# Local/dev only — tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 1 — working business backend
app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(inventory.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(ai_qa.router)

# Phase 2 — AI-driven commerce and workshop
app.include_router(messaging.router)
app.include_router(workshop.router)

# Phase 3 — financial automation and multi-platform integration
app.include_router(finance.router)
app.include_router(analytics.router)

# ERP core — general ledger + procurement (added once catalog/orders/workshop/
# finance were already working; this is what makes the numbers in Phase 3
# traceable to a real trial balance instead of just dashboard summaries)
app.include_router(ledger.router)
app.include_router(procurement.router)

# Serve the admin UI from this same server — so exposing this one process
# (LAN IP, ngrok, cloudflared, or a real deployment) gives you both the API
# and the UI at once, same origin, no separate frontend host to expose.
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/ui", StaticFiles(directory=_frontend_dir, html=True), name="ui")


@app.get("/")
def root():
    return {
        "status": "ok",
        "shop": "PR.Racing Shop — ช่างอ้อมบ้านโป่ง",
        "phases": {
            "1": "catalog, inventory, orders, customers, admin auth, catalog-grounded AI Q&A — fully working",
            "2": "LINE webhook + workshop jobs — logic complete, needs a real LINE OA to go live",
            "3": "settlement reconciliation + invoice OCR + analytics — invoice OCR is real (needs ANTHROPIC_API_KEY); settlement matching is real logic against a placeholder reference format",
            "erp_core": "general ledger (double-entry, chart of accounts, trial balance) + procurement (suppliers, purchase orders, goods receipt) — fully working, posts real journal entries",
        },
        "docs": "/docs",
    }
