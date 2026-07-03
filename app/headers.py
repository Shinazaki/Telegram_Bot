from aiogram import Router

router = Router()
from app.handlers.absence import router as absence_router
from app.handlers.auth import router as auth_router
from app.handlers.report import router as report_router

router.include_router(auth_router)
router.include_router(absence_router)
router.include_router(report_router)
