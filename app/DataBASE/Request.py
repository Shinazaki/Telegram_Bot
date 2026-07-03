from datetime import date

from app.DataBASE.BDmodels import Absence, Student, async_session
from sqlalchemy import func, select
from sqlalchemy.orm import aliased


def normalize_email(email: str) -> str:
    return email.strip().lower()


def resolve_role(student: Student) -> str:
    if student.role == "leader" or student.is_group_leader:
        return "leader"
    return "student"


async def get_student_by_email(email: str) -> Student | None:
    async with async_session() as session:
        normalized_email = normalize_email(email)
        return await session.scalar(
            select(Student).where(func.lower(Student.email) == normalized_email)
        )


async def get_student_by_telegram_id(tg_id: int) -> Student | None:
    async with async_session() as session:
        return await session.scalar(select(Student).where(Student.tg_id == tg_id))


async def bind_telegram_id(student_id: int, tg_id: int) -> None:
    async with async_session() as session:
        existing = await session.scalar(
            select(Student).where(Student.tg_id == tg_id, Student.id != student_id)
        )
        if existing is not None:
            return

        student = await session.get(Student, student_id)
        if student is None:
            return

        student.tg_id = tg_id
        student.role = resolve_role(student)
        await session.commit()


async def create_absence(
    student_id: int,
    absence_date: date,
    reason_type: str,
    photo_file_id: str | None = None,
) -> None:
    async with async_session() as session:
        session.add(
            Absence(
                student_id=student_id,
                absence_date=absence_date,
                reason_type=reason_type,
                photo_file_id=photo_file_id,
            )
        )
        await session.commit()


async def get_group_absences_for_leader(leader_id: int) -> list[dict]:
    async with async_session() as session:
        leader = await session.get(Student, leader_id)
        if leader is None or leader.group is None:
            return []

        student_alias = aliased(Student)

        result = await session.execute(
            select(
                student_alias.SNF,
                Absence.absence_date,
                Absence.reason_type,
                Absence.photo_file_id,
            )
            .join(student_alias, student_alias.id == Absence.student_id)
            .where(student_alias.group == leader.group)
            .order_by(Absence.absence_date.desc(), student_alias.SNF.asc())
        )

        rows = []
        for full_name, absence_date, reason_type, photo_file_id in result.all():
            rows.append(
                {
                    "full_name": full_name,
                    "absence_date": absence_date,
                    "reason_type": reason_type,
                    "has_document": bool(photo_file_id),
                }
            )

        return rows