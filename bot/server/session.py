from .database import get_db
from timby_config import TIME_LIMIT
from time import time


def updateRunningSession(session):
    print("Updateing entry {}".format(session[0]))
    try:
        db = get_db()
        c = db.cursor()
        sqlcmd = "UPDATE time_entries SET begintime=%s, lasttime=%s, user=%s, project=%s where ID=%s"
        c.execute(sqlcmd, (session[0], session[1], session[2], session[3], session[4]))
    except Exception as e:
        print(e)


def getRunningSession(user):
    try:
        db = get_db()
        c = db.cursor()
        limit = time() - TIME_LIMIT
        c.execute("SELECT begintime, lasttime, user, project, ID, type FROM time_entries WHERE user=%s and lasttime > %s order by lasttime desc", (user, limit))
        session = c.fetchone()
        session_arr = []
        if session is None:
            return None
        session_arr.extend(session)
        return session_arr
    except Exception as e:
        print("cannot get running session for user {} exception {}".format(user, e))


def startNewSession(user, project=None, sessionType=None):
    seconds = time()
    try:
        db = get_db()
        c = db.cursor()
        sqlcmd = "INSERT INTO time_entries(user, begintime, lasttime, totaltime, project, type) VALUES(%s,%s,%s,%s,%s,%s)"
        c.execute(sqlcmd, (user, seconds, seconds, 0, project, sessionType))

    except Exception as e:
        print(e)


def getAllRunningSessions():
    try:
        db = get_db()
        c = db.cursor()
        limit = time() - TIME_LIMIT
        c.execute("SELECT user FROM time_entries WHERE lasttime > %s GROUP BY user desc", (limit,))
        tupl = c.fetchall()
        active_users = []
        if tupl is None:
            return []
        for entry in tupl:
            active_users.extend(entry)
        return active_users
    except Exception as e:
        print("cannot get running session for users exception {}".format(e))
