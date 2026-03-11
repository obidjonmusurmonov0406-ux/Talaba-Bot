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

# Gemini AI ulanishini eng barqaror v1 versiyasiga majburlaymiz
genai.configure(api_key=GEMINI_KEY)

# Modelni xatosiz aniqlash funksiyasi
def get_gemini_model():
    # v1beta xatosidan qochish uchun eng oddiy model nomidan foydalanamiz
    return genai.GenerativeModel('gemini-1.5-flash-latest')

model = get_gemini_model()

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
    msg = await message.answer("🧠 AI akademik esse yozmoqda...")
    try:
        response = model.generate_content(f"{message.text} mavzusida o'zbek tilida esse yoz.")
        doc = Document()
        doc.add_heading(message.text, 0)
        doc.add_paragraph(response.text)
        
        file_path = f"esse_{message.from_user.id}.docx"
        doc.save(file_path)
        await message.answer_document(FSInputFile(file_path), caption="✅ Esse tayyor!")
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Xato: API bilan ulanishda muammo bo'ldi. Birozdan so'ng qayta urinib ko'ring.")
    await msg.delete()
    await state.clear()

# --- TAQDIMOT YARATISH ---
@dp.message(F.text == "📊 Professional Taqdimot (PPTX)")
async def pptx_req(message: types.Message, state: FSMContext):
    await state.set_state(BotStates.waiting_for_pptx)
    await message.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message(BotStates.waiting_for_pptx)
async def handle_pptx(message: types.Message, state: FSMContext):
    msg = await message.answer("🎨 Professional slaydlar tayyorlanmoqda...")
    try:
        prompt = f"'{message.text}' mavzusida 7 ta slayd uchun matn yoz. Har bir slaydni 'SLAYD:' so'zi bilan ajrat."
        response = model.generate_content(prompt)
        
        prs = Presentation()
        prs.slide_width, prs.slide_height = 12192000, 6858000 # 16:9
        
        slides_data = response.text.split("SLAYD:")
        for data in slides_data[1:]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            lines = data.strip().split("\n")
            if lines:
                slide.shapes.title.text = lines[0].replace(":", "").strip()
                slide.placeholders[1].text = "\n".join(lines[1:]).strip()

        file_path = f"ppt_{message.from_user.id}.pptx"
        prs.save(file_path)
        await message.answer_document(FSInputFile(file_path), caption="✅ Taqdimot tayyor!")
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Xato: Taqdimot yaratib bo'lmadi.")
    await msg.delete()
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
