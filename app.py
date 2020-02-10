from flask import Flask, send_from_directory
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

import mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

def getdb():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="timby"
    )
    mydb.autocommit = True

    return mydb

app = Flask(__name__)
API_TOKEN = timby_config.API_TOKEN
conn = {}
time_limit = 60*5
bot = telegram.Bot(token=API_TOKEN)

@app.route('/<path:path>')
def ui(path):
    return send_from_directory('ui', path)

@app.route('/report', methods=['GET'])
def hello():

    #data = json.loads(request.data)
    seconds = time.time()
    user = request.args.get('user')

    session = getRunningSession( user)
    totaltime = "just now"
    sessionType = "Unknown"
    print(request.remote_addr)
    if "192.168.2." in str(request.remote_addr):
        sessionType = "Local"
        print("Local session!")
    if '192.168.3.' in str(request.remote_addr):
        sessionType = "VPN"
    if '127.0.0.1' in str(request.remote_addr):
        sessionType = "Dev"

    if session is None:
        print("creating new entry for user {}", user)
        startNewSession( user, None, sessionType)
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

def startNewSession( user, project = None, sessionType=None):
    seconds = time.time()
    try:
        db = getdb()
        c = db.cursor()
        sqlcmd = "INSERT INTO time_entries(user, begintime, lasttime, totaltime, project, type) VALUES(%s,%s,%s,%s,%s,%s)"
        c.execute(sqlcmd, (user, seconds, seconds, 0, project, sessionType))
        
    except Exception as e:
        print(e)
    
def updateRunningSession( session):
        print("Updateing entry {}".format(session[0]))
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
        c.execute("SELECT * FROM time_entries WHERE user=%s and lasttime > %s order by lasttime desc", (user,limit))
        tupl = c.fetchone()
        session_arr = []
        if tupl is None:
            return None
        session_arr.extend(tupl)
        return session_arr
    except Exception as e:
        print("cannot get running session for user {} exception {}".format(user, e))

def getAllRunningSessions():
    try:
        db = getdb()
        c = db.cursor()
        limit = time.time() - time_limit
        c.execute("SELECT user FROM time_entries WHERE lasttime > %s GROUP BY user desc", (limit, ))
        tupl = c.fetchall()
        active_users = []
        if tupl is None:
            return []
        for entry in tupl:
            active_users.extend(entry)
        return active_users
    except Exception as e:
        print("cannot get running session for users exception {}".format(e))


def showHelp(update, context):
    text = """Usage: 
/start [Tell the bot who you are / initiate]
/session [Session overview]
/s
/project {projectname} [Set your project]
/p
/manual {projectname} {time} [Add manual time entry]
/m"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def addManualSession(update, context):
    username = update.message.chat.username
    args = update.message.text.split()

    if len(args) == 3:
        duration = int(args[2]) * 60 #given in minutes, converted to secs
        project = args[1]
        now = time.time()
        beginTime = now - duration
        print("Creating manual entry, {} {}".format(beginTime, duration))
        try:
            db = getdb()
            c = db.cursor()
            sqlcmd = "INSERT INTO time_entries(user, begintime, lasttime, totaltime, project, type) VALUES(%s,%s,%s,%s,%s,%s)"
            c.execute(sqlcmd, (username, beginTime, 0, duration, project, 'Manual'))
            context.bot.send_message(chat_id=update.effective_chat.id, text="A manual entry has been created on project {} with a duration of {} minutes".format(project, int(args[2])))
            return
        except Exception as e:
            print(e)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /manual {project} {time}")
       
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
    
    sql_adjust1 = """ ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS type VARCHAR(255); """

    # create a database connection

    # create tables
    try:
        db = getdb()
        c = db.cursor()
        c.execute(sql_create_time_entries)
        c.execute(sql_chat_ids)
        c.execute(sql_adjust1)

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
            print('booooooo')
            print(session)
            startNewSession( username, new_project, session[6])
            context.bot.send_message(chat_id=update.effective_chat.id, text="Started a new session with project set to {}!".format(new_project))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You really need a username dude...")

def session(update, context):
    username = update.message.chat.username
    #args = update.message.text.split()

    try:
        now = time.time()
        if username is not None:
            session = getRunningSession( username)
            if session is None:
                context.bot.send_message(chat_id=update.effective_chat.id, text="You have no active session")
                return
            
            lasttime = session[1]
            workedTime = session[2] + (now - lasttime) #update totaltime

        
        context.bot.send_message(chat_id=update.effective_chat.id, text="You've been working for {} seconds on project {}".format(str(datetime.timedelta(seconds=workedTime)), session[4]))

    except Exception as e:
        print(e)

def take_break(update, context):
    username = update.message.chat.username
    session = getRunningSession(username)
    args = update.message.text.split()
    if len(args) == 2:
        session[2] = session[2] - (int(args[1])*60) #substract breaktime
        updateRunningSession(session)
        context.bot.send_message(chat_id=update.effective_chat.id, text="A break of {} minutes has been substracted from your worktime".format(args[1]))


def listUsers(update, context):
    #username = update.message.chat.username
    runningSessions = getAllRunningSessions()
    print(runningSessions)
    activeUsersString = '\n'.join(runningSessions)
    print(activeUsersString)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Active users: \n{}".format(activeUsersString))



def get_chat_id(user):
    db = getdb()
    c = db.cursor()
    c.execute("SELECT chat_id FROM chatids WHERE user=%s", (user,))
    obj = c.fetchone()
    if obj is None:
        return None
    return obj[0]

@app.route('/getWeeks/<year>', methods=['GET'])
def getWeeks(year):
    weeks_query = '''SELECT distinct(WEEK(from_unixtime(begintime))) as Week
    FROM time_entries
    where YEAR(from_unixtime(begintime)) = %s
    order by Week desc
    '''
    db = getdb()
    c = db.cursor()
    c.execute(weeks_query, (year, ))
    entries = c.fetchall()
    return json.dumps(entries)

@app.route('/getWeeksPerProject/<project>', methods=['GET'])
def getWeeksPerProject(project):
    weeks_query = '''SELECT distinct(WEEK(from_unixtime(begintime))) as Week, YEAR(from_unixtime(begintime)) as Year
    FROM time_entries
    where project = %s
     order by Year desc, Week desc
    '''
    db = getdb()
    c = db.cursor()
    c.execute(weeks_query, (project, ))
    entries = c.fetchall()
    return json.dumps(entries)

@app.route('/getDataWeek/<week>/<year>', methods=['GET'])
def getDataWeek(week, year):
    dataweeks_query = '''SELECT user as User, sum(totaltime)
    FROM time_entries
    where YEAR(from_unixtime(begintime)) = %s and WEEK(from_unixtime(begintime)) = %s
    group by user
    '''
    db = getdb()
    c = db.cursor()
    c.execute(dataweeks_query, (year, week, ))
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        hours = entry[1] / 3600
        minutes = (entry[1] / 60) % 60
        time = ("%d Hours, %02d Minutes" % (hours, minutes))

        row['user'] = entry[0]
        row['time'] = time
        results.append(row)
        print(entry)
    return json.dumps(results)

@app.route('/getDataWeekPerProject/<project>/<week>/<year>', methods=['GET'])
def getDataWeekPerProject(project, week, year):
    dataweeks_query = '''SELECT user as User, sum(totaltime) as Totaltime
    FROM time_entries
    where YEAR(from_unixtime(begintime)) = %s and WEEK(from_unixtime(begintime)) = %s and project = %s
    group by user
    '''
    db = getdb()
    c = db.cursor()
    c.execute(dataweeks_query, (year, week, project, ))
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        hours = entry[1] / 3600
        minutes = (entry[1] / 60) % 60
        time = ("%d Hours, %02d Minutes" % (hours, minutes))
        print(time)
        row['user'] = entry[0]
        row['time'] = time
        results.append(row)
        print(row)
    return json.dumps(results)

@app.route('/users', methods=['GET'])
def getUsers():
    userquery = 'SELECT DISTINCT(user) FROM chatids'

    db = getdb()
    c = db.cursor()
    c.execute(userquery)
    entries = c.fetchall()
    results = []
    for entry in entries:
        results.append(entry)
    return json.dumps(results)

@app.route('/projects', methods=['GET'])
def getProjects():
    userquery = 'SELECT DISTINCT(project) FROM time_entries'

    db = getdb()
    c = db.cursor()
    c.execute(userquery)
    entries = c.fetchall()
    return json.dumps(entries)



@app.route('/getTypes/<user>/<week>', methods=['GET'])
def getTypes(user, week):
    typesquery = '''SELECT sum(totaltime) as totaal, type from time_entries WHERE USER=%s and  WEEK(from_unixtime(begintime), '%h') = %s group by type;'''
    db = getdb()
    c = db.cursor()
    c.execute(typesquery, (user, week))
    entries = c.fetchall()
    results = {}
    for entry in entries:
        hours = int(entry[0]/3600)
        minutes = (entry[0] /60) % 60
        time=("%d:%02d" % (hours, minutes))
        print(time)
        results[entry[1]]= time
    print(results)
    return json.dumps(results)

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
        row['start'] = str(entry[1])
        row['week'] = entry[2]
        row['totaltime'] = str(entry[3])
        row['project'] = entry[4]
        results.append(row)
    return json.dumps(results)

@app.route('/time_entries_week', methods=['GET'])
def time_entries_by_week():
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(sum(totaltime)) as Duration 
    FROM time_entries 
    GROUP BY user, week;
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, )
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        row['user'] = entry[0]
        row['start'] = str(entry[1])
        row['week'] = entry[2]
        row['totaltime'] = str(entry[3])
        results.append(row)
    return json.dumps(results)

@app.route('/allEntriesWeekUser/<week>/<user>', methods=['GET'])
def allEntriesWeekUser(week, user):
    time_entries_by_week_query = '''SELECT 
    from_unixtime(begintime) as Start, 
    sec_to_time(totaltime) as Duration,
    project as Project, 
    DAYNAME(from_unixtime(begintime)) as Daynamestarted, 
    from_unixtime(lasttime) as Stop, 
    DAYNAME(from_unixtime(lasttime)) as Daynamestopped,
     begintime as id
    FROM time_entries where WEEK(from_unixtime(begintime)) = %s and user=%s;
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (week, user, ))
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        date = str(entry[0]).split(' ', 1)
        datestop = str(entry[4]).split(' ', 1)
        print(date)
        dayname = entry[3]
        print(dayname)
        row['id'] = entry[6]
        row['start'] = entry[3] +' ('+ date[1][:-3] + 'u)'
        row['stopped'] = entry[5] + ' (' + datestop[1][:-3] + 'u)'
        row['totaltime'] = str(entry[1])[:-3] + ' Hours'
        row['project'] = str(entry[2])
        results.append(row)
    return json.dumps(results)


@app.route('/getProjectData/<project>', methods=['GET'])
def getProjectData(project):
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    ROUND(sum(totaltime),4) as Duration, project as Name
    FROM time_entries
    WHERE project=%s
    GROUP BY week, user
    order by week DESC ;
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (project,))
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        hours = entry[3] / 3600
        minutes = (entry[3] / 60) % 60
        time = ("%d,%02d" % (hours, minutes))
        print(time)
        jipla = str(entry[1]).split(' ', 1)

        row['user'] = entry[0]
        row['year'] = jipla[0][0:4]
        row['start'] = jipla[1][:-3] + 'u (' + jipla[0] + ')'
        row['week'] = entry[2]
        row['totaltime'] = str(time)
        results.append(row)
    return json.dumps(results)

@app.route('/getTotalTimesProject/<project>', methods=['GET'])
def getTotalTimesProject(project):
    time_entries_by_week_query = '''SELECT sum(totaltime) as total, user from time_entries where project = %s group by user
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (project,))
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        hours = entry[0] / 3600
        minutes = (entry[0] / 60) % 60
        time = ("%d Hours, %02d Minutes" % (hours, minutes))

        row['user'] = entry[1]
        row['time'] = str(time)
        results.append(row)
    return json.dumps(results)


@app.route('/deleteEntry/<begintime>', methods=['DELETE'])
def deleteEntry(begintime):
    time_entries_by_week_query = '''DELETE FROM time_entries WHERE begintime=%s;
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (begintime,))
    return 'succes!'

@app.route('/time_entries_week_user/<user>', methods=['GET'])
def time_entries_by_week_for_user(user):
    print('hier')
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sum(totaltime)as Duration , YEAR(from_unixtime(begintime)) as Year
     
     
    FROM time_entries
    WHERE USER=%s
    GROUP BY week
    order by Year desc, Week desc;
    ''' 
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (user, ) )
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        hours = entry[3] / 3600
        minutes = (entry[3] / 60) % 60
        time = ("%d Hours, %02d Minutes" % (hours, minutes))

        jipla = str(entry[1]).split(' ', 1 )

        row['user'] = entry[0]
        row['start'] = jipla[1][:-3] + 'u ('+jipla[0]+')'
        row['week'] = entry[2]
        row['totaltime'] = str(time)
        row['year'] = entry[4]
        results.append(row)
    print(results)
    return json.dumps(results)

@app.route('/time_entries_week_user_project/<user>', methods=['GET'])
def time_entries_by_week_for_user_project(user):
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(sum(totaltime)) as Duration, project as Project
    FROM time_entries
    WHERE USER=%s
    GROUP BY week, project;
    ''' 
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (user, ) )
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        row['user'] = entry[0]
        row['start'] = str(entry[1])
        row['week'] = entry[2]
        row['totaltime'] = str(entry[3])
        row['project'] = entry[4]
        results.append(row)
    return json.dumps(results)

if __name__ == '__main__':
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    project_handler = CommandHandler('project', project)
    dispatcher.add_handler(project_handler)
  
    project_handler = CommandHandler('p', project)
    dispatcher.add_handler(project_handler)

    session_handler = CommandHandler('session', session)
    dispatcher.add_handler(session_handler)

    session_handler = CommandHandler('s', session)
    dispatcher.add_handler(session_handler)

    take_breakhandler = CommandHandler('break', take_break)
    dispatcher.add_handler(take_breakhandler)
    

    addManual_handler = CommandHandler('manual', addManualSession)
    dispatcher.add_handler(addManual_handler)

    addManual_handler = CommandHandler('m', addManualSession)
    dispatcher.add_handler(addManual_handler)

    list_usershandler = CommandHandler('users', listUsers)
    dispatcher.add_handler(list_usershandler)

    help_handler = CommandHandler('help', showHelp)
    dispatcher.add_handler(help_handler)

    help_handler = CommandHandler('h', showHelp)
    dispatcher.add_handler(help_handler)
    

    threadBot = threading.Thread(target = updater.start_polling)
    threadBot.start()
    print("thread for bot started, now starting rest api")
    init()
    app.run(host='0.0.0.0')


