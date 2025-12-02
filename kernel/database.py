from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, BigInteger, Text

# Database Configuration
DATABASE_URL = "postgresql+asyncpg://vryndara:devpassword@localhost:5433/vryndara_core"

Base = declarative_base()

# Define the Event Log Table
class EventLog(Base):
    __tablename__ = "event_log"

    id = Column(String, primary_key=True)  # UUID
    source = Column(String, index=True)
    target = Column(String, index=True)
    type = Column(String)
    payload = Column(Text)
    timestamp = Column(BigInteger, index=True)

# Async Engine Setup
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """Creates tables if they don't exist."""
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Uncomment to reset DB
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] Schema initialized.")