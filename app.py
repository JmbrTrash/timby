from flask import Flask
from flask import request
import json
import time

import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler
import telegram
import datetime
import timby_config as timby_config

import mysql.connector


def getdb():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="jimber",
    database="timby"
    )
    mydb.autocommit = True

    return mydb

app = Flask(__name__)
API_TOKEN = timby_config.API_TOKEN
conn = {}
time_limit = 60*5
bot = telegram.Bot(token=API_TOKEN)

@app.route('/report', methods=['GET'])
def hello():

    #data = json.loads(request.data)
    seconds = time.time()
    user = request.args.get('user')

    session = getRunningSession( user)
    totaltime = "just now"
    if session is None:
        print("creating new entry")
        startNewSession( user)
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
            
        updateRunningSession(session)
        
    return "User {} is having an active session since {}".format(user, totaltime)

def startNewSession( user, project = None):
   
    seconds = time.time()
    print(user, seconds, seconds, 0, project)
    try:
        db = getdb()
        c = db.cursor()
        sqlcmd = "INSERT INTO time_entries(user, begintime, lasttime, totaltime, project) VALUES(%s,%s,%s,%s,%s)"
        c.execute(sqlcmd, (user, seconds, seconds, 0, project))
        
    except Exception as e:
        print(e)
    
def updateRunningSession( session):
        print("Updateing entry{}".format(session[0]))
        try:
            db = getdb()
            c = db.cursor()
            sqlcmd = "UPDATE time_entries SET begintime=%s, lasttime=%s, totaltime=%s, user=%s, project=%s where ID=%s"
            c.execute(sqlcmd, ( session[0], session[1], session[2], session[3], session[4], session[5]))
        except Exception as e:
            print(e)
    
def getRunningSession( user):
    try:
        db = getdb()
        c = db.cursor()
        limit = time.time() - time_limit
        print("limit {}".format(limit))
        c.execute("SELECT * FROM time_entries WHERE user=%s and lasttime > %s order by lasttime desc", (user,limit))
        tupl = c.fetchone()
        session_arr = []
        if tupl is None:
            return None
        session_arr.extend(tupl)
        return session_arr
    except Exception as e:
        print("cannot get running session for user {} exception {}".format(user, e))



       
def init():
 
    sql_create_time_entries = """ CREATE TABLE IF NOT EXISTS time_entries (
                                        begintime integer NOT NULL,
                                        lasttime integer NOT NULL,
                                        totaltime integer NOT NULL,
                                        user text,
                                        project text,
                                        ID INTEGER PRIMARY KEY AUTO_INCREMENT
                                    ); """

    sql_chat_ids = """ CREATE TABLE IF NOT EXISTS chatids (
                                        user TEXT NOT NULL,
                                        chat_id TEXT NOT NULL
                                    ); """
    # create a database connection

    # create tables
    try:
        db = getdb()
        c = db.cursor()
        c.execute(sql_create_time_entries)
        c.execute(sql_chat_ids)
    except Exception as e:
        print(e)

@app.before_request
def before_request():
    print("BEFORE !!!! ")
    #init()


def start(update, context):
    username = update.message.chat.username
    print(username)
    if username is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your name is {}".format(username))
        try:
            db = getdb()
            c = db.cursor()
            sqlcmd = "INSERT INTO chatids(user,chat_id) VALUES(%s,%s)"
            c.execute(sqlcmd, (username, update.effective_chat.id))
            
        except Exception as e:
            print(e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You will need a Telegram username!")

def project(update, context):
    username = update.message.chat.username
    args = update.message.text.split()
    if username is not None:
        
        session = getRunningSession( username)
        
        if session is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are not working at the moment")
            return
        if len(args) == 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are currently working on {}".format(session[4]))
            return
        if session[4] == None:
            new_project = update.message.text.split()[1]
            session[4] = new_project
            updateRunningSession( session)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Project set to {}!".format(new_project))
        else:
            new_project = update.message.text.split()[1]
            startNewSession( username, new_project)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Started a new session with project set to {}!".format(new_project))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You really need a username dude...")

def session(update, context):
    username = update.message.chat.username
    #args = update.message.text.split()
    now = time.time()
    if username is not None:
        session = getRunningSession( username)
        if session is None:
             context.bot.send_message(chat_id=update.effective_chat.id, text="You have no active session")
        sessiontime = now - session[0]
        context.bot.send_message(chat_id=update.effective_chat.id, text="You've been working for {} seconds on project {}".format(str(datetime.timedelta(seconds=sessiontime)), session[4]))

def take_break(update, context):
    username = update.message.chat.username
    session = getRunningSession(username)
    args = update.message.text.split()
    
    if len(args) == 1:
        session[2] = session[2] - (args[0]*60) #substract breaktime
        updateRunningSession(session)
        context.bot.send_message(chat_id=update.effective_chat.id, text="A break of {} minutes has been substracted from your worktime".format(args[0]))

def get_chat_id(user):
    db = getdb()
    c = db.cursor()
    c.execute("SELECT chat_id FROM chatids WHERE user=%s", (user,))
    obj = c.fetchone()
    if obj is None:
        return None
    return obj[0]

@app.route('/time_entries', methods=['GET'])
def time_entries():
    time_entries_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(totaltime) as Duration,
    project as Project 
    FROM time_entries;'''

    db = getdb()
    c = db.cursor()
    c.execute(time_entries_query, )
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        row['user'] = entry[0]
        row['start'] = str(entry[1].utcnow())
        row['week'] = entry[2]
        row['totaltime'] = entry[3].total_seconds()
        row['project'] = entry[4]
        results.append(row)
    return json.dumps(results)

@app.route('/time_entries_week', methods=['GET'])
def time_entries_by_week():
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(sum(totaltime)) as Duration 
    FROM time_entries 
    GROUP BY week;
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, )
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        row['user'] = entry[0]
        row['start'] = str(entry[1].utcnow())
        row['week'] = entry[2]
        row['totaltime'] = entry[3].total_seconds()
        results.append(row)
    return json.dumps(results)

@app.route('/time_entries_week_user/<user>', methods=['GET'])
def time_entries_by_week_for_user(user):
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(sum(totaltime)) as Duration 
    FROM time_entries
    WHERE USER=%s
    GROUP BY week;
    ''' 
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (user, ) )
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        row['user'] = entry[0]
        row['start'] = str(entry[1].utcnow())
        row['week'] = entry[2]
        row['totaltime'] = entry[3].total_seconds()
        results.append(row)
    return json.dumps(results)

if __name__ == '__main__':
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    project_handler = CommandHandler('project', project)
    dispatcher.add_handler(project_handler)
  
    session_handler = CommandHandler('session', session)
    dispatcher.add_handler(session_handler)

    take_breakhandler = CommandHandler('break', take_break)
    dispatcher.add_handler(take_breakhandler)
    
    threadBot = threading.Thread(target = updater.start_polling)
    threadBot.start()
    print("thread for bot started, now starting rest api")
    init()
    app.run(host='0.0.0.0')
