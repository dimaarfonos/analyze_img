from flask import Flask, render_template, request, send_file
import pytesseract
import cv2
from pydub import AudioSegment
import time
from gtts import gTTS
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from PIL import Image
from googletrans import Translator
import os
from flask import abort
import shutil
import uuid  # Для генерации уникальных имён файлов

app = Flask(__name__)

# Папка для хранения загруженных файлов и сгенерированных аудио
UPLOAD_FOLDER = 'static_wb'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Конфигурация Flask с указанием папки

# Инициализация переводчика Google Translate
translator = Translator()

# Инициализация модели BLIP для генерации описаний изображений
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

@app.route('/', methods=['GET', 'POST'])


# def copy_image(src, dest):
#     """
#     Копирует изображение из src в dest.
    
#     :param src: Путь к исходному изображению
#     :param dest: Путь к файлу назначения
#     """
#     try:
#         # Проверяем, существует ли исходный файл
#         if not os.path.exists(src):
#             print(f"Исходный файл не найден: {src}")
#             return
        
#         # Копируем изображение
#         shutil.copy2(src, dest)  # copy2 сохраняет метаданные файла
#         print(f"Изображение '{src}' успешно скопировано в '{dest}'")
    
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
# Пример использования



def index():
    result = None
    if request.method == 'POST':
        file = request.files.get('image')  # Получаем файл из формы
        if file:
            # Генерируем уникальное имя для файла, чтобы избежать перезаписи
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)  # Сохраняем файл на диск
            copy_im = f'C:/Users/DIMA/OneDrive - Российский Университет Дружбы Народов/Рабочий стол/project/static/{filename}'
            # copy_image(image_path, copy_im)
            shutil.copy2(image_path, copy_im)
            try:
                # Обрабатываем изображение: распознаём текст или генерируем описание
                result = process_image(image_path)
                # Для отображения изображения в HTML убираем 'static/' из пути
                result['image_path'] = filename
            except Exception as e:
                # В случае ошибки возвращаем её в шаблон
                result = {'error': str(e)}
    # Отрисовываем страницу с результатами (если есть)
    return render_template('index.html', result=result)

def process_image(image_path):
    # Загружаем изображение с помощью OpenCV
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")
    # Конвертируем из BGR (OpenCV формат) в RGB (для pytesseract)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Распознаём текст на изображении (английский язык)
    text = pytesseract.image_to_string(img_rgb, lang='eng')

    if text.strip():  # Если текст есть
        try:
            # Переводим распознанный текст на русский
            translated_text = translator.translate(text, dest='ru').text
            # Генерируем аудио с помощью gTTS
            tts = gTTS(text=translated_text, lang='ru')
            audio_filename = f"speech_{uuid.uuid4().hex}.mp3"
            # audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
            audio_path = f'C:/Users/DIMA/OneDrive - Российский Университет Дружбы Народов/Рабочий стол/project/static/{audio_filename}'
            tts.save(audio_path)  # Сохраняем аудио
            # copy_au = f'C:/Users/DIMA/OneDrive - Российский Университет Дружбы Народов/Рабочий стол/project/static/{audio_filename}'
            # # copy_auage(image_path, copy_au)
            # shutil.copy2(audio_path, copy_au)
            return {
                'type': 'text',
                'original': text,
                'translated': translated_text,
                'audio': audio_filename
            }
        except Exception as e:
            return {'error': f"Ошибка при переводе текста: {e}"}
    else:
        # Если текста нет, пробуем сгенерировать описание сцены с помощью BLIP
        try:
            img_pil = Image.open(image_path).convert('RGB')
            inputs = processor(img_pil, return_tensors="pt")
            out = model.generate(**inputs)
            caption = processor.decode(out[0], skip_special_tokens=True)
            translated_caption = translator.translate(caption, dest='ru').text
            tts = gTTS(text=translated_caption, lang='ru')
            audio_filename = f"caption_{uuid.uuid4().hex}.mp3"
            # audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
            audio_path = f'C:/Users/DIMA/OneDrive - Российский Университет Дружбы Народов/Рабочий стол/project/static/{audio_filename}'
            tts.save(audio_path)
            # copy_au = f'C:/Users/DIMA/OneDrive - Российский Университет Дружбы Народов/Рабочий стол/project/static/{audio_filename}'
            # # copy_auage(image_path, copy_au)
            # shutil.copy2(image_path, copy_au)
            return {
                'type': 'caption',
                'original': caption,
                'translated': translated_caption,
                'audio': audio_filename
            }
        except Exception as e:
            return {'error': f"Ошибка при описании сцены: {e}"}

# Маршрут для отдачи аудиофайлов клиенту
@app.route('/audio/<filename>')
def get_audio(filename):
    audio_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(audio_path):
        abort(404)
    return send_file(audio_path)

if __name__ == '__main__':
    app.run(debug=True)
