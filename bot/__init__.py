from flask import Flask
from flask_cors import CORS, cross_origin
from telegram.ext import Updater
from telegram.ext import CommandHandler

from server.api import api
from server.database import database_init
from client.ui import ui

import bot_commands

import threading

from timby_config import API_TOKEN, PORT, HOST

import mimetypes

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

app = Flask(__name__)
app.register_blueprint(api)
app.register_blueprint(ui)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', bot_commands.start)
    dispatcher.add_handler(start_handler)

    project_handler = CommandHandler('project', bot_commands.project)
    dispatcher.add_handler(project_handler)

    project_handler = CommandHandler('p', bot_commands.project)
    dispatcher.add_handler(project_handler)

    session_handler = CommandHandler('session', bot_commands.current_session)
    dispatcher.add_handler(session_handler)

    session_handler = CommandHandler('s', bot_commands.current_session)
    dispatcher.add_handler(session_handler)

    take_break_handler = CommandHandler('break', bot_commands.take_break)
    dispatcher.add_handler(take_break_handler)

    addManual_handler = CommandHandler('manual', bot_commands.addManualSession)
    dispatcher.add_handler(addManual_handler)

    addManual_handler = CommandHandler('m', bot_commands.addManualSession)
    dispatcher.add_handler(addManual_handler)

    projectList_handler = CommandHandler('list', bot_commands.listProjects)
    dispatcher.add_handler(projectList_handler)

    createProject_handler = CommandHandler('createproject', bot_commands.createProject)
    dispatcher.add_handler(createProject_handler)

    list_users_handler = CommandHandler('users', bot_commands.listUsers)
    dispatcher.add_handler(list_users_handler)

    help_handler = CommandHandler('help', bot_commands.showHelp)
    dispatcher.add_handler(help_handler)

    help_handler = CommandHandler('h', bot_commands.showHelp)
    dispatcher.add_handler(help_handler)

    threadBot = threading.Thread(target=updater.start_polling)
    threadBot.start()
    print("thread for bot started, now starting rest server")
    database_init()
    app.run(host=HOST, port=PORT)
