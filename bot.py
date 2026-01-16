import requests
import json
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = "8234313919:AAH4COsuFFpAu9Vew0nFO7FhKQFxBXJQVg0"
ADMIN_ID = 287265398
OWNER_USERNAME = "@tgzorf"
CHANNEL_USERNAME = "@NOOLSHY"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Хранилище (в памяти - для теста)
users = {}
applications = {}
next_app_id = 1

# Категории
CATEGORIES = ["Медийки", "Высокий фейм", "Средний фейм", "Малый фейм"]

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения"""
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Ошибка отправки: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return None

def send_inline_keyboard(chat_id, text, buttons):
    """Отправка inline клавиатуры"""
    keyboard = {'inline_keyboard': buttons}
    return send_message(chat_id, text, keyboard)

def answer_callback(callback_id, text=None):
    """Ответ на callback"""
    try:
        payload = {'callback_query_id': callback_id}
        if text:
            payload['text'] = text
        
        requests.post(
            f"{BASE_URL}/answerCallbackQuery",
            json=payload,
            timeout=5
        )
    except:
        pass

def handle_start(user_id, first_name):
    """Обработка /start"""
    users[user_id] = {'step': 0, 'data': {}}
    
    welcome = f"""<b>👋 Привет, {first_name}!</b>

🤖 <b>Бот для заявок в NoolShy Fame</b>

🎯 <b>Нажми "📝 Подать заявку"</b> чтобы начать

👑 <b>Владелец:</b> {OWNER_USERNAME}
🔗 <b>Канал:</b> {CHANNEL_USERNAME}"""
    
    keyboard = {
        'keyboard': [
            [{'text': '📝 Подать заявку'}],
            [{'text': 'ℹ️ Информация'}, {'text': '📜 Правила'}]
        ],
        'resize_keyboard': True
    }
    
    send_message(user_id, welcome, keyboard)
    logger.info(f"Пользователь {user_id} начал работу")

def handle_info(user_id):
    """Информация о сообществе"""
    text = f"""<b>🎭 NoolShy Fame</b>

<b>Категории:</b>
• 📢 Медийки - известные личности
• 🔥 Высокий фейм - популярные в кругах
• ⚡ Средний фейм - активные участники
• 💫 Малый фейм - начинающие

<b>Контакты:</b>
• Владелец: {OWNER_USERNAME}
• Канал: {CHANNEL_USERNAME}

Для подачи заявки нажмите "📝 Подать заявку" """
    
    send_message(user_id, text)

def handle_rules(user_id):
    """Правила"""
    text = f"""<b>📜 Правила использования бота</b>

1. Запрещен спам и флуд
2. Информация должна быть достоверной
3. Одна заявка на человека
4. Соблюдение правил Telegram
5. Контент должен быть легальным

👑 <b>Администратор:</b> {OWNER_USERNAME}"""
    
    send_message(user_id, text)

def start_application(user_id):
    """Начало заявки"""
    users[user_id] = {'step': 1, 'data': {}}
    send_message(user_id, "<b>📝 ШАГ 1 из 5</b>\n\n💎 <b>Введите ваш НИК:</b>\n<i>Пример: ZorF, Madonna Maniac</i>")

def process_step(user_id, text):
    """Обработка шагов заявки"""
    if user_id not in users:
        return
    
    step = users[user_id]['step']
    data = users[user_id]['data']
    
    # Шаг 1: Ник
    if step == 1:
        if len(text) < 2 or len(text) > 20:
            send_message(user_id, "❌ Ник должен быть от 2 до 20 символов")
            return
        
        data['nickname'] = text
        users[user_id]['step'] = 2
        users[user_id]['data'] = data
        send_message(user_id, "<b>📝 ШАГ 2 из 5</b>\n\n👤 <b>Введите юзернейм:</b>\n<i>Пример: @username или просто username</i>")
    
    # Шаг 2: Юзернейм
    elif step == 2:
        username = text.strip()
        if not username.startswith('@'):
            username = '@' + username
        
        data['username'] = username
        users[user_id]['step'] = 3
        users[user_id]['data'] = data
        
        keyboard = {
            'keyboard': [[{'text': cat} for cat in CATEGORIES]],
            'resize_keyboard': True
        }
        
        send_message(user_id, "<b>📝 ШАГ 3 из 5</b>\n\n🏷️ <b>Выберите категорию:</b>", keyboard)
    
    # Шаг 3: Категория
    elif step == 3:
        if text not in CATEGORIES:
            send_message(user_id, "❌ Выберите категорию из предложенных")
            return
        
        data['category'] = text
        users[user_id]['step'] = 4
        users[user_id]['data'] = data
        send_message(user_id, "<b>📝 ШАГ 4 из 5</b>\n\n🔗 <b>Ссылка на проект:</b>\n<i>Пример: https://t.me/NOOLSHY или @NOOLSHY</i>")
    
    # Шаг 4: Проект
    elif step == 4:
        data['project'] = text
        users[user_id]['step'] = 5
        users[user_id]['data'] = data
        
        keyboard = {
            'keyboard': [
                [{'text': '➕ Добавить ссылку'}, {'text': '➡️ Пропустить'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, "<b>📝 ШАГ 5 из 5</b>\n\n🔗 <b>Доп. ссылки (необязательно):</b>\nНажмите '➕ Добавить ссылку' или '➡️ Пропустить'", keyboard)
    
    # Шаг 5: Доп ссылки
    elif step == 5:
        if text == '➕ Добавить ссылку':
            users[user_id]['step'] = 'waiting_link'
            send_message(user_id, "🔗 <b>Введите ссылку:</b>\n<i>Пример: https://example.com</i>")
        else:
            data['extra_links'] = []
            show_preview(user_id, data)
    
    # Ожидание ссылки
    elif step == 'waiting_link':
        if 'extra_links' not in data:
            data['extra_links'] = []
        
        data['extra_links'].append(text)
        users[user_id]['step'] = 'add_more_links'
        users[user_id]['data'] = data
        
        keyboard = {
            'keyboard': [
                [{'text': '➕ Добавить ещё'}, {'text': '✅ Готово'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, f"✅ <b>Ссылка добавлена!</b>\n\nДобавить ещё или завершить?", keyboard)
    
    # Добавить еще ссылок
    elif step == 'add_more_links':
        if text == '➕ Добавить ещё':
            users[user_id]['step'] = 'waiting_link'
            send_message(user_id, "🔗 <b>Введите следующую ссылку:</b>")
        else:
            show_preview(user_id, data)

def show_preview(user_id, data):
    """Показ предпросмотра заявки"""
    preview = f"""<b>📋 ПРЕДПРОСМОТР ЗАЯВКИ</b>

👤 <b>Ник:</b> {data['nickname']}
🔖 <b>Юзернейм:</b> {data['username']}
🏷️ <b>Категория:</b> {data['category']}
🔗 <b>Проект:</b> {data['project']}"""
    
    if 'extra_links' in data and data['extra_links']:
        preview += "\n\n<b>📎 Доп. ссылки:</b>\n"
        for link in data['extra_links']:
            preview += f"• {link}\n"
    
    preview += f"\n<i>Всё верно? Подтвердите отправку</i>"
    
    keyboard = {
        'keyboard': [
            [{'text': '✅ ОТПРАВИТЬ ЗАЯВКУ'}, {'text': '❌ Отменить'}]
        ],
        'resize_keyboard': True
    }
    
    send_message(user_id, preview, keyboard)
    users[user_id] = {'step': 'confirm', 'data': data}

def submit_application(user_id, username):
    """Отправка заявки"""
    if user_id not in users or users[user_id]['step'] != 'confirm':
        send_message(user_id, "❌ Нет данных для отправки")
        return
    
    global next_app_id
    data = users[user_id]['data']
    
    # Сохраняем заявку
    applications[next_app_id] = {
        'user_id': user_id,
        'username': username,
        'data': data,
        'status': 'pending',
        'time': datetime.now().strftime('%d.%m.%Y %H:%M')
    }
    
    # Уведомляем пользователя
    send_message(user_id, f"✅ <b>Заявка #{next_app_id} отправлена!</b>\n\nАдминистратор получил вашу заявку. Ожидайте ответа 1-3 дня.")
    
    # Отправляем админу
    send_to_admin(next_app_id, data, user_id, username)
    
    # Очищаем
    del users[user_id]
    next_app_id += 1

def send_to_admin(app_id, data, user_id, username):
    """Отправка заявки администратору"""
    admin_text = f"""<b>📨 НОВАЯ ЗАЯВКА #{app_id}</b>

👤 <b>Ник:</b> {data['nickname']}
🔖 <b>Юзернейм:</b> {data['username']}
🏷️ <b>Категория:</b> {data['category']}
🔗 <b>Проект:</b> {data['project']}"""
    
    if 'extra_links' in data and data['extra_links']:
        admin_text += "\n\n<b>📎 Доп. ссылки:</b>\n"
        for link in data['extra_links']:
            admin_text += f"• {link}\n"
    
    admin_text += f"\n👤 <b>Отправитель:</b> @{username}"
    admin_text += f"\n🆔 <b>ID:</b> {user_id}"
    admin_text += f"\n⏰ <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    buttons = [[
        {'text': '✅ Принять', 'callback_data': f'accept_{app_id}_{user_id}'},
        {'text': '❌ Отклонить', 'callback_data': f'reject_{app_id}_{user_id}'}
    ]]
    
    send_inline_keyboard(ADMIN_ID, admin_text, buttons)
    logger.info(f"Заявка #{app_id} отправлена админу")

def handle_callback(callback_id, user_id, data, message_id, chat_id):
    """Обработка callback от админа"""
    if user_id != ADMIN_ID:
        answer_callback(callback_id, "❌ Нет прав администратора")
        return
    
    parts = data.split('_')
    if len(parts) < 3:
        return
    
    action = parts[0]
    app_id = int(parts[1])
    target_user_id = int(parts[2])
    
    if app_id not in applications:
        answer_callback(callback_id, "❌ Заявка не найдена")
        return
    
    app = applications[app_id]
    
    if action == 'accept':
        applications[app_id]['status'] = 'accepted'
        send_message(target_user_id, f"🎉 <b>ВАША ЗАЯВКА #{app_id} ПРИНЯТА!</b>\n\nДобро пожаловать в NoolShy Fame! 🎭")
        send_message(chat_id, f"✅ Заявка #{app_id} принята", message_id=message_id)
        answer_callback(callback_id, "✅ Заявка принята")
        
    elif action == 'reject':
        applications[app_id]['status'] = 'rejected'
        send_message(target_user_id, f"❌ <b>ВАША ЗАЯВКА #{app_id} ОТКЛОНЕНА</b>\n\nОбратитесь к администратору: {OWNER_USERNAME}")
        send_message(chat_id, f"❌ Заявка #{app_id} отклонена", message_id=message_id)
        answer_callback(callback_id, "❌ Заявка отклонена")

def edit_message(chat_id, message_id, text):
    """Редактирование сообщения"""
    try:
        requests.post(
            f"{BASE_URL}/editMessageText",
            json={
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text,
                'parse_mode': 'HTML'
            }
        )
    except:
        pass

def main():
    """Главный цикл бота"""
    print("🤖 Запуск бота NoolShy Fame")
    print(f"👑 Владелец: {OWNER_USERNAME}")
    print(f"🆔 Admin ID: {ADMIN_ID}")
    print("⏳ Ожидание обновлений...")
    
    offset = 0
    
    try:
        # Проверяем бота
        resp = requests.get(f"{BASE_URL}/getMe")
        if resp.status_code == 200:
            bot_info = resp.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['first_name']
                print(f"✅ Бот '{bot_name}' запущен!")
            else:
                print(f"❌ Ошибка: {bot_info}")
                return
        else:
            print(f"❌ Ошибка подключения: {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    while True:
        try:
            # Получаем обновления
            response = requests.get(
                f"{BASE_URL}/getUpdates",
                params={'offset': offset, 'timeout': 30},
                timeout=35
            )
            
            if response.status_code != 200:
                print(f"❌ Ошибка: {response.status_code}")
                time.sleep(5)
                continue
            
            updates = response.json()
            
            if not updates.get('ok'):
                print(f"❌ Ответ не ok: {updates}")
                time.sleep(5)
                continue
            
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                
                # Callback от админа
                if 'callback_query' in update:
                    callback = update['callback_query']
                    callback_id = callback['id']
                    user_id = callback['from']['id']
                    data = callback['data']
                    message = callback.get('message', {})
                    message_id = message.get('message_id')
                    chat_id = message.get('chat', {}).get('id')
                    
                    handle_callback(callback_id, user_id, data, message_id, chat_id)
                    continue
                
                # Сообщения
                if 'message' not in update:
                    continue
                
                message = update['message']
                user_id = message['from']['id']
                username = message['from'].get('username', '')
                first_name = message['from'].get('first_name', '')
                
                # Команда /start
                if 'text' in message and message['text'].startswith('/start'):
                    handle_start(user_id, first_name)
                    continue
                
                # Кнопки
                if 'text' in message:
                    text = message['text']
                    
                    if text == '📝 Подать заявку':
                        start_application(user_id)
                        continue
                    
                    elif text == 'ℹ️ Информация':
                        handle_info(user_id)
                        continue
                    
                    elif text == '📜 Правила':
                        handle_rules(user_id)
                        continue
                    
                    elif text == '✅ ОТПРАВИТЬ ЗАЯВКУ':
                        submit_application(user_id, username)
                        continue
                    
                    elif text == '❌ Отменить':
                        if user_id in users:
                            del users[user_id]
                        send_message(user_id, "❌ Заявка отменена")
                        continue
                    
                    # Обработка текста
                    process_step(user_id, text)
                    
        except requests.exceptions.Timeout:
            continue
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
            break
        except Exception as e:
            print(f"💥 Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()