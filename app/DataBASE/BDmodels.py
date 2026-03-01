from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String

engine = create_async_engine(url ='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = 'Students'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    SNF: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    course: Mapped[int] = mapped_column()
    group: Mapped[int] = mapped_column()

async def async_main():
    async with engine.begin() as DataB:
        await DataB.run_sync(Base.metadata.create_all)