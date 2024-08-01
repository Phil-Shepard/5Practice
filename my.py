import logging
import requests
import telebot
import json
import os
import base64

# Эндпоинты сервиса и данные для аутентификации
API_TOKEN = os.environ['TELEGRAM_TOKEN']
my_vision_url = 'https://myapi.com/vision'
my_token = 'my_api_token'

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(API_TOKEN, threaded=False)

#обработчик события
def process_event(event):
    request_body_dict = json.loads(event['body'])
    update = telebot.types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])

#платформа обработичк
def handler(event, context):
    process_event(event)
    return {
        'statusCode': 200
    }

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Бот умеет распознавать текст с картинок.")


@bot.message_handler(func=lambda message: True, content_types=['photo'])
def echo_photo(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    image_data = base64.b64encode(downloaded_file).decode('utf-8')
    response_text = image_analyze(my_vision_url, my_token, image_data)
    bot.reply_to(message, response_text)

def image_analyze(vision_url, my_token, image_data):
    response = requests.post(vision_url, headers={'Authorization': 'Bearer ' + my_token}, json={
        "image_data": image_data
    })
    result = response.json()
    text = result.get('text', 'Распознавание текста не удалось.')
    return text

if __name__ == '__main__':
    bot.polling(none_stop=True)
