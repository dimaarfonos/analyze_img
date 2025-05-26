
# Makefile

# Имя основного файла Flask-приложения
APP=app.py

# Установка зависимостей
install:
	pip install -r requirements.txt

# Запуск приложения
run:
	FLASK_APP=$(APP) FLASK_ENV=development flask run

# Очистка сгенерированных файлов
clean:
	rm -rf static/*.mp3 static/*.jpg static/*.png static/*.jpeg

# Обновление моделей HuggingFace
update-models:
	python3 -c "from transformers import BlipProcessor, BlipForConditionalGeneration; BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base'); BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')"

# Проверка форматирования (если используешь black)
lint:
	black .
