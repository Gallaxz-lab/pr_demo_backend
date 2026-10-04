"""Run: python create_admin.py <username> <password> [role] — creates/resets an admin login.
Defaults: username=owner password=changeme role=owner"""
import sys
from app.database import SessionLocal, Base, engine
from app import models
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

username = sys.argv[1] if len(sys.argv) > 1 else "owner"
password = sys.argv[2] if len(sys.argv) > 2 else "changeme"
role = sys.argv[3] if len(sys.argv) > 3 else "owner"

user = db.query(models.AdminUser).filter_by(username=username).first()
if user:
    user.hashed_password = hash_password(password)
    user.role = role
else:
    db.add(models.AdminUser(username=username, hashed_password=hash_password(password), role=role))
db.commit()
print(f"Admin user '{username}' ready with role '{role}'.")
