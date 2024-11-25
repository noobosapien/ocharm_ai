from db_connection import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    CheckConstraint,
    UniqueConstraint,
)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    jid = Column(String(200), nullable=False)
    name = Column(String(100), nullable=False)
    authenticated_use = Column(
        Integer, nullable=False, default="100", server_default="100"
    )

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="user_name_length_check"),
        UniqueConstraint("jid", name="uq_user_jid"),
    )
