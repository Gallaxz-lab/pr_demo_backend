"""Run: python seed_data.py — populates demo catalog data matching the Phase 1 pitch deck."""
from app.database import SessionLocal, Base, engine
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

catalog = [
    ("EX-155-FULL", "Full exhaust system", "exhaust", 8900,
     [("Yamaha", "Exciter 155", 2019, 2024)], 4),
    ("SPK-15T-428", "Racing sprocket 15T", "drivetrain", 650,
     [("Yamaha", "Exciter 155", 2019, 2024), ("Honda", "CBR150R", 2017, 2023)], 2),
    ("ECU-RMP-01", "ECU remap kit", "electronics", 3500,
     [("Honda", "CBR150R", 2017, 2023), ("Honda", "PCX 160", 2021, 2024)], 9),
    ("BRK-SPT-W125", "Rear brake pump, sport", "brakes", 1200,
     [("Honda", "Wave 125i", 2018, 2023)], 1),
    ("SHK-ADJ-R1", "Rear shock, adjustable", "suspension", 4200,
     [("Honda", "Wave 125i", 2018, 2023), ("Yamaha", "Exciter 155", 2019, 2024)], 6),
    ("ADP-PCX160", "Brake pump adapter", "brakes", 350,
     [("Honda", "PCX 160", 2021, 2024)], 0),
]

for sku, name, cat, price, compat, stock in catalog:
    if db.query(models.Product).filter_by(sku=sku).first():
        continue
    p = models.Product(sku=sku, name=name, category=cat, price=price)
    db.add(p)
    db.flush()
    for make, model, yf, yt in compat:
        db.add(models.Compatibility(product_id=p.id, bike_make=make, bike_model=model, year_from=yf, year_to=yt))
    db.add(models.StockLevel(product_id=p.id, quantity=stock, reorder_threshold=3))

db.commit()
print(f"Seeded {len(catalog)} catalog items.")
