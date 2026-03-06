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

# Konfiguratsiya
TOKEN = os.getenv("BOT_TOKEN")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=TOKEN)
dp = Dispatcher()

class BotStates(StatesGroup):
    waiting_for_esse = State()
    waiting_for_pptx = State()

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Sifatli Esse (Word)"), KeyboardButton(text="📊 Professional Taqdimot (PPTX)")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Salom! Men Gemini AI yordamida mustaqil ishlaringizni tayyorlayman. 🎓", reply_markup=menu)

@dp.message(F.text == "📝 Sifatli Esse (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring:")

@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    status = await message.answer("🧠 AI esse yozmoqda...")
    try:
        prompt = f"'{message.text}' mavzusida o'zbek tilida akademik esse yoz. Reja, kirish va xulosa bo'lsin."
        response = model.generate_content(prompt)
        doc = Document()
        doc.add_heading(message.text, 0)
        doc.add_paragraph(response.text)
        path = f"{message.text[:10]}.docx"
        doc.save(path)
        await message.answer_document(FSInputFile(path), caption="✅ Esse tayyor!")
        os.remove(path)
    except: await message.answer("❌ Xatolik!")
    await status.delete()
    await state.clear()

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    status = await message.answer("🎨 Taqdimot tayyorlanmoqda...")
    try:
        prompt = f"'{message.text}' mavzusida 5 ta slayd uchun sarlavha va qisqa matn yoz (O'zbekcha). Har bir slaydni 'SLAYD:' so'zi bilan boshla."
        response = model.generate_content(prompt)
        prs = Presentation()
        slides = response.text.split("SLAYD:")
        for s in slides[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            lines = s.strip().split("\n")
            slide.shapes.title.text = lines[0]
            slide.placeholders[1].text = "\n".join(lines[1:])
        path = f"{message.text[:10]}.pptx"
        prs.save(path)
        await message.answer_document(FSInputFile(path), caption="✅ Taqdimot tayyor!")
        os.remove(path)
    except: await message.answer("❌ Xatolik!")
    await status.delete()
    await state.clear()

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
