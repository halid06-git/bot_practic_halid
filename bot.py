import telebot  # здесь мы импортируем все нужные бибиотеки
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
import db 

bot = telebot.TeleBot(TOKEN) # говорим ему бери токен
temp = {} # здесь мы сохраняем временные данные

def menu(): # короче здесь создаём список из 4 кнопки * их типо отправляет нам как кнопки а не список
    KeyBoard = ReplyKeyboardMarkup(resize_keyboard=True)
    KeyBoard.add(*[KeyboardButton(b) for b in ['Записать день', 'Статистика', 'История', 'Очистить']])
    return KeyBoard

def all_buttons(): # здесь мы создаем цифры который пользователь будет нажимать на них, а отмена так на всякий пожарный
    KeyBoard = ReplyKeyboardMarkup(resize_keyboard=True)
    KeyBoard.add(*[KeyboardButton(str(i)) for i in range(1, 6)])
    KeyBoard.add(KeyboardButton('Отмена'))
    return KeyBoard

@bot.message_handler(commands=['start']) # здесь передаем команду старт после этой команды все начинается он выдаёт Ассаламу алейкум
def start(m):
    bot.send_message(m.chat.id, 'Ассаламу алейкум', reply_markup=menu())

@bot.message_handler(func=lambda m: m.text == 'Записать день') # здесь пользователь нажимает на записать день
def ask(m):
    temp[m.chat.id] = {'step': 'mood'}
    bot.send_message(m.chat.id, 'Настроение 1-5:', reply_markup=all_buttons())

@bot.message_handler(func=lambda m: m.text == 'Отмена') # а это просто так отмена вдруг пользователь передумает
def cancel(m):
    temp.pop(m.chat.id, None)
    bot.send_message(m.chat.id, 'Отмена', reply_markup=menu())

@bot.message_handler(func=lambda m: m.text.isdigit() and 1 <= int(m.text) <= 5) 
def handle(m):
    uid = m.chat.id
    if uid not in temp:
        bot.send_message(uid, 'Жми "Записать день"', reply_markup=menu())
        return
    
    step = temp[uid]['step']
    val = int(m.text)
    
    if step == 'mood':  #  тут логика так работает Адам если пользователь нажал на часы работы, бот автоматом переключается на часы сна и дальше он сохраняет в бд
        temp[uid]['mood'] = val
        temp[uid]['step'] = 'work'
        bot.send_message(uid, 'Часы работы:', reply_markup=all_buttons())
    
    elif step == 'work':
        temp[uid]['work'] = val
        temp[uid]['step'] = 'sleep'
        bot.send_message(uid, 'Часы сна:', reply_markup=all_buttons())
    
    else: 
        temp[uid]['sleep'] = val
        db.save(uid, temp[uid]['mood'], temp[uid]['work'], temp[uid]['sleep'], '')
        del temp[uid]
        bot.send_message(uid, 'Чакх ялар хьун', reply_markup=menu())

@bot.message_handler(func=lambda m: m.text in ['Статистика', 'История', 'Очистить'])
def commands(m):
    uid = m.chat.id 
    
    if m.text == 'Статистика':
        rows = db.get_last7(uid)
        if not rows:
            bot.send_message(uid, 'Нет данных. Запиши хотя бы один день!', reply_markup=menu()) # здесь выдает это если пользователь ничего не записал за день 
            return
        
        moods = [r[0] for r in rows]
        works = [r[1] for r in rows]
        sleeps = [r[2] for r in rows]
        
        avg_mood = sum(moods) / len(moods)
        avg_work = sum(works) / len(works)
        avg_sleep = sum(sleeps) / len(sleeps)
        
        good, bad = db.get_insight(uid)
        
        msg = f"📊 Статистика за 7 дней:\n"
        msg += f"Настроение: {avg_mood:.1f}/5\n"
        msg += f"Работа: {avg_work:.1f} ч\n"
        msg += f"Сон: {avg_sleep:.1f} ч" # тут он берет часы сна который пользователь спал больше и меньше 7 часов и потом делит
        
        if good > 0 and bad > 0 and good > bad:
            msg += f"\n\n💡 Когда спишь больше 7 часов, настроение выше на {good - bad:.1f} балла"
        
        bot.send_message(uid, msg, reply_markup=menu())
    
    elif m.text == 'История':
        rows = db.get_history(uid)
        if rows:
            msg = "Твои записи:\n\n"
            for r in rows[-5:]:
                msg += f"{r[0]} | Настроение: {r[1]} | Работа: {r[2]} ч | Сон: {r[3]} ч\n"
                msg += "---\n"
            bot.send_message(uid, msg, reply_markup=menu())
        else:
            bot.send_message(uid, 'Нет записей. Начни вести дневник!', reply_markup=menu())
    
    elif m.text == 'Очистить':
        db.clear(uid)
        bot.send_message(uid, 'Все данные удалены!', reply_markup=menu())

@bot.message_handler(func=lambda m: True)
def other(m):
    bot.send_message(m.chat.id, '👆 Используй кнопки меню', reply_markup=menu())

print('Заходи в тг и проверяй Адам!😀')
bot.infinity_polling()