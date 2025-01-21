from models import User
from db_connection import SessionLocal


db = SessionLocal()


def get_user(jid):
    user = db.query(User).filter(User.jid == jid).first()
    return user
