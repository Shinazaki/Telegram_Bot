import asyncio
import logging

from aiogram import Bot ,Dispatcher
from app.config import TOKEN
from app.headers import router
from app.DataBASE.BDmodels import async_main
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stop")        