import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me any TikTok video link, and I will download it without watermark.")

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "tiktok.com" not in url:
        return

    msg = await update.message.reply_text("⏳ Processing video, please wait...")

    try:
        # Resolve short URL if necessary
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # TikWM API Request
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = session.get(api_url, timeout=15)
        res = response.json()

        if res.get("code") == 0:
            video_url = res["data"]["play"]
            title = res["data"].get("title", "TikTok Video")

            # Direct video URL stream send to avoid server memory overload
            await update.message.reply_video(
                video=video_url,
                caption=f"✨ {title}\n\nDownloaded via TikTok Bot"
            )
            await msg.delete()
        else:
            await msg.edit_text("❌ Video not found. Please check if the link is valid.")

    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        await msg.edit_text("❌ Failed to download video. Please try again later.")

def main():
    if not TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN not found!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    
    logging.info("Bot execution started...")
    app.run_polling()

if __name__ == '__main__':
    main()

