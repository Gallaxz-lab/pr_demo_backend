from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import Base, engine
from app.routers import catalog, inventory, customers, orders, ai_qa, auth, messaging, workshop, finance, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PR.Racing Shop — Business Backend",
    description="Vertical ERP for a performance motorcycle garage. One shared catalog/inventory/order database across all modules.",
    version="0.1.0",
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
            "3": "settlement reconciliation + invoice OCR + analytics — logic complete, needs marketplace/OCR API access to go live",
        },
        "docs": "/docs",
    }
