from flask import Blueprint, request
import json
from time import time
from datetime import datetime
from datetime import timedelta

import telegram
from timby_config import API_TOKEN
from .session import startNewSession, getRunningSession, updateRunningSession

from .database import get_db

api = Blueprint('api', __name__, url_prefix='/api')

conn = {}
bot = telegram.Bot(token=API_TOKEN)


@api.route('/report', methods=['GET'])
def report():
    user = request.args.get('user')
    session = getRunningSession(user)
    session_type = "Unknown"
    chat_id = get_chat_id(user)

    if "192.168.2." in str(request.remote_addr):
        session_type = "Local"
    if '192.168.3.' in str(request.remote_addr):
        session_type = "VPN"
    if '127.0.0.1' in str(request.remote_addr):
        session_type = "Dev"

    if session is None:
        startNewSession(user, None, session_type)
        return "{} just started a new session!".format(user)

    saved_session_type = session[5]
    project = session[3]

    current_time = int(time())
    session[1] = current_time

    saved_time = int(session[0])
    total_seconds = (current_time - saved_time)
    session[2] = total_seconds
    updateRunningSession(session)

    if saved_session_type != session_type:
        startNewSession(user, project, session_type)
        if chat_id is not None:
            bot.send_message(chat_id=chat_id,
                            text="You started a new session, connection changed to {}".format(session_type))
    else:
        if project is None:
            if chat_id is not None:
                bot.send_message(chat_id=chat_id,
                                 text="You are working without active project, please set project using /project { projectname }")

    hours = int(total_seconds / 3600)
    minutes = int((total_seconds / 60) % 60)
    total_time = '{} hours and {} minutes'.format(hours, minutes)

    return "User {} is having an active session on {}, {}".format(user, project, total_time)


def get_project_list():
    try:
        db = get_db()
        cursor = db.cursor()
        projects_sql = "SELECT name FROM projects ORDER BY name ASC"
        cursor.execute(projects_sql)
        project_list = cursor.fetchall()
        return project_list
    except Exception as e:
        print(e)
        return None


def get_chat_id(user):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id FROM chatids WHERE user=%s", (user,))
    obj = c.fetchone()
    if obj is None:
        return None
    return obj[0]


@api.route('/getWeeks/<year>', methods=['GET'])
def getWeeks(year):
    weeks_query = '''SELECT distinct(WEEK(from_unixtime(begintime))) as Week
    FROM time_entries
    where YEAR(from_unixtime(begintime)) = %s
    order by Week desc
    '''
    db = get_db()
    c = db.cursor()
    c.execute(weeks_query, (year,))
    entries = c.fetchall()
    return json.dumps(entries)


@api.route('/getWeeksPerProject/<project>', methods=['GET'])
def getWeeksPerProject(project):
    weeks_query = '''SELECT distinct(WEEK(from_unixtime(begintime))) as Week, YEAR(from_unixtime(begintime)) as Year
    FROM time_entries
    where project = %s
     order by Year desc, Week desc
    '''
    db = get_db()
    c = db.cursor()
    c.execute(weeks_query, (project,))
    entries = c.fetchall()
    return json.dumps(entries)


@api.route('/getDataWeek/<week>/<year>', methods=['GET'])
def getDataWeek(week, year):
    dataweeks_query = '''SELECT user as User, sum(totaltime)
    FROM time_entries
    where YEAR(from_unixtime(begintime)) = %s and WEEK(from_unixtime(begintime)) = %s
    group by user
    '''
    db = get_db()
    c = db.cursor()
    c.execute(dataweeks_query, (year, week,))
    entries = c.fetchall()
    results = []
    for entry in entries:
        results.append(convertEntryToTimeData(entry))
    return json.dumps(results)


@api.route('/getDataWeekPerProject/<project>/<week>/<year>', methods=['GET'])
def getDataWeekPerProject(project, week, year):
    dataweeks_query = '''SELECT user as User, sum(totaltime) as Totaltime
    FROM time_entries
    where YEAR(from_unixtime(begintime)) = %s and WEEK(from_unixtime(begintime)) = %s and project = %s
    group by user
    '''
    db = get_db()
    c = db.cursor()
    c.execute(dataweeks_query, (year, week, project,))
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
    timeData['time'] = timeDuration
    return timeData


@api.route('/users', methods=['GET'])
def getUsers():
    userquery = 'SELECT DISTINCT(user) FROM chatids'

    db = get_db()
    c = db.cursor()
    c.execute(userquery)
    entries = c.fetchall()
    results = []
    for entry in entries:
        results.append(entry)
    return json.dumps(results)


@api.route('/projects', methods=['GET'])
def getProjects():
    currentProjects = get_project_list()
    return json.dumps(currentProjects)


@api.route('/getTypes/<user>/<week>', methods=['GET'])
def getTypes(user, week):
    typesquery = '''SELECT sum(totaltime) as total, type from time_entries WHERE USER=%s and  WEEK(from_unixtime(begintime), '%h') = %s group by type;'''
    db = get_db()
    c = db.cursor()
    c.execute(typesquery, (user, week))
    entries = c.fetchall()
    results = {}
    for entry in entries:
        hours = int(entry[0] / 3600)
        minutes = (entry[0] / 60) % 60
        time = ("%02d:%02d" % (hours, minutes))
        results[entry[1]] = time
    return json.dumps(results)


@api.route('/time_entries', methods=['GET'])
def time_entries():
    time_entries_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(totaltime) as Duration,
    project as Project 
    FROM time_entries;'''

    db = get_db()
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


@api.route('/time_entries_week', methods=['GET'])
def time_entries_by_week():
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(sum(totaltime)) as Duration 
    FROM time_entries 
    GROUP BY user, week;
    '''
    db = get_db()
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


@api.route('/allEntriesWeekUser/<week>/<user>', methods=['GET'])
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
    db = get_db()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (week, user,))
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
        timeData['project'] = 'No project' if project is None else project
        results.append(timeData)
    return json.dumps(results)


def convertToTimeDict(day, time):
    return {'day': day, 'hours': time.hour, 'minutes': time.minute}


@api.route('/getProjectData/<project>', methods=['GET'])
def getProjectData(project):
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sum(totaltime) as Duration, project as Name
    FROM time_entries
    WHERE project=%s
    GROUP BY week, user
    order by week DESC ;
    '''
    db = get_db()
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
            timeResults[year] = {'seconds': duration}
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
    return {'hours': hours, 'minutes': minutes}


@api.route('/getTotalTimesProject/<project>', methods=['GET'])
def getTotalTimesProject(project):
    time_entries_by_week_query = '''SELECT user, sum(totaltime) as total from time_entries where project = %s group by user
    '''
    db = get_db()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (project,))
    entries = c.fetchall()
    results = []
    for entry in entries:
        results.append(convertEntryToTimeData(entry))
    return json.dumps(results)


@api.route('/deleteEntry/<begintime>', methods=['DELETE'])
def deleteEntry(begintime):
    time_entries_by_week_query = '''DELETE FROM time_entries WHERE begintime=%s;
    '''
    db = get_db()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (begintime,))
    return 'succes!'


@api.route('/time_entries_week_user/<user>', methods=['GET'])
def time_entries_by_week_for_user(user):
    time_entries_by_week_query = '''SELECT user as User, WEEK(from_unixtime(begintime)) as Week, 
    sum(totaltime)as Duration , YEAR(from_unixtime(begintime)) as Year
    FROM time_entries
    WHERE USER=%s
    GROUP BY week
    order by Year desc, Week desc;
    '''
    db = get_db()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (user,))
    entries = c.fetchall()
    results = []
    for entry in entries:
        row = {}
        row['user'] = entry[0]
        row['week'] = entry[1]
        row['time'] = int(entry[2])
        row['year'] = entry[3]
        results.append(row)
    return json.dumps(results)


@api.route('/time_entries_week_user_project/<user>', methods=['GET'])
def time_entries_by_week_for_user_project(user):
    time_entries_by_week_query = '''SELECT user as User, from_unixtime(begintime) as Start, WEEK(from_unixtime(begintime)) as Week, 
    sec_to_time(sum(totaltime)) as Duration, project as Project
    FROM time_entries
    WHERE USER=%s
    GROUP BY week, project;
    '''
    db = get_db()
    c = db.cursor()
    c.execute(time_entries_by_week_query, (user,))
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
