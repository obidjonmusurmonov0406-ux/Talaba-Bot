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

# API kalitni tekshirish va sozlash
if not TOKEN or not GEMINI_KEY:
    raise ValueError("BOT_TOKEN yoki GEMINI_API_KEY topilmadi!")

genai.configure(api_key=GEMINI_KEY)

# Modelni eng barqaror ko'rinishda tanlash
# v1beta xatosidan qochish uchun 'models/' prefiksini qo'shamiz
model = genai.GenerativeModel('models/gemini-1.5-flash')

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
        "Salom! Men Gemini AI bilan ishlaydigan aqlli yordamchiman. 🎓\n"
        "Tahliliy ishlar tayyorlash uchun xizmatni tanlang:", 
        reply_markup=menu
    )

# --- ESSE ---
@dp.message(F.text == "📝 Sifatli Esse (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring:")

@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    msg = await message.answer("🧠 AI tahlil qilmoqda...")
    try:
        response = model.generate_content(f"{message.text} mavzusida o'zbek tilida akademik esse yoz.")
        doc = Document()
        doc.add_heading(message.text, 0)
        doc.add_paragraph(response.text)
        path = f"esse_{message.from_user.id}.docx"
        doc.save(path)
        await message.answer_document(FSInputFile(path))
        os.remove(path)
    except Exception as e:
        await message.answer("❌ API ulanishda xato. Iltimos, API kalit va mintaqa sozlamalarini tekshiring.")
    await msg.delete()
    await state.clear()

# --- TAQDIMOT ---
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    msg = await message.answer("🎨 Slaydlar tayyorlanmoqda...")
    try:
        prompt = f"'{message.text}' haqida 7 slaydli reja yoz. Har slaydni 'SLAYD:' so'zi bilan ajrat."
        response = model.generate_content(prompt)
        prs = Presentation()
        prs.slide_width, prs.slide_height = 12192000, 6858000
        for data in response.text.split("SLAYD:")[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = message.text
            slide.placeholders[1].text = data.strip()
        path = f"ppt_{message.from_user.id}.pptx"
        prs.save(path)
        await message.answer_document(FSInputFile(path))
        os.remove(path)
    except Exception:
        await message.answer("❌ Taqdimotda xatolik yuz berdi.")
    await msg.delete()
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
