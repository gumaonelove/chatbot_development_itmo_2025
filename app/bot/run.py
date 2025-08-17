from __future__ import annotations
import os, json, logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from app.core.rag import RAGEngine, format_answer
from app.parsers.html_pages import collect_program_corpus
from app.parsers.study_plan_pdf import fetch_pdf_text
from app.core.models import DocChunk
from app.core.rag import chunk_text
from app.core.recommend import recommend

logging.basicConfig(level=logging.INFO)
load_dotenv()

HELP = (
    "/start — приветствие\n"
    "/compare — сравнить программы\n"
    "/plan — как планировать обучение\n"
    "/recommend — рекомендации элективов (спрошу о бэкграунде)\n"
)

class BotApp:
    def __init__(self):
        self.rag = RAGEngine()
        self.docs: list[DocChunk] = []
        self._warm_up()

    def _warm_up(self):
        corpus = collect_program_corpus()
        for slug, bundle in corpus.items():
            for p in bundle["pages"]:
                self.docs.extend(chunk_text(p["text"], p["url"]))
            for link in bundle.get("plan_links", []):
                try:
                    text = fetch_pdf_text(link)
                    self.docs.extend(chunk_text(text, link))
                except Exception as e:
                    logging.warning("plan fetch failed: %s", e)
        self.rag.build(self.docs)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Здравствуйте! Я помогаю сравнить магистратуры ИТМО: «Искусственный интеллект» и "
            "«Управление ИИ‑продуктами (AI Product)». Задайте вопрос или используйте /compare /plan /recommend."
        )

    async def compare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = "чем отличаются магистратуры искусственный интеллект и управление ии-продуктами?"
        results, s = self.rag.query(q, k=5)
        answer = format_answer(q, results, s)
        await update.message.reply_text(answer)

    async def plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = "как устроено обучение, формат (онлайн/очно), длительность, стоимость и вакансии после?"
        results, s = self.rag.query(q, k=6)
        answer = format_answer(q, results, s)
        await update.message.reply_text(answer)

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.message.text.strip()
        results, s = self.rag.query(q, k=5)
        answer = format_answer(q, results, s)
        await update.message.reply_text(answer)

    async def recommend_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Короткая анкета. Укажите профиль из списка: software_engineer | data_analyst | product_manager | researcher | data_engineer"
        )
        return

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = BotApp()
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", app.start))
    application.add_handler(CommandHandler("compare", app.compare))
    application.add_handler(CommandHandler("plan", app.plan))
    application.add_handler(CommandHandler("recommend", app.recommend_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, app.on_text))

    application.run_polling()

if __name__ == "__main__":
    main()
