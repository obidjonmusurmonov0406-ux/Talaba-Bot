import os
import asyncio
import wikipedia
from pptx import Presentation
from docx import Document
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
wikipedia.set_lang("uz")

# Bot holatlarini belgilaymiz (Esse yoki Taqdimot kutish uchun)
class BotStates(StatesGroup):
    waiting_for_esse = State()
    waiting_for_pptx = State()

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Esse yozish (Word)"), KeyboardButton(text="📊 Taqdimot (PPTX)")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear() # Holatni tozalaymiz
    await message.answer("Salom! Men endi aqlliroqman. 🎓\nPastdagi tugmalardan birini tanlang:", reply_markup=menu)

@dp.message(F.text == "📝 Esse yozish (Word)")
async def esse_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_esse)
    await message.answer("📝 Esse mavzusini yuboring (Masalan: Alisher Navoiy):")

@dp.message(F.text == "📊 Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring (Masalan: Astronomiya):")

# FAQAT ESSE UCHUN ISHLAYDI
@dp.message(BotStates.waiting_for_esse)
async def handle_esse(message: types.Message, state: FSMContext):
    status = await message.answer("🔍 Esse tayyorlanmoqda...")
    try:
        search = wikipedia.search(message.text)
        page = wikipedia.page(search[0])
        
        doc = Document()
        doc.add_heading(page.title, 0)
        doc.add_paragraph(page.content[:4000]) # Wordga uzun matn
        path = f"{page.title}.docx"
        doc.save(path)
        
        await message.answer_document(FSInputFile(path), caption="✅ Esse tayyor!")
        os.remove(path)
    except:
        await message.answer("❌ Ma'lumot topilmadi.")
    await status.delete()
    await state.clear()

# FAQAT TAQDIMOT UCHUN ISHLAYDI
@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    status = await message.answer("📊 Taqdimot tayyorlanmoqda...")
    try:
        search = wikipedia.search(message.text)
        page = wikipedia.page(search[0])
        
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = page.title
        slide.shapes.placeholders[1].text = "Taqdimot tayyorladi: Aqlli Bot"
        
        # 2-slayd
        slide2 = prs.slides.add_slide(prs.slide_layouts[1])
        slide2.shapes.title.text = "Asosiy ma'lumot"
        slide2.shapes.placeholders[1].text = page.summary[:1000]
        
        path = f"{page.title}.pptx"
        prs.save(path)
        
        await message.answer_document(FSInputFile(path), caption="✅ Taqdimot tayyor!")
        os.remove(path)
    except:
        await message.answer("❌ Ma'lumot topilmadi.")
    await status.delete()
    await state.clear()
    
async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
