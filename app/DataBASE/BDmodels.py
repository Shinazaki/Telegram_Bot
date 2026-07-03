from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String, text
from datetime import date, datetime

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "Students"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    SNF: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    course: Mapped[int | None] = mapped_column(nullable=True)
    group: Mapped[int | None] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="student")
    is_group_leader: Mapped[bool] = mapped_column(Boolean, default=False)


class Absence(Base):
    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("Students.id"), index=True)
    absence_date: Mapped[date] = mapped_column(Date)
    reason_type: Mapped[str] = mapped_column(String(20))
    photo_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def _ensure_students_columns() -> None:
    async with engine.begin() as connection:
        rows = await connection.execute(text("PRAGMA table_info('Students')"))
        columns = {row[1] for row in rows.fetchall()}

        if "role" not in columns:
            await connection.execute(
                text("ALTER TABLE 'Students' ADD COLUMN role VARCHAR(20) DEFAULT 'student'")
            )

        if "is_group_leader" not in columns:
            await connection.execute(
                text("ALTER TABLE 'Students' ADD COLUMN is_group_leader BOOLEAN DEFAULT 0")
            )


async def async_main():
    async with engine.begin() as data_base:
        await data_base.run_sync(Base.metadata.create_all)

    await _ensure_students_columns()