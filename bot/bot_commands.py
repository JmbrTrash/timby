from time import time, strftime, gmtime
from server.database import get_db

from server.api import get_project_list
from server.session import startNewSession, getAllRunningSessions, getRunningSession, updateRunningSession


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
        duration = int(args[2]) * 60  # given in minutes, converted to secs
        project = args[1]
        now = time()
        beginTime = now - duration
        try:
            db = get_db()
            c = db.cursor()
            sqlcmd = "INSERT INTO time_entries(user, begintime, lasttime, totaltime, project, type) VALUES(%s,%s,%s,%s,%s,%s)"
            c.execute(sqlcmd, (username, beginTime, 0, duration, project, 'Manual'))
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="A manual entry has been created on project {} with a duration of {} minutes".format(
                                         project, int(args[2])))
            return
        except Exception as e:
            print(e)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /manual {project} {time}")


def current_session(update, context):
    username = update.message.chat.username
    session = getRunningSession(username)

    if session is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No active session!")
    else:
        current_project = session[3]
        begin_time = int(session[0])
        last_time = int(session[1])
        total_seconds = (last_time - begin_time)
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds / 60) % 60)
        total_time = '{} hours and {} minutes'.format(hours, minutes)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Active session on {} for {}".format(current_project, total_time))


def createProject(update, context):
    username = update.message.chat.username
    args = update.message.text.split()
    projectName = args[1]

    if (canManage(username) is False):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You don't have the rights to create a new project")
        return

    if (projectExists(projectName) is True):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Project {} already exists!".format(projectName))
        return

    try:
        db = get_db()
        cursor = db.cursor()
        insertProject = "INSERT INTO projects (name) VALUES(%s)"
        cursor.execute(insertProject, (projectName,))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Created new project: {projectName}")
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to create new project: {projectName}")


def canManage(username):
    try:
        db = get_db()
        cursor = db.cursor()
        get_user_rights = "SELECT canManage from chatids WHERE user=%s"
        cursor.execute(get_user_rights, (username,))
        can_manage = cursor.fetchone()
        return can_manage[0] > 0
    except Exception as e:
        print(e)
        return False


def projectExists(project_name):
    try:
        db = get_db()
        cursor = db.cursor()
        sqlcmd = "SELECT * FROM projects WHERE name = %s"
        cursor.execute(sqlcmd, (project_name,))
        projects = cursor.fetchall()
        return len(projects) > 0
    except Exception as e:
        print(e)
    return False


def listProjects(update, context):
    current_projects = cursorListToString(get_project_list())
    if current_projects is None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No projects found!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Current projects: {}".format(current_projects))


def cursorListToString(item_list):
    return ', '.join(str(item) for cursor_list in item_list for item in cursor_list)


def start(update, context):
    username = update.message.chat.username
    if username is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your name is {}".format(username))
        try:
            db = get_db()
            c = db.cursor()
            sqlcmd = "INSERT INTO chatids (id,user) VALUES(%(id)s,%(user)s) ON DUPLICATE KEY UPDATE user=%(user)s"
            c.execute(sqlcmd, {'id': update.effective_chat.id, 'user': username})

        except Exception as e:
            print(e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You will need a Telegram username!")


def project(update, context):
    print('test')
    username = update.message.chat.username
    args = update.message.text.split()
    if username is not None:

        session = getRunningSession(username)
        project_name = update.message.text.split()[1]

        if session is None:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are not working at the moment")
            return
        if len(args) == 1:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You are currently working on {}".format(session[4]))
            return
        if (projectExists(project_name) is False):
            project_list = cursorListToString(get_project_list())
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=("Project {} does not exist!" + "\n" + "Available projects: {}").format(
                                         project_name, project_list))
            return
        if session[3] == None:
            session[3] = project_name
            updateRunningSession(session)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Project set to {}!".format(project_name))
        else:
            startNewSession(username, project_name, session[6])
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Started a new session with project set to {}!".format(project_name))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You really need a username dude...")


def take_break(update, context):
    username = update.message.chat.username
    session = getRunningSession(username)
    args = update.message.text.split()
    if len(args) == 2:
        session[2] = session[2] - (int(args[1]) * 60)  # substract breaktime
        updateRunningSession(session)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="A break of {} minutes has been substracted from your worktime".format(args[1]))


def listUsers(update, context):
    runningSessions = getAllRunningSessions()
    activeUsersString = '\n'.join(runningSessions)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Active users: \n{}".format(activeUsersString))

