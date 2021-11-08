import sqlite3
from base_functions import log
from datetime import datetime

def db_connect():
    try:
        sqlite_conn = sqlite3.connect('database.db')
        return sqlite_conn
    except Exception as e:
        log(e)

def create_tables():
    try:
        sqlite_conn = db_connect()
        sqlite_conn.execute('''CREATE TABLE IF NOT EXISTS lurking(
            ID INTEGER PRIMARY KEY, 
            tg_chatid TEXT,
            wallet TEXT,
            nick TEXT,
            status TEXT,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP);'''
        )
    except Exception as e:
        log(e)

def insert_new_row(tg_chatid,wallet,nick,balance):
    try:
        sqlite_conn = db_connect()
        sqlite_conn.execute("INSERT INTO lurking(tg_chatid,wallet,nick,status) VALUES (?,?,?,?)" , (tg_chatid,wallet,nick,balance) )
        sqlite_conn.commit()
    except Exception as e:
        log(e)

def get_all_user_wallets(tg_chatid):
    try:
        sqlite_conn = db_connect()
        sqlite_cursor = sqlite_conn.execute("SELECT id,tg_chatid,wallet,nick,status,create_time FROM lurking WHERE tg_chatid = ?", (tg_chatid,))
        data = []

        for row in sqlite_cursor:
            push = {}
            push['id'] = row[0]
            push['tg_chatid'] = row[1]
            push['wallet'] = row[2]
            push['nick'] = row[3]
            push['status'] = row[4]
            push['create_time'] = row[5]
            data.append(push)
        return data
    except Exception as e:
        log(e)

def get_all_wallets():
    try:
        sqlite_conn = db_connect()
        sqlite_cursor = sqlite_conn.execute("SELECT wallet FROM lurking")
        data = []

        for row in sqlite_cursor:
            push = row[0]
            data.append(push)

        return data
    except Exception as e:
        log(e)


def get_wallet(wid):
    try:
        sqlite_conn = db_connect()
        sqlite_cursor = sqlite_conn.execute("SELECT id,tg_chatid,wallet,nick,status,create_time FROM lurking WHERE id = ?", (wid,))
        for row in sqlite_cursor:
            data = {}
            data['id'] = row[0]
            data['tg_chatid'] = row[1]
            data['wallet'] = row[2]
            data['nick'] = row[3]
            data['status'] = row[4]
            data['create_time'] = row[5]
            return data
    except Exception as e:
        log(e)

def get_wallet_by_addr(addr):
    try:
        sqlite_conn = db_connect()
        sqlite_cursor = sqlite_conn.execute("SELECT id,tg_chatid,wallet,nick,status,create_time FROM lurking WHERE wallet = ?", (addr,))
        for row in sqlite_cursor:
            data = {}
            data['id'] = row[0]
            data['tg_chatid'] = row[1]
            data['wallet'] = row[2]
            data['nick'] = row[3]
            data['status'] = row[4]
            data['create_time'] = row[5]
            return data
    except Exception as e:
        log(e)

def stop_lurking(row_id):
    try:
        sqlite_conn = db_connect()
        sqlite_conn.execute("DELETE FROM lurking WHERE id = ? ", (row_id,) )
        sqlite_conn.commit()
    except Exception as e:
        log(e)

def update_balance(address,balance):
    try:
        sqlite_conn = db_connect()
        sqlite_conn.execute("UPDATE lurking SET status = ?, create_time = ? WHERE wallet = ? ", (balance,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),address) )
        sqlite_conn.commit()
    except Exception as e:
        log(e)

        # 2021-11-07 17:52:44

