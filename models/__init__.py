# from models.user import User
# from models.session import Session
from sqlalchemy.orm import Session

# Dependency
def get_db() -> Session:
    from core.setup import DataBaseSession

    db = DataBaseSession()
    try:
        return db
    finally:
        db.close()
