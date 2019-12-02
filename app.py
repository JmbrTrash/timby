from flask import Flask
from flask import request
import json
import time
import sqlite3
import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler
import telegram
import datetime
import timby_config as timby_config
app = Flask(__name__)
API_TOKEN = timby_config.API_TOKEN
conn = {}
time_limit = 60*5
bot = telegram.Bot(token=API_TOKEN)

@app.route('/report', methods=['GET'])
def hello():
    global conn
    #data = json.loads(request.data)
    seconds = time.time()
    user = request.args.get('user')

    session = getRunningSession(conn, user)
    totaltime = "just now"
    if session is None:
        print("creating new entry")
        startNewSession(conn, user)
    else:

        lasttime=session[1]
        session[1] = seconds
        session[2]=session[2] + (seconds - lasttime) #update totaltime
        totaltime = str(datetime.timedelta(seconds=session[2]))
        project = session[4]
        if project is None:
            chat_id = get_chat_id(user)
            if chat_id is not None:
                bot.send_message(chat_id=chat_id, text="You are working without active project, please set project using /project { projectname }")
            
        updateRunningSession(conn, session)
        
    return "User {} is having an active session since {}".format(user, totaltime)

def startNewSession(dbcon, user, project = None):
    seconds = time.time()
    try:
        c = dbcon.cursor()
        sqlcmd = "INSERT INTO time_entries(user, begintime, lasttime, totaltime, project) VALUES(?,?,?,?,?)"
        c.execute(sqlcmd, (user, seconds, seconds, 0, project))
        dbcon.commit()
    except Exception as e:
        print(e)
    
def updateRunningSession(dbcon, session):
        print("Updateing entry{}".format(session[0]))
        try:
            c = dbcon.cursor()
            sqlcmd = "UPDATE time_entries SET begintime=?, lasttime=?, totaltime=?, user=?, project=? where ID=?"
            c.execute(sqlcmd, ( session[0], session[1], session[2], session[3], session[4], session[5]))
            dbcon.commit()
        except Exception as e:
            print(e)
    
def getRunningSession(dbcon, user):
    try:
        cur = dbcon.cursor()
        limit = time.time() - time_limit
        print("limit {}".format(limit))
        cur.execute("SELECT * FROM time_entries WHERE user=? and lasttime > ? order by lasttime desc", (user,limit))
        tupl = cur.fetchone()
        session_arr = []
        if tupl is None:
            return None
        session_arr.extend(tupl)
        return session_arr
    except Exception as e:
        print("cannot get running session for user {} exception {}".format(user, e))



def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)
        
def init():
    global conn
    database = r"timelogging.db"
 
    sql_create_time_entries = """ CREATE TABLE IF NOT EXISTS time_entries (
                                        begintime integer NOT NULL,
                                        lasttime integer NOT NULL,
                                        totaltime integer NOT NULL,
                                        user text,
                                        project text,
                                        ID INTEGER PRIMARY KEY
                                    ); """

    sql_chat_ids = """ CREATE TABLE IF NOT EXISTS chatids (
                                        user TEXT NOT NULL,
                                        chat_id TEXT NOT NULL
                                    ); """
    # create a database connection


    conn = create_connection(database)
 
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_time_entries)
        create_table(conn, sql_chat_ids)
    else:
        print("Error! cannot create the database connection.")

@app.before_request
def before_request():
    print("BEFORE !!!! ")
    init()

def bot_db():
    database = r"timelogging.db"
    conn2 = create_connection(database)
    return conn2

def start(update, context):
    db_con = bot_db()
    username = update.message.chat.username
    print(username)
    if username is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your name is {}".format(username))
        try:
            c = db_con.cursor()
            sqlcmd = "INSERT INTO chatids(user,chat_id) VALUES(?,?)"
            c.execute(sqlcmd, (username, update.effective_chat.id))
            db_con.commit()
        except Exception as e:
            print(e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You will need a Telegram username!")

def project(update, context):
    username = update.message.chat.username
    args = update.message.text.split()
    if username is not None:
        
        db_con = bot_db()
        session = getRunningSession(db_con, username)
        
        if session is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are not working at the moment")
            return
        if len(args) == 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are currently working on {}".format(session[4]))
            return
        if session[4] == None:
            new_project = update.message.text.split()[1]
            session[4] = new_project
            updateRunningSession(db_con, session)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Project set to {}!".format(new_project))
        else:
            new_project = update.message.text.split()[1]
            startNewSession(db_con, username, new_project)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Started a new session with project set to {}!".format(new_project))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You really need a username dude...")

def session(update, context):
    username = update.message.chat.username
    #args = update.message.text.split()
    if username is not None:
        db_con = bot_db()
        session = getRunningSession(db_con, username)
        if session is None:
             context.bot.send_message(chat_id=update.effective_chat.id, text="You have no active session")
        context.bot.send_message(chat_id=update.effective_chat.id, text="You've been working for {} seconds on project {}".format(str(datetime.timedelta(seconds=session[2])), session[4]))

def get_chat_id(user):
    global conn
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM chatids WHERE user=?", (user,))
    obj = cur.fetchone()
    if obj is None:
        return None
    return obj[0]

if __name__ == '__main__':
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    project_handler = CommandHandler('project', project)
    dispatcher.add_handler(project_handler)
  
    session_handler = CommandHandler('session', session)
    dispatcher.add_handler(session_handler)

    threadBot = threading.Thread(target = updater.start_polling)
    threadBot.start()
    print("thread for bot started, now starting rest api")
    init()
    app.run()

