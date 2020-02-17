from database import getDb


def start(update, context):
    username = update.message.chat.username
    if username is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your name is {}".format(username))
        try:
            db = getDb()
            c = db.cursor()
            query = "INSERT INTO chatids (id,user) VALUES(%(id)s,%(user)s) ON DUPLICATE KEY UPDATE user=%(user)s"
            c.execute(query, {'id': update.effective_chat.id, 'user': username})

        except Exception as e:
            print(e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You will need a Telegram username!")
