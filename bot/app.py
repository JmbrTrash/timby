from flask import Flask, send_from_directory
from flask import request
import json
import time
from datetime import datetime
from datetime import timedelta

import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler
import telegram
import timby_config as timby_config

import mysql.connector

import mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

app = Flask(__name__)
API_TOKEN = timby_config.API_TOKEN
conn = {}
time_limit = 60*5
bot = telegram.Bot(token=API_TOKEN)

def getdb():
    mydb = mysql.connector.connect(
        host=timby_config.MYSQL_HOST,
        user=timby_config.MYSQL_USER,
        passwd=timby_config.MYSQL_PASSWORD,
        database=timby_config.MYSQL_DATABASE
    )
    mydb.autocommit = True

    return mydb

@app.route('/')
@app.route('/<path:path>')
def renderUi(path = 'index.html'):
    return send_from_directory('../ui', path)

@app.route('/report', methods=['GET'])
def hello():

    #data = json.loads(request.data)
    seconds = time.time()
    user = request.args.get('user')

    session = getRunningSession( user)
    totaltime = "just now"
    sessionType = "Unknown"
    if "192.168.2." in str(request.remote_addr):
        sessionType = "Local"
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
        workedTime = session[2] + (seconds - lasttime) #update totaltime
        if workedTime > 0:
            totaltime = time.strftime("%H hours and %M minutes", time.gmtime(workedTime))
        project = session[4]
        if project is None:
            chat_id = get_chat_id(user)
            if chat_id is not None:
                bot.send_message(chat_id=chat_id, text="You are working without active project, please set project using /project { projectname }")
            
        updateRunningSession(session)
        
    return "User {} is having an active session for {}".format(user, totaltime)

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

def createProject(update, context):
    username = update.message.chat.username
    args = update.message.text.split()
    projectName = args[1]

    if (canManage(username) is False):
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have the rights to create a new project")
        return

    if (projectExists(projectName) is True):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Project {} already exists!".format(projectName))
        return

    try:
        db = getdb()
        cursor = db.cursor()
        insertProject = "INSERT INTO projects (name) VALUES(%s)"
        cursor.execute(insertProject, (projectName,))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Created new project: {projectName}")
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to create new project: {projectName}")
        
def listProjects(update, context):
    currentProjects = convertCursorListToString(getProjectList())
    if currentProjects is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No projects found!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Current projects: {}".format(currentProjects))

def convertCursorListToString(itemList):
    return ', '.join(str(item) for cursorList in itemList for item in cursorList)

def canManage(userName):
    try:
        db = getdb()
        cursor = db.cursor()
        getUserRights = "SELECT canManage from chatids WHERE user=%s"
        cursor.execute(getUserRights, (userName,))
        canManage = cursor.fetchone()
        return canManage[0] > 0
    except Exception as e:
        print(e)
        return False

def getProjectList():
    try:
        db = getdb()
        cursor = db.cursor()
        projectsSQL = "SELECT name FROM projects ORDER BY name ASC"
        cursor.execute(projectsSQL)
        projectList = cursor.fetchall()
        return projectList
    except Exception as e:
        print(e)
        return None

def init():
 
    sql_create_time_entries = """ CREATE TABLE IF NOT EXISTS time_entries (
                                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                        begintime integer NOT NULL,
                                        lasttime integer NOT NULL,
                                        totaltime integer NOT NULL,
                                        user text,
                                        project_id integer NOT NULL
                                    ); """

    sql_chat_ids = """ CREATE TABLE IF NOT EXISTS chatids (
                                        id integer PRIMARY KEY NOT NULL,
                                        user TEXT NOT NULL,
                                        canManage boolean default 0
                                    ); """

    sql_create_projects = """ CREATE TABLE IF NOT EXISTS projects (
                                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                                        name varchar(45) NOT NULL
                                    ); """
    
    sql_adjust1 = """ ALTER TABLE time_entries ADD COLUMN IF NOT EXISTS type VARCHAR(255); """

    adjustCanManage = """ ALTER TABLE chatids ADD COLUMN IF NOT EXISTS canManage boolean default 0; """

    # create a database connection

    # create tables
    try:
        db = getdb()
        c = db.cursor()
        c.execute(sql_create_time_entries)
        c.execute(sql_create_projects)
        c.execute(sql_chat_ids)
        c.execute(sql_adjust1)
        c.execute(adjustCanManage)
    except Exception as e:
        print(e)

@app.before_request
def before_request():
    print("BEFORE !!!! ")
    #init()


def start(update, context):
    username = update.message.chat.username
    if username is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your name is {}".format(username))
        try:
            db = getdb()
            c = db.cursor()
            sqlcmd = "INSERT INTO chatids (id,user) VALUES(%(id)s,%(user)s) ON DUPLICATE KEY UPDATE user=%(user)s"
            c.execute(sqlcmd, { 'id': update.effective_chat.id, 'user': username })
            
        except Exception as e:
            print(e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You will need a Telegram username!")

def project(update, context):
    username = update.message.chat.username
    args = update.message.text.split()
    if username is not None:
        
        session = getRunningSession( username)
        projectName = update.message.text.split()[1]
        
        if session is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are not working at the moment")
            return
        if len(args) == 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are currently working on {}".format(session[4]))
            return
        if (projectExists(projectName) is False):
            projectList = convertCursorListToString(getProjectList())
            context.bot.send_message(chat_id=update.effective_chat.id, text=("Project {} does not exists!" + "\n" + "Available projects: {}").format(projectName, projectList))
            return
        if session[4] == None:
            session[4] = projectName
            updateRunningSession( session)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Project set to {}!".format(projectName))
        else:
            startNewSession( username, projectName, session[6])
            context.bot.send_message(chat_id=update.effective_chat.id, text="Started a new session with project set to {}!".format(projectName))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You really need a username dude...")

def projectExists(projectName):
    try:
        db = getdb()
        cursor = db.cursor()
        sqlcmd = "SELECT * FROM projects WHERE name = %s"
        cursor.execute(sqlcmd, (projectName,))
        projects = cursor.fetchall()
        return len(projects) > 0
    except Exception as e:
        print(e)
    return False

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
            projectName = session[4]
            timeData = time.strftime("%H hours and %M minutes", time.gmtime(workedTime))
            
        context.bot.send_message(chat_id=update.effective_chat.id, text="You've been working for {} on project {}".format(timeData, projectName))

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
    runningSessions = getAllRunningSessions()
    activeUsersString = '\n'.join(runningSessions)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Active users: \n{}".format(activeUsersString))

def get_chat_id(user):
    db = getdb()
    c = db.cursor()
    c.execute("SELECT id FROM chatids WHERE user=%s", (user,))
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
        results.append(convertEntryToTimeData(entry))
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
        results.append(convertEntryToTimeData(entry))
    return json.dumps(results)

def convertEntryToTimeData(entry):
    timeData = {}
    user = entry[0]
    timeDuration = int(entry[1])
    timeData['user'] = user
    timeDict = timeForSeconds(timeDuration)
    timeData['time'] = timeDict
    return timeData

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
    currentProjects = getProjectList()
    return json.dumps(currentProjects)

@app.route('/getTypes/<user>/<week>', methods=['GET'])
def getTypes(user, week):
    typesquery = '''SELECT sum(totaltime) as total, type from time_entries WHERE USER=%s and  WEEK(from_unixtime(begintime), '%h') = %s group by type;'''
    db = getdb()
    c = db.cursor()
    c.execute(typesquery, (user, week))
    entries = c.fetchall()
    results = {}
    for entry in entries:
        hours = int(entry[0]/3600)
        minutes = (entry[0] /60) % 60
        time=("%02d:%02d" % (hours, minutes))
        results[entry[1]]= time
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
    begintime as Start,
    lasttime as Stop,  
    totaltime as Duration,
    DAYNAME(from_unixtime(begintime)) as Daynamestarted, 
    DAYNAME(from_unixtime(lasttime)) as Daynamestopped,
    project,
    id,
    type
    FROM time_entries where WEEK(from_unixtime(begintime)) = %s and user=%s ORDER BY type ASC;
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (week, user, ))
    entries = c.fetchall()
    results = []
    for entry in entries:
        timeData = {}
        startTime = datetime.fromtimestamp(entry[0])
        endTime = datetime.fromtimestamp(entry[1])
        timeDuration = timeForSeconds(int(str(entry[2])))
        startDay = entry[3]
        endDay = entry[4]
        project = entry[5]
        entryId = entry[6]
        entryType = entry[7]
        timeData['id'] = entryId
        timeData['type'] = entryType
        timeData['start'] = convertToTimeDict(startDay, startTime)
        if entryType != 'Manual':
            timeData['stopped'] = convertToTimeDict(endDay, endTime)
        else:
            endTime = startTime
            endTime += timedelta(hours=timeDuration['hours'], minutes=timeDuration['minutes'])
            timeData['stopped'] = convertToTimeDict(endDay, endTime)  
        timeData['totaltime'] = timeDuration
        timeData['project'] = project
        results.append(timeData)
    return json.dumps(results)

def convertToTimeDict(day, time):
    return { 'day': day, 'hours': time.hour, 'minutes': time.minute }


@app.route('/getProjectData/<project>', methods=['GET'])
def getProjectData(project):
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sum(totaltime) as Duration, project as Name
    FROM time_entries
    WHERE project=%s
    GROUP BY week, user
    order by week DESC ;
    '''
    db = getdb() 
    c = db.cursor()
    c.execute(time_entries_by_week_query, (project,))
    entries = c.fetchall()
    timeResults = {}
    totalSeconds = 0
    for entry in entries:
        dateTime = entry[1].timetuple()
        duration = int(entry[3])
        year = dateTime.tm_year
        totalSeconds += duration
        if (year in timeResults):
            currentTimeData = timeResults[year]
            currentTimeData['seconds'] += duration
        else:
            timeResults[year] = { 'seconds': duration }
    timeResults = convertToTime(timeResults)
    timeResults['Total'] = timeForSeconds(totalSeconds)
    return json.dumps(timeResults)

def convertToTime(timerResults):
    timeData = {}
    for year in timerResults:
        times = timerResults[year]
        seconds = times['seconds']
        timeData[year] = timeForSeconds(seconds)
    return timeData

def timeForSeconds(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds / 60) % 60)
    minutes = ("%02d" % (minutes))
    return { 'hours': hours, 'minutes': minutes }

@app.route('/getTotalTimesProject/<project>', methods=['GET'])
def getTotalTimesProject(project):
    time_entries_by_week_query = '''SELECT user, sum(totaltime) as total from time_entries where project = %s group by user
    '''
    db = getdb()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (project,))
    entries = c.fetchall()
    results = []
    for entry in entries:
        results.append(convertEntryToTimeData(entry))
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

    projectList_handler = CommandHandler('list', listProjects)
    dispatcher.add_handler(projectList_handler)

    createProject_handler = CommandHandler('createproject', createProject)
    dispatcher.add_handler(createProject_handler)

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


