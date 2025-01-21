from models import User
from db_connection import SessionLocal


db = SessionLocal()


def get_primary_users(jid):
    user = db.query(User).filter(User.jid == jid).first()
    primary_users = db.query(User).filter(User.primary_user == user.id).all()
    return primary_users
