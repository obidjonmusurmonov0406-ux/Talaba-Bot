import os
import asyncio
import google.generativeai as genai
from pptx import Presentation
from pptx.util import Inches, Pt
from docx import Document
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# --- KONFIGURATSIYA ---
# Railway Variables'dan o'zgaruvchilarni olish
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not TOKEN or not GEMINI_KEY:
    raise ValueError("XATO: Railway Variables (BOT_TOKEN yoki GEMINI_API_KEY) topilmadi!")

# Gemini AI ulanishi
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Bot holatlari
class BotStates(StatesGroup):
    waiting_for_esse = State()
    waiting_for_pptx = State()

# --- ASOSIY MENYU ---
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Sifatli Esse (Word)")],
    [KeyboardButton(text="📊 Professional Taqdimot (PPTX)")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Salom! Men Gemini AI yordamida mustaqil ishlaringizni professional darajada tayyorlayman. 🎓\n\n"
        "Quyidagilardan birini tanlang:", 
        reply_markup=menu
    )

# --- ESSE YARATISH (WORD) ---
@dp.message(F.text == "📝 Sifatli Esse (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring (Masalan: 'O'zbekistonning iqtisodiy rivojlanishi'):")

@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    msg = await message.answer("🧠 AI mavzuni tahlil qilmoqda va esse yozmoqda...")
    try:
        prompt = (
            f"'{message.text}' mavzusida o'zbek tilida akademik esse yoz. "
            f"Tuzilishi: Reja, Kirish, 3 ta asosiy tahliliy qism va Xulosa bo'lsin. "
            f"Matn mazmunli va kamida 500 ta so'zdan iborat bo'lsin."
        )
        response = model.generate_content(prompt)
        
        doc = Document()
        doc.add_heading(message.text, 0)
        
        # Matnni qismlarga bo'lib chiroyli yozish
        paragraphs = response.text.split('\n')
        for p in paragraphs:
            if p.strip():
                doc.add_paragraph(p.strip())
        
        file_path = f"{message.text[:10]}_esse.docx"
        doc.save(file_path)
        
        await message.answer_document(FSInputFile(file_path), caption=f"✅ '{message.text}' bo'yicha esse tayyor!")
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Esse yaratishda xato: {str(e)}")
    
    await msg.delete()
    await state.clear()

# --- TAQDIMOT YARATISH (PPTX) ---
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    msg = await message.answer("🎨 Professional slaydlar tayyorlanmoqda, kuting...")
    try:
        prompt = (
            f"'{message.text}' mavzusida 7 ta slayddan iborat professional taqdimot rejasi yoz. "
            f"Har bir slaydni 'SLAYD:' so'zi bilan boshla. "
            f"Slaydlar tarkibi: 1
