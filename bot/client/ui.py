from flask import Blueprint, send_from_directory

ui = Blueprint('ui', __name__)


@ui.route('/')
@ui.route('/<path:path>')
def render(path='index.html'):
    return send_from_directory('../ui', path)
