from threading import Thread
#-------------------------
import telebot
from telebot import types,util
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#-------------------------
import db
import base_functions as bf
from base_functions import log
#-------------------------
TOKEN = '' #bot token
bot = telebot.TeleBot(TOKEN)
#-------------------------
db.create_tables()
bf.init_logs()
bot_data = bot.get_me()
#-------------------------
upd_time = 5     #CHECK LOOP TIMER (in secs)
Thread(target=bf.checker_loop,args=[bot,upd_time]).start()
#-------------------------
@bot.message_handler(commands=['start'])
def command_start(m):
    try:
        cid = m.chat.id
        chat_type = m.chat.type
        username = m.chat.username

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton('➕Добавить'), types.KeyboardButton('📂Список'))
        bot.send_message(cid,f'🤖{bot_data.username}💬', reply_markup=markup)

    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: message.text == '➕Добавить')
def command_rules(m):
    try:
        cid = m.chat.id
        bot.send_message(cid,'🤖Для добавления нового отслеживаания, укажите адрес кошелька и его название <b>через пробел</b>, например:\n\n<code>3PB397Z2Yf9ZwvMRNFqhdb84cDk4nQYM4W WalletName</code>', parse_mode='HTML')
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: message.text == '📂Список')
def command_rules(m):
    try:
        cid = m.chat.id
        wallets = db.get_all_user_wallets(cid)
        if wallets == []:
            bot.send_message(cid,'🤖Список пуст', parse_mode='HTML')
            return

        markup = types.InlineKeyboardMarkup()
        for wallet_data in wallets:
            markup.row(InlineKeyboardButton(f"{wallet_data['nick']}", callback_data=f"show_wallet-{str(wallet_data['id'])}"), InlineKeyboardButton(f"❌", callback_data=f"delete_wallet-{str(wallet_data['id'])}"))

        bot.send_message(cid,'🤖Список добавленых кошельков', parse_mode='HTML',reply_markup=markup)
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    try:
        cid = m.chat.id
        text = m.text

        try:
            wallet = text.split(' ')[0]
            nick = text.split(' ')[1]
        except:
            bot.send_message(cid,'❌Не верная форма записи! Смотрите пример:\n\n<code>3PB397Z2Yf9ZwvMRNFqhdb84cDk4nQYM4W WalletName</code>', parse_mode='HTML')
            return

        if len(wallet) < 25:
            bot.send_message(cid,'❌Не верная форма записи! Смотрите пример:\n\n<code>3PB397Z2Yf9ZwvMRNFqhdb84cDk4nQYM4W WalletName</code>', parse_mode='HTML')
            return

        check = bf.check_address(wallet)

        if not check[0]:
            bot.send_message(cid,'❌Введён неверный биткойн адрес!', parse_mode='HTML')
            return

        db.insert_new_row(cid,wallet,nick,check[1])
        bot.send_message(cid,'✅Отслеживание добавлено', parse_mode='HTML')

    except Exception as e:
        log(e)

#-------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        cid = call.from_user.id
        username = call.from_user.username
        params = call.data.split('-')

        if params[0] == 'show_wallet':
            w_id = params[1]
            bot.send_message(cid,f"<code>{db.get_wallet(w_id)['wallet']}</code>",parse_mode='HTML')
            bot.delete_message(cid,call.message.id)

        elif params[0] == 'delete_wallet':
            w_id = params[1]
            db.stop_lurking(w_id)

            wallets = db.get_all_user_wallets(cid)
            if wallets == []:
                bot.edit_message_text('🤖Список пуст',cid,call.message.id,reply_markup=None)
            else:
                markup = types.InlineKeyboardMarkup()
                for wallet_data in wallets:
                    markup.row(InlineKeyboardButton(f"{wallet_data['nick']}", callback_data=f"show_wallet-{str(wallet_data['id'])}"), InlineKeyboardButton(f"❌", callback_data=f"delete_wallet-{str(wallet_data['id'])}"))
                bot.edit_message_text('🤖Список добавленых кошельков',cid,call.message.id,reply_markup=markup)

    except Exception as e:
        log(e)
#-------------------------
if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            log(e)
            time.sleep(3)
            print('BOT CRASH')
