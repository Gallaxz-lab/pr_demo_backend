from sqlalchemy.orm import Session
from app import models


def get_default_warehouse(db: Session) -> models.Warehouse:
    wh = db.query(models.Warehouse).filter_by(is_default=True).first()
    if not wh:
        wh = models.Warehouse(name="Main Warehouse", address="", is_default=True)
        db.add(wh)
        db.commit()
        db.refresh(wh)
    return wh
