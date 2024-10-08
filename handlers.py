from moviepy.editor import *
from telegram import Update, InputMediaVideo
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Отправьте мне видео, и я преобразую его в видеокружок.")

async def process_video(update: Update, context: CallbackContext):
    # Отправка сообщения о начале обработки
    await update.message.reply_text("Видео получил, начинаю закруглять, подожди, плз.")

    try:
        video_file = await context.bot.getFile(update.message.video.file_id)
        await video_file.download_to_drive(f"videos/input_video_{update.message.video.file_id}.mp4")
    
        # Prеобразование видео в видеокружок
        input_video = VideoFileClip(f"videos/input_video_{update.message.video.file_id}.mp4")
        w, h = input_video.size
        circle_size = 360
        aspect_ratio = float(w) / float(h)
        
        if w > h:
            new_w = int(circle_size * aspect_ratio)
            new_h = circle_size
        else:
            new_w = circle_size
            new_h = int(circle_size / aspect_ratio)
            
        resized_video = input_video.resize((new_w, new_h))
        output_video = resized_video.crop(x_center=resized_video.w/2, y_center=resized_video.h/2, width=circle_size, height=circle_size)
        # Уменьшение битрейта и разрешения для уменьшения размера файла
        output_video.write_videofile(
            f"videos/output_video_{update.message.video.file_id}.mp4", 
            codec="libx264", 
            audio_codec="aac", 
            bitrate="2M",  # Уменьшаем битрейт
            audio_bitrate="64k",  # Уменьшаем аудиобитрейт
            fps=24,  # Можно снизить FPS для уменьшения размера
            #preset="ultrafast"  # Быстрое сжатие
        )
    
        # Отправка видеокружка в чат
        with open(f"videos/output_video_{update.message.video.file_id}.mp4", "rb") as video:
            await context.bot.send_video_note(chat_id=update.message.chat_id, video_note=video, duration=int(output_video.duration), length=circle_size)
    except Exception as err:
        await update.message.reply_text(f"err: {err}.")
