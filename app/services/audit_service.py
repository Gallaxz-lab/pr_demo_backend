from sqlalchemy.orm import Session
from app import models


def log_action(db: Session, actor: str, action: str, entity: str, entity_id="", detail: str = ""):
    db.add(models.AuditLog(actor=actor, action=action, entity=entity, entity_id=str(entity_id), detail=detail))
    db.commit()
