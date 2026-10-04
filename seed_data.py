"""Run: python seed_data.py — populates demo catalog, supplier, and chart of
accounts (the last one also happens automatically on app startup)."""
from app.database import SessionLocal, Base, engine
from app import models
from app.services.ledger_service import seed_chart_of_accounts

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# (sku, name, category, price, cost_price, compatibility, stock)
catalog = [
    ("EX-155-FULL", "Full exhaust system", "exhaust", 8900, 5300,
     [("Yamaha", "Exciter 155", 2019, 2024)], 4),
    ("SPK-15T-428", "Racing sprocket 15T", "drivetrain", 650, 380,
     [("Yamaha", "Exciter 155", 2019, 2024), ("Honda", "CBR150R", 2017, 2023)], 2),
    ("ECU-RMP-01", "ECU remap kit", "electronics", 3500, 2000,
     [("Honda", "CBR150R", 2017, 2023), ("Honda", "PCX 160", 2021, 2024)], 9),
    ("BRK-SPT-W125", "Rear brake pump, sport", "brakes", 1200, 700,
     [("Honda", "Wave 125i", 2018, 2023)], 1),
    ("SHK-ADJ-R1", "Rear shock, adjustable", "suspension", 4200, 2500,
     [("Honda", "Wave 125i", 2018, 2023), ("Yamaha", "Exciter 155", 2019, 2024)], 6),
    ("ADP-PCX160", "Brake pump adapter", "brakes", 350, 200,
     [("Honda", "PCX 160", 2021, 2024)], 0),
]

for sku, name, cat, price, cost, compat, stock in catalog:
    if db.query(models.Product).filter_by(sku=sku).first():
        continue
    p = models.Product(sku=sku, name=name, category=cat, price=price, cost_price=cost)
    db.add(p)
    db.flush()
    for make, model, yf, yt in compat:
        db.add(models.Compatibility(product_id=p.id, bike_make=make, bike_model=model, year_from=yf, year_to=yt))
    db.add(models.StockLevel(product_id=p.id, quantity=stock, reorder_threshold=3))

if not db.query(models.Supplier).filter_by(name="Bangkok Moto Parts Co.").first():
    db.add(models.Supplier(name="Bangkok Moto Parts Co.", contact="คุณสมศักดิ์", phone="02-123-4567"))

db.commit()
seed_chart_of_accounts(db)
print(f"Seeded {len(catalog)} catalog items, 1 supplier, and the chart of accounts.")
