from app.DataBASE.BDmodels import async_session
from app.DataBASE.BDmodels import Student
from sqlalchemy import select

async def get_student_SNF(name: str):
    async with async_session() as session:
        user = await session.scalar(select(Student).where(Student.SNF == name))
        print(user)