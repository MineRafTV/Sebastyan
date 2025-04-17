import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile
)

API_TOKEN = "7697580781:AAFQABGbMRgeEiqRWAM3m3ouS-kEBhU7WcA"
PHOTO_FOLDER = r"C:\Users\SystemX\Documents\Bot\photos"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

photos = []
user_photo_index = {}

def kill_previous_instances():
    try:
        current_pid = os.getpid()
        output = os.popen('wmic process where "name=\'python.exe\'" get processid, commandline').read()
        for line in output.split('\n'):
            if 'bot.py' in line and str(current_pid) not in line:
                pid = line.strip().split()[-1]
                os.system(f'taskkill /F /PID {pid}')
                print(f"Завершен процесс: {pid}")
    except Exception as e:
        print(f"Ошибка завершения процессов: {str(e)}")

def load_photos():
    global photos
    if not os.path.exists(PHOTO_FOLDER):
        raise Exception(f"Папка {PHOTO_FOLDER} не существует!")
    photos = [f for f in os.listdir(PHOTO_FOLDER) 
            if f.endswith((".jpg", ".jpeg", ".png"))]
    if not photos:
        raise Exception("Нет фотографий в папке!")
    print(f"Загружено фото: {len(photos)} шт.")

def get_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👈 Назад", callback_data="prev"),
            InlineKeyboardButton(text="👉 Далее", callback_data="next")
        ]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    try:
        await message.answer("🎉 С Днем Рождения!🎂")
        user_photo_index[message.from_user.id] = 0
        await send_photo(message.from_user.id)
    except Exception as e:
        await message.answer(f"😢 Ошибка: {str(e)}")

@dp.callback_query(lambda c: c.data in ["next", "prev"])
async def navigate_photos(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_index = user_photo_index.get(user_id, 0)
    new_index = current_index + 1 if callback.data == "next" else max(0, current_index - 1)
    user_photo_index[user_id] = new_index
    await send_photo(user_id)
    await callback.answer()

async def send_photo(user_id: int):
    try:
        index = user_photo_index.get(user_id, 0)
        if index >= len(photos):
            await bot.send_message(user_id, "📸 Это последняя фотка! /start - начать заново")
            return
        
        photo_path = os.path.join(PHOTO_FOLDER, photos[index])
        await bot.send_photo(
            user_id,
            FSInputFile(photo_path),
            caption=f"Фото {index + 1}/{len(photos)}\n{get_funny_comment(index)}",
            reply_markup=get_keyboard()
        )
    except Exception as e:
        await bot.send_message(user_id, f"🚨 Ошибка: {str(e)}")

def get_funny_comment(index: int) -> str:
    comments = [
        "А вот это было эпично!",
        "Тут ты вообще выдал! 🤣",
        "Момент истины!",
        "Этот момент мы не забудем!"
    ]
    return comments[index % len(comments)]

async def main():
    kill_previous_instances()
    await bot.delete_webhook(drop_pending_updates=True)
    load_photos()
    
    try:
        await dp.start_polling(bot, polling_timeout=30)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())