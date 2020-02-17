from database import getDb


def createProject(update, context):
    username = update.message.chat.username
    args = update.message.text.split()
    project_name = args[1]

    if canManage(username) is False:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You don't have the rights to create a new project")
        return
    if projectExists(project_name) is True:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Project {} already exists!".format(project_name))
        return
    try:
        db = getDb()
        cursor = db.cursor()
        insert_project = "INSERT INTO projects (name) VALUES(%s)"
        cursor.execute(insert_project, (project_name,))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Created new project: {project_name}")
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to create new project: {project_name}")


def listProjects(update, context):
    current_projects = convertCursorListToString(getProjectList())
    if not current_projects:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No projects found!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Current projects: {}".format(current_projects))


def convertCursorListToString(project_list):
    return ', '.join(str(item) for cursorList in project_list for item in cursorList)


def canManage(username):
    try:
        db = getDb()
        cursor = db.cursor()
        get_user_rights = "SELECT canManage from chatids WHERE user=%s"
        cursor.execute(get_user_rights, (username,))
        has_rights = cursor.fetchone()
        return has_rights[0] > 0
    except Exception as e:
        print(e)
        return False


def getProjectList():
    try:
        db = getDb()
        cursor = db.cursor()
        projects_sql = "SELECT name FROM projects ORDER BY name ASC"
        cursor.execute(projects_sql)
        project_list = cursor.fetchall()
        return project_list
    except Exception as e:
        print(e)
        return None


def projectExists(project_name):
    try:
        db = getDb()
        cursor = db.cursor()
        query = "SELECT * FROM projects WHERE name = %s"
        cursor.execute(query, (project_name,))
        projects = cursor.fetchall()
        return len(projects) > 0
    except Exception as e:
        print(e)
    return False
