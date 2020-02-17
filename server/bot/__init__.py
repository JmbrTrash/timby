from flask import Flask

import telegram
import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler

from timby_config import API_TOKEN

from bot.start import start
from bot.projects import createProject, listProjects

from api.api import api
from ui.ui import ui

import mimetypes

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

bot = telegram.Bot(token=API_TOKEN)


def create_app():
    app = Flask(__name__)

    app.register_blueprint(api)
    app.register_blueprint(ui)

    return app


if __name__ == '__main__':
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    #project_handler = CommandHandler('project', )
    #dispatcher.add_handler(project_handler)

    #project_handler = CommandHandler('p', project)
    #dispatcher.add_handler(project_handler)

    # session_handler = CommandHandler('session', session)
    # dispatcher.add_handler(session_handler)

    # session_handler = CommandHandler('s', session)
    # dispatcher.add_handler(session_handler)

    # take_breakhandler = CommandHandler('break', take_break)
    # dispatcher.add_handler(take_breakhandler)

    # addManual_handler = CommandHandler('manual', addManualSession)
    # dispatcher.add_handler(addManual_handler)

    # addManual_handler = CommandHandler('m', addManualSession)
    # dispatcher.add_handler(addManual_handler)

    projectList_handler = CommandHandler('list', listProjects)
    dispatcher.add_handler(projectList_handler)

    createProject_handler = CommandHandler('createproject', createProject)
    dispatcher.add_handler(createProject_handler)

    # list_usershandler = CommandHandler('users', listUsers)
    # dispatcher.add_handler(list_usershandler)

    # help_handler = CommandHandler('help', showHelp)
    # dispatcher.add_handler(help_handler)

    # help_handler = CommandHandler('h', showHelp)
    # dispatcher.add_handler(help_handler)

    threadBot = threading.Thread(target=updater.start_polling)
    threadBot.start()
    print("thread for bot started, now starting rest api")
    create_app().run(host='0.0.0.0')
