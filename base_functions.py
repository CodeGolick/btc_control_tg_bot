import sys
import logging
import requests
from datetime import datetime
from time import sleep
#-------------------------
from telebot import types,util
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#-------------------------
import db
#-------------------------
def init_logs():
    sys.setrecursionlimit(5000)
    logging.basicConfig(filename='logs.log', filemode='w',encoding='utf-8', level=logging.ERROR)
    print('Silent Start')
#-------------------------
def log(e):
    print(e)
    logging.exception(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
#-------------------------
def check_address(address):
    try:
        req = requests.get(f'https://blockchain.info/balance?active={address}').json()
        if 'error' in str(req):
            return [False]
        else:
            return [True,req[address]['final_balance']]
    except Exception as e:
        log(e)
#-------------------------

def checker_loop(bot, upd_time):
    while 1:
        try: 
            wallets = db.get_all_wallets()

            if wallets == []:
                print("нет кошельков")
                continue

            param = ''
            for each_wallet in wallets:
                param += each_wallet + '|'

            req = requests.get(f'https://blockchain.info/balance?active={param}').json()

            for each in req:
                cur_balance = int(req[each]['final_balance'])
                wallet_data = db.get_wallet_by_addr(each)
                last_balance = int(wallet_data['status'])
                wallet_nick = wallet_data['nick']
                cid = wallet_data['tg_chatid']
                time = wallet_data['create_time']

                if cur_balance == last_balance:     #неизменился
                    diffs = datetime.now() - datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                    diffs_in_days = round( diffs.total_seconds()/(60*60*24) )
                    print({'wallet_nick':wallet_nick,'wallet_address':each,'balance':cur_balance,'status':'NOT CHANGE','no_change_days':diffs_in_days})
                    if diffs_in_days == 7:
                        bot.send_message(cid,f'🔴 <b>{wallet_nick}</b> не пополнял свой кошелек уже 7 дней',parse_mode='HTML')
                        db.update_balance(each,cur_balance)

                elif cur_balance < last_balance:    #вывод
                    print({'wallet_nick':wallet_nick,'wallet_address':each,'balance':cur_balance,'status':'WITHDRAW','no_change_days':0})
                    db.update_balance(each,cur_balance)
                elif cur_balance > last_balance:    #пополнение
                    db.update_balance(each,cur_balance)

                    btc_diff = float(int(cur_balance) - int(last_balance))/ 100000000
                    courses = requests.get('https://blockchain.info/ticker').json()
                    inRUB = round(float(courses['RUB']['last']) * btc_diff, 2)

                    print({'wallet_nick':wallet_nick,'wallet_address':each,'balance':cur_balance,'balance_in_rub':inRUB,'status':'TOPUP','no_change_days':0})

                    bot.send_message(cid,f'💰 <b>{wallet_nick}</b> пополнил кошелек\n💎 <code>{each}</code>\n💵 { str(btc_diff) }BTC | ~{inRUB} ₽',parse_mode='HTML')

        except Exception as e:
            log(e)

        finally:
            print('*-----------------------*')
            sleep(upd_time)