import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def resolve_url(url: str) -> str:
    try:
        res = requests.head(url, allow_redirects=True, timeout=10)
        return res.url
    except Exception:
        return url

def fetch_tikwm_data(tiktok_url: str):
    clean_url = resolve_url(tiktok_url)
    api_url = "https://www.tikwm.com/api/"
    params = {"url": clean_url, "hd": 1}
    try:
        response = requests.get(api_url, params=params, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("code") == 0:
                return res_json.get("data")
    except Exception:
        pass
    return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me any TikTok video link.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not ("tiktok.com" in text):
        return

    status_msg = await update.message.reply_text("⚡ Analyzing TikTok link...")
    data = fetch_tikwm_data(text)

    if not data:
        await status_msg.edit_text("❌ Data not found or invalid link.")
        return

    author = data.get("author", {})
    nickname = author.get("nickname", "Unknown")
    unique_id = author.get("unique_id", "user")
    region = data.get("region", "US")
    title = data.get("title", "No Title")
    music_info = data.get("music_info", {})
    music_title = music_info.get("title", "original sound")
    
    views = data.get("play_count", 0)
    likes = data.get("digg_count", 0)
    comments = data.get("comment_count", 0)
    shares = data.get("share_count", 0)
    downloads = data.get("download_count", 0)
    video_id = data.get("id", "N/A")

    caption = (
        f"📹 **VIDEO • ANALYTICS**\n\n"
        f"👤 **{nickname}** | 🆔 `{video_id}`\n"
        f"📝 {title}\n"
        f"🎵 {music_title}\n\n"
        f"📊 **Statistics**\n"
        f"• 👁 {views:,} Views\n"
        f"• 💖 {likes:,} Likes\n"
        f"• 💬 {comments:,} Comments\n"
        f"• 🔁 {shares:,} Shares\n"
        f"• 📥 {downloads:,} Downloads\n\n"
        f"ℹ **Info**\n"
        f"• 🌐 Region | {region}\n"
        f"• 👻 Shadow ban | No\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("576p", callback_data="dl_576"),
            InlineKeyboardButton("720p", callback_data="dl_720"),
            InlineKeyboardButton("1080p", callback_data="dl_1080")
        ],
        [
            InlineKeyboardButton("Original", callback_data="dl_orig"),
            InlineKeyboardButton("MP3", callback_data="dl_mp3"),
            InlineKeyboardButton("Cover", callback_data="dl_cover")
        ],
        [
            InlineKeyboardButton("Recheck", callback_data="recheck"),
            InlineKeyboardButton("Shazam", callback_data="shazam")
        ],
        [
            InlineKeyboardButton(f"👤 {unique_id}", url=f"https://www.tiktok.com/@{unique_id}")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    cover_url = data.get("cover")
    
    if cover_url:
        await update.message.reply_photo(photo=cover_url, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
        await status_msg.delete()
    else:
        await status_msg.edit_text(caption, parse_mode="Markdown", reply_markup=reply_markup)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
