import os
import asyncio
import wikipedia
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from docx import Document
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
wikipedia.set_lang("uz")

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 Esse yozish (Word)"), KeyboardButton(text="📊 Taqdimot (PPTX)")],
    [KeyboardButton(text="ℹ️ Yordam")]
], resize_keyboard=True)

# --- WORD (ESSE) YARATISH ---
def create_word(title, content):
    doc = Document()
    doc.add_heading(title, 0)
    doc.add_heading("REJA:", level=1)
    doc.add_paragraph("1. Kirish\n2. Asosiy qism\n3. Xulosa")
    doc.add_heading("MATN:", level=1)
    doc.add_paragraph(content)
    path = f"{title}.docx"
    doc.save(path)
    return path

# --- DIZAYNLI TAQDIMOT YARATISH ---
def create_pptx(title, content):
    prs = Presentation()
    
    # 1-Slayd (Titul)
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_shape = slide.shapes.title
    title_shape.text = title
    # Rang berish
    title_shape.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102) # To'q ko'k
    slide.shapes.placeholders[1].text = "Tayyorladi: Aqlli Talaba Boti"

    # 2-Slayd (Ma'lumot)
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Mavzu tahlili"
    body = slide.shapes.placeholders[1]
    body.text = content[:700] # Slaydga ko'p matn sig'maydi
    
    path = f"{title}.pptx"
    prs.save(path)
    return path

@dp.message(F.text == "📝 Esse yozish (Word)")
async def esse_req(msg: types.Message):
    await msg.answer("📝 Esse mavzusini yuboring:")

@dp.message(F.text == "📊 Taqdimot (PPTX)")
async def pptx_req(msg: types.Message):
    await msg.answer("📊 Taqdimot mavzusini yuboring:")

@dp.message()
async def handle_docs(message: types.Message):
    if message.text in ["ℹ️ Yordam", "📝 Esse yozish (Word)", "📊 Taqdimot (PPTX)"]: return
    
    status = await message.answer("🔍 Ma'lumot qidirilmoqda va fayl shakllantirilmoqda...")
    try:
        search = wikipedia.search(message.text)
        page = wikipedia.page(search[0])
        full_text = page.content # Esse uchun uzunroq matn
        
        # Word yoki PPTX ekanini aniqlash (oddiy mantiq)
        if len(full_text) > 0:
            word_path = create_word(page.title, full_text[:3000]) # Word uchun uzun matn
            ppt_path = create_pptx(page.title, page.summary)    # PPTX uchun qisqa matn
            
            # Ikkalasini ham yuboramiz yoki tanlovga qarab (hozircha ikkalasini yuboradi)
            await message.answer_document(FSInputFile(word_path), caption="📄 Esse (Word) tayyor!")
            await message.answer_document(FSInputFile(ppt_path), caption="📊 Taqdimot (PPTX) tayyor!")
            
            os.remove(word_path)
            os.remove(ppt_path)
            await status.delete()
            
    except:
        await status.edit_text("❌ Mavzu bo'yicha ma'lumot yetarli emas. Boshqa mavzu yozing.")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
