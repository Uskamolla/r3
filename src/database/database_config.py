from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext

# Initialize password hashing using bcrypt algorithm via passlib.
# The "deprecated=auto" setting automatically handles migration if the hashing scheme changes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLite database connection URL. The file "users.db" will be created in the current directory.
DATABASE_URL = "sqlite:///./users.db"

# Create the SQLAlchemy engine with SQLite-specific threading workaround,
# since SQLite only allows one thread to communicate with it at a time by default.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory for creating new database sessions.
# autoflush=False prevents automatic flushing before queries.
# autocommit=False requires explicit commits for transactions.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for all ORM models to inherit from.
Base = declarative_base()

# User model representing the "users" table in the database.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Stores the bcrypt-hashed password, not plaintext.

# Create all tables defined by Base subclasses if they don't already exist.
Base.metadata.create_all(bind=engine)

# Hashes a plaintext password using bcrypt.
# Truncates input to 72 characters since bcrypt ignores anything beyond that limit.
def hash_password(password: str) -> str:
    safe_pw = password[:72]
    return pwd_context.hash(safe_pw)

# Verifies a plaintext password against a stored bcrypt hash.
# Truncates input to 72 characters to match the hashing behavior.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_pw = plain_password[:72]
    return pwd_context.verify(safe_pw, hashed_password)