import os
import asyncio
import google.generativeai as genai
from pptx import Presentation
from docx import Document
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# --- KONFIGURATSIYA ---
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API ni eng xavfsiz versiyada sozlash
genai.configure(api_key=GEMINI_KEY)

# MUHIM: Ba'zi mintaqalarda faqat 'gemini-pro' yoki 'gemini-1.5-flash' ishlaydi
# Biz eng so'nggi va barqaror model nomidan foydalanamiz
model = genai.GenerativeModel('gemini-1.5-flash')

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
    await message.answer("Xizmatlardan birini tanlang:", reply_markup=menu)

# --- ESSE QISMI ---
@dp.message(F.text == "📝 Sifatli Esse (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring:")

@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    status_msg = await message.answer("🧠 AI tahlil qilmoqda...")
    try:
        # AI dan javob olish
        response = model.generate_content(f"{message.text} mavzusida o'zbek tilida akademik esse yoz.")
        
        doc = Document()
        doc.add_heading(message.text, 0)
        doc.add_paragraph(response.text)
        
        path = f"esse_{message.from_user.id}.docx"
        doc.save(path)
        
        await message.answer_document(FSInputFile(path), caption="✅ Esse tayyor!")
        os.remove(path)
    except Exception as e:
        # Xatoni foydalanuvchiga tushunarli qilib ko'rsatish
        await message.answer(f"❌ API Xatosi yuz berdi. Iltimos, bir ozdan so'ng qayta urinib ko'ring.")
        print(f"DEBUG: {e}") # Railway loglarida xatoni ko'rish uchun
    finally:
        await status_msg.delete()
        await state.clear()

# --- TAQDIMOT QISMI ---
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message,
