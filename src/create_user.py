from models import User
from db_connection import get_db_session, SessionLocal
from dotenv import load_dotenv

load_dotenv()

db = SessionLocal()

new_user = User(
    jid="migara@xmpp.jp",
    name="migara",
    authenticated_use=(1 << 1 | 1 << 2 | 1 << 3 | 1 << 4),
)

db.add(new_user)
db.commit()
db.refresh(new_user)
