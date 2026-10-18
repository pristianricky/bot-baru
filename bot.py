
import os
import re
import logging
import httpx

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("BACKEND_API_KEY", "")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🧰 Tools", callback_data="tools"),
        InlineKeyboardButton("🧮 Kalkulator", callback_data="calc"),
    ],
    [
        InlineKeyboardButton("ℹ️ Info Bot", callback_data="info"),
        InlineKeyboardButton("💚 Status API", callback_data="health"),
    ],
])


async def api_get(path):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{API_URL}{path}")
        response.raise_for_status()
        return response.json()


async def api_post(path, payload):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{API_URL}/calculate",
            json=payload,
            headers={"X-API-Key": API_KEY},
        )
        response.raise_for_status()
        return response.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "🔥 CKYY MULTIFUNCTION BOT\n\nPilih menu di bawah:",
        reply_markup=MENU,
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "/start - Menu utama\n"
        "/help - Bantuan\n"
        "/id - ID Telegram\n"
        "/hitung 10 + 5 - Kalkulator"
    )


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"ID Telegram: {update.effective_user.id}"
    )


async def hitung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expression = " ".join(context.args)
    match = re.fullmatch(
        r"(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)",
        expression,
    )

    if not match:
        await update.effective_message.reply_text(
            "Format: /hitung 10 + 5"
        )
        return

    a, op, b = float(match[1]), match[2], float(match[3])

    try:
        data = await api_post(
            "/calculate", {"a": a, "b": b, "op": op}
        )
        await update.effective_message.reply_text(
            f"🧮 Hasil: {data['result']:g}"
        )
    except httpx.HTTPStatusError as e:
        detail = "Perhitungan gagal."
        try:
            detail = e.response.json().get("detail", detail)
        except ValueError:
            pass
        await update.effective_message.reply_text(detail)
    except httpx.HTTPError:
        await update.effective_message.reply_text(
            "API belum aktif atau tidak bisa dihubungi."
        )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "home":
        await query.edit_message_text(
            "🔥 CKYY MULTIFUNCTION BOT\nPilih menu:",
            reply_markup=MENU,
        )
        return

    if query.data == "tools":
        text = "🧰 TOOLS\n\n• Kalkulator\n• Info bot\n• Status API"
    elif query.data == "calc":
        text = "🧮 Kirim perintah:\n/hitung 10 + 5"
    elif query.data == "info":
        try:
            data = await api_get("/info")
            text = (
                f"🤖 {data['name']}\n"
                f"Versi: {data['version']}\n"
                f"Fitur: {', '.join(data['features'])}"
            )
        except httpx.HTTPError:
            text = "API belum aktif."
    elif query.data == "health":
        try:
            data = await api_get("/health")
            text = f"💚 Backend: {data['status']}"
        except httpx.HTTPError:
            text = "🔴 Backend tidak bisa dihubungi."
    else:
        text = "Menu tidak dikenal."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali", callback_data="home")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard)


def main():
    if not TOKEN or not API_KEY:
        raise RuntimeError("Token bot atau BACKEND_API_KEY belum diatur.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("hitung", hitung))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()


if __name__ == "__main__":
    main()
  
