import requests
import json
import time
import os
from datetime import datetime

# ===================== КОНСТАНТЫ =====================
# Токен и ID админа берутся из переменных окружения
TOKEN ='8243905366:AAFL4SO3yVpZI9zUkiQOBfZtkdeRP4AhIoY'
ADMIN_ID = 8598334384
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ===================== ХРАНИЛИЩЕ =====================
users = {}  # {user_id: {step: 1, data: {...}}}
applications = {}  # {app_id: {...}}
next_app_id = 1

# ===================== УТИЛИТЫ =====================
def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения"""
    try:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json=payload,
            timeout=10
        )
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return None

def send_inline_keyboard(chat_id, text, buttons):
    """Отправка сообщения с inline-кнопками"""
    keyboard = {
        'inline_keyboard': buttons
    }
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

def edit_message(chat_id, message_id, text, reply_markup=None):
    """Редактирование сообщения"""
    try:
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        requests.post(
            f"{BASE_URL}/editMessageText",
            json=payload,
            timeout=10
        )
    except:
        pass

# ===================== ОБРАБОТЧИКИ =====================
def handle_start(user_id, username, first_name):
    """Обработка команды /start"""
    users[user_id] = {'step': 0, 'data': {}}
    
    keyboard = {
        'keyboard': [
            [{'text': '📝 Подать заявку'}],
            [{'text': 'ℹ️ Информация'}]
        ],
        'resize_keyboard': True
    }
    
    text = f"""<b>👋 Привет, {first_name}!</b>

🤖 Бот для заявок в <b>NoolShy Fame</b>

🎯 Нажми <b>"📝 Подать заявку"</b> чтобы начать"""
    
    send_message(user_id, text, keyboard)

def handle_application_button(user_id):
    """Начало заявки"""
    users[user_id] = {'step': 1, 'data': {}}
    
    text = """<b>📝 ШАГ 1 из 5</b>

💎 <b>Введите ваш НИК:</b>
Как вас будут называть в фейм-листе

<i>Пример: ZorF, Франциско, Madonna Maniac</i>"""
    
    send_message(user_id, text)

def handle_info(user_id):
    """Информация"""
    text = """<b>🎭 NoolShy Fame</b>

🔹 <b>Категории:</b>
• 👑 Владелец
• 📢 Медийки
• 🔥 Высокий фейм
• ⚡ Средний фейм
• 💫 Малый фейм

🔹 <b>Контакты:</b>
@tgzorf - владелец
@NOOLSHY - канал

💎 <b>Для подачи заявки нажмите "📝 Подать заявку"</b>"""
    
    send_message(user_id, text)

def process_user_message(user_id, text):
    """Обработка сообщений пользователя"""
    if user_id not in users:
        return
    
    step = users[user_id]['step']
    data = users[user_id]['data']
    
    # Шаг 1: Ник
    if step == 1:
        data['nickname'] = text
        users[user_id]['step'] = 2
        users[user_id]['data'] = data
        
        send_message(user_id, """<b>📝 ШАГ 2 из 5</b>

👤 <b>Введите ваш юзернейм Telegram:</b>
С @ в начале

<i>Пример: @username</i>""")
    
    # Шаг 2: Юзернейм
    elif step == 2:
        username = text.strip()
        if not username.startswith('@'):
            username = '@' + username
        
        data['username'] = username
        users[user_id]['step'] = 3
        users[user_id]['data'] = data
        
        keyboard = {
            'keyboard': [
                [{'text': 'Медийки'}, {'text': 'Высокий фейм'}],
                [{'text': 'Средний фейм'}, {'text': 'Малый фейм'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, """<b>📝 ШАГ 3 из 5</b>

🏷️ <b>Кем вы себя считаете?</b>
Выберите категорию:""", keyboard)
    
    # Шаг 3: Категория
    elif step == 3:
        if text not in ['Медийки', 'Высокий фейм', 'Средний фейм', 'Малый фейм']:
            send_message(user_id, "❌ Пожалуйста, выберите категорию из предложенных.")
            return
        
        data['category'] = text
        users[user_id]['step'] = 4
        users[user_id]['data'] = data
        
        send_message(user_id, """<b>📝 ШАГ 4 из 5</b>

🔗 <b>Ссылка на ваш проект/канал:</b>
Основной проект, где вас можно найти

<i>Пример: https://t.me/NOOLSHY или @NOOLSHY</i>""")
    
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
        
        send_message(user_id, """<b>📝 ШАГ 5 из 5</b>

🔗 <b>Дополнительные ссылки</b>

Вы можете добавить ссылки на:
• Прайс/Маркет
• TikTok/YouTube
• Discord/VK
• Сайт/Блог

Выберите действие:""", keyboard)
    
    # Шаг 5: Доп ссылки
    elif step == 5:
        if text == '➕ Добавить ссылку':
            users[user_id]['step'] = 'link_type'
            show_link_types(user_id)
        else:
            data['extra_links'] = []
            show_preview(user_id, data)
    
    # Выбор типа ссылки
    elif step == 'link_type':
        if text == '✅ Готово':
            show_preview(user_id, data)
        else:
            users[user_id]['current_link_type'] = text
            users[user_id]['step'] = 'link_url'
            
            send_message(user_id, f"🔗 <b>Введите ссылку для '{text}':</b>\n\n<i>Пример: https://example.com</i>")
    
    # Ввод URL ссылки
    elif step == 'link_url':
        link_type = users[user_id].get('current_link_type', 'Другое')
        link_url = text
        
        if 'extra_links' not in data:
            data['extra_links'] = []
        
        data['extra_links'].append({
            'type': link_type,
            'url': link_url
        })
        
        users[user_id]['data'] = data
        users[user_id]['step'] = 'link_type'
        
        keyboard = {
            'keyboard': [
                [{'text': '➕ Добавить ещё'}, {'text': '✅ Готово'}]
            ],
            'resize_keyboard': True
        }
        
        send_message(user_id, f"✅ <b>Ссылка добавлена!</b>\n📌 Тип: {link_type}\n🔗 URL: {link_url}\n\nДобавить ещё ссылки?", keyboard)

def show_link_types(user_id):
    """Показ типов ссылок"""
    keyboard = {
        'keyboard': [
            [{'text': 'Прайс'}, {'text': 'Маркет'}, {'text': 'TikTok'}],
            [{'text': 'YouTube'}, {'text': 'Discord'}, {'text': 'VK'}],
            [{'text': 'Сайт'}, {'text': 'Блог'}, {'text': 'Другое'}],
            [{'text': '✅ Готово'}]
        ],
        'resize_keyboard': True
    }
    
    send_message(user_id, "📌 <b>Выберите тип ссылки:</b>", keyboard)

def show_preview(user_id, data):
    """Показ превью заявки"""
    preview = f"""<b>📋 ПРЕДПРОСМОТР ЗАЯВКИ</b>

👤 <b>Ник:</b> {data['nickname']}
🔖 <b>Юзернейм:</b> {data['username']}
🏷️ <b>Категория:</b> {data['category']}
🔗 <b>Проект:</b> {data['project']}

"""
    
    if 'extra_links' in data and data['extra_links']:
        preview += "<b>📎 Дополнительные ссылки:</b>\n"
        for link in data['extra_links']:
            preview += f"• {link['type']}: {link['url']}\n"
        preview += "\n"
    
    preview += "<i>Всё верно? Подтвердите отправку.</i>"
    
    keyboard = {
        'keyboard': [
            [{'text': '✅ ОТПРАВИТЬ ЗАЯВКУ'}, {'text': '❌ Отменить'}]
        ],
        'resize_keyboard': True
    }
    
    send_message(user_id, preview, keyboard)
    users[user_id] = {'step': 'confirm', 'data': data}

def handle_send_application(user_id, username):
    """Обработка отправки заявки"""
    if user_id not in users or users[user_id]['step'] != 'confirm':
        send_message(user_id, "❌ Нет данных для отправки. Начните заново.")
        return
    
    data = users[user_id]['data']
    
    # Проверяем обязательные поля
    required = ['nickname', 'username', 'category', 'project']
    for field in required:
        if field not in data or not data[field]:
            send_message(user_id, f"❌ Ошибка: поле '{field}' не заполнено.")
            return
    
    global next_app_id
    
    # Сохраняем заявку
    applications[next_app_id] = {
        'user_id': user_id,
        'username': username,
        'data': data,
        'status': 'pending'
    }
    
    # Отправляем подтверждение пользователю
    send_message(
        user_id,
        f"✅ <b>Заявка #{next_app_id} отправлена!</b>\n\n"
        f"Администратор получил вашу заявку.\n"
        f"Ожидайте решения в течение 1-3 дней.\n\n"
        f"По вопросам: @tgzorf"
    )
    
    print(f"📨 Заявка #{next_app_id} от {user_id}")
    
    # Отправляем админу
    send_application_to_admin(next_app_id, data, user_id, username)
    
    # Увеличиваем счетчик и очищаем
    next_app_id += 1
    del users[user_id]

def send_application_to_admin(app_id, app_data, user_id, username):
    """Отправка заявки админу"""
    admin_text = f"""<b>📨 НОВАЯ ЗАЯВКА #{app_id}</b>

👤 <b>Ник:</b> {app_data['nickname']}
🔖 <b>Юзернейм:</b> {app_data['username']}
🏷️ <b>Категория:</b> {app_data['category']}
🔗 <b>Проект:</b> {app_data['project']}

"""
    
    if 'extra_links' in app_data and app_data['extra_links']:
        admin_text += "<b>📎 Доп. ссылки:</b>\n"
        for link in app_data['extra_links']:
            admin_text += f"• {link['type']}: {link['url']}\n"
        admin_text += "\n"
    
    admin_text += f"""
👤 <b>Отправитель:</b> @{username}
🆔 <b>ID:</b> {user_id}
⏰ <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    # Проверяем что ADMIN_ID установлен
    if not ADMIN_ID:
        print("❌ ADMIN_ID не установлен! Заявка не отправлена админу.")
        return
    
    # Создаем inline-кнопки
    buttons = [[
        {'text': '✅ Принять', 'callback_data': f'accept_{app_id}_{user_id}'},
        {'text': '❌ Отклонить', 'callback_data': f'reject_{app_id}_{user_id}'}
    ]]
    
    send_inline_keyboard(ADMIN_ID, admin_text, buttons)
    print(f"📨 Заявка #{app_id} отправлена админу {ADMIN_ID}")

def handle_callback(callback_id, user_id, data, message_id, chat_id):
    """Обработка callback от админа"""
    print(f"🔘 Callback от {user_id}: {data}")
    
    # Проверяем что это админ
    if user_id != ADMIN_ID:
        answer_callback(callback_id, "❌ Нет прав администратора")
        return
    
    parts = data.split('_')
    if len(parts) < 3:
        answer_callback(callback_id, "❌ Неверный формат")
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
        
        # Уведомляем пользователя
        send_message(
            target_user_id,
            f"🎉 <b>ВАША ЗАЯВКА #{app_id} ПРИНЯТА!</b>\n\n"
            f"Администратор одобрил вашу заявку на вступление в NoolShy Fame.\n\n"
            f"👤 <b>Ваш ник:</b> {app['data']['nickname']}\n"
            f"🏷️ <b>Категория:</b> {app['data']['category']}\n\n"
            f"Добро пожаловать в наше сообщество! 🎭\n\n"
            f"По всем вопросам обращайтесь к @tgzorf"
        )
        
        # Редактируем сообщение у админа
        edit_message(chat_id, message_id, f"✅ <b>Заявка #{app_id} принята</b>\nПользователь уведомлен.")
        
        answer_callback(callback_id, "✅ Заявка принята")
        
    elif action == 'reject':
        applications[app_id]['status'] = 'rejected'
        
        # Уведомляем пользователя
        send_message(
            target_user_id,
            f"❌ <b>ВАША ЗАЯВКА #{app_id} ОТКЛОНЕНА</b>\n\n"
            f"Администратор отклонил вашу заявку на вступление.\n\n"
            f"👤 <b>Ваш ник:</b> {app['data']['nickname']}\n"
            f"🏷️ <b>Категория:</b> {app['data']['category']}\n\n"
            f"<b>Причина:</b> не соответствует требованиям сообщества\n\n"
            f"Вы можете подать новую заявку через 30 дней.\n"
            f"По вопросам обращайтесь к @tgzorf"
        )
        
        # Редактируем сообщение у админа
        edit_message(chat_id, message_id, f"❌ <b>Заявка #{app_id} отклонена</b>\nПользователь уведомлен.")
        
        answer_callback(callback_id, "❌ Заявка отклонена")

# ===================== ГЛАВНЫЙ ЦИКЛ =====================
def main():
    print("=" * 60)
    print("🤖 ЗАПУСК БОТА NoolShy Fame")
    print("=" * 60)
    
    # Проверяем наличие токена
    if not TOKEN:
        print("❌ ОШИБКА: BOT_TOKEN не установлен!")
        print("Добавьте переменную окружения BOT_TOKEN")
        return
    
    if not ADMIN_ID:
        print("⚠️ ВНИМАНИЕ: ADMIN_ID не установлен!")
        print("Заявки не будут отправляться админу")
    
    offset = 0
    
    while True:
        try:
            # Получаем обновления
            response = requests.get(
                f"{BASE_URL}/getUpdates",
                params={'offset': offset, 'timeout': 30},
                timeout=35
            )
            
            if response.status_code != 200:
                print(f"❌ Ошибка API: {response.status_code}")
                time.sleep(5)
                continue
            
            updates = response.json()
            
            if not updates.get('ok'):
                print(f"❌ Ответ не ok: {updates}")
                time.sleep(5)
                continue
            
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                
                # Обработка callback
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
                
                # Обработка сообщений
                if 'message' not in update:
                    continue
                
                message = update['message']
                user_id = message['from']['id']
                username = message['from'].get('username', '')
                first_name = message['from'].get('first_name', '')
                
                # Команда /start
                if 'text' in message and message['text'].startswith('/start'):
                    handle_start(user_id, username, first_name)
                    continue
                
                # Кнопка "Подать заявку"
                if 'text' in message and message['text'] == '📝 Подать заявку':
                    handle_application_button(user_id)
                    continue
                
                # Кнопка "Информация"
                if 'text' in message and message['text'] == 'ℹ️ Информация':
                    handle_info(user_id)
                    continue
                
                # Кнопка "Отправить заявку"
                if 'text' in message and message['text'] == '✅ ОТПРАВИТЬ ЗАЯВКУ':
                    handle_send_application(user_id, username)
                    continue
                
                # Кнопка "Отменить"
                if 'text' in message and message['text'] == '❌ Отменить':
                    if user_id in users:
                        del users[user_id]
                    send_message(user_id, "❌ Заявка отменена.")
                    continue
                
                # Обработка текстовых сообщений
                if 'text' in message:
                    process_user_message(user_id, message['text'])
                    continue
        
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"💥 Ошибка в главном цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
