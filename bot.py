import os
import asyncio
import logging
import google.generativeai as genai
from pptx import Presentation
from docx import Document
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)

# --- KONFIGURATSIYA ---
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# API ni eng barqaror shaklda sozlash
genai.configure(api_key=GEMINI_KEY)

# Modelni tanlash (Mintaqaviy 404 xatosini oldini olish uchun)
def get_model():
    try:
        # Eng yangi va tezkor model
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        # Muammo bo'lsa, zaxira model
        return genai.GenerativeModel('gemini-pro')

model = get_model()

bot = Bot(token=TOKEN)
dp = Dispatcher()

class BotStates(StatesGroup):
    waiting_for_esse = State()
    waiting_for_pptx = State()

# --- MENYU ---
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Sifatli Esse (Word)")],
    [KeyboardButton(text="📊 Professional Taqdimot (PPTX)")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Salom! Men professional esse va taqdimotlar yaratuvchi botman. 🚀", 
        reply_markup=menu
    )

# --- ESSE YARATISH ---
@dp.message(F.text == "📝 Sifatli Esse (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring:")

@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    wait_msg = await message.answer("🧠 AI akademik esse yozmoqda...")
    try:
        response = model.generate_content(f"{message.text} mavzusida o'zbek tilida batafsil esse yoz.")
        
        doc = Document()
        doc.add_heading(message.text, 0)
        doc.add_paragraph(response.text)
        
        file_path = f"esse_{message.from_user.id}.docx"
        doc.save(file_path)
        
        await message.answer_document(FSInputFile(file_path), caption="✅ Esse tayyor!")
        os.remove(file_path)
    except Exception as e:
        logging.error(f"Esse Error: {e}")
        await message.answer("❌ API bilan bog'lanishda xato. Kalitingizni va mintaqangizni tekshiring.")
    finally:
        await wait_msg.delete()
        await state.clear()

# --- TAQDIMOT YARATISH ---
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    wait_msg = await message.answer("🎨 Professional slaydlar tayyorlanmoqda...")
    try:
        prompt = f"'{message.text}' mavzusida 7 ta slayd uchun matn yoz. Har bir slaydni 'SLAYD:' so'zi bilan ajrat."
        response = model.generate_content(prompt)
        
        prs = Presentation()
        prs.slide_width, prs.slide_height = 12192000, 6858000 # 16:9
        
        parts = response.text.split("SLAYD:")
        for part in parts[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = message.text
            slide.placeholders[1].text = part.strip()

        file_path = f"ppt_{message.from_user.id}.pptx"
        prs.save(file_path)
        await message.answer_document(FSInputFile(file_path), caption="✅ Taqdimot tayyor!")
        os.remove(file_path)
    except Exception as e:
        logging.error(f"PPTX Error: {e}")
        await message.answer("❌ Taqdimot yaratishda xato yuz berdi.")
    finally:
        await wait_msg.delete()
        await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
