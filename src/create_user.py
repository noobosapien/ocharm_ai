from dotenv import load_dotenv

load_dotenv()
from db_connection import get_db_session, SessionLocal
from models import User

db = SessionLocal()

new_user = User(
    jid="abc1234",
    name="test2",
    authenticated_use=(1 << 1 | 1 << 2 | 1 << 3 | 1 << 4),
)
db.add(new_user)
db.commit()
db.refresh(new_user)
